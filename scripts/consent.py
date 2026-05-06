#!/usr/bin/env python3
"""PIPA Article 28-8 consent management for founder-portfolio.

Records / verifies / revokes user consent for sending face photos to OpenAI
(US-hosted, gpt-image-2 model) for AI portrait generation. Required by Korean
PIPA when the data subject sends biometric data overseas.

User explicitly chose OpenAI over fal.ai (2026-05-06 directive). See privacy.md
v2.0 §7 for the self-use gray-zone disclosure.

Subcommands:
    grant        — read privacy.md aloud, capture consent → .consent.json
    verify       — exit 0 if valid consent exists, 2 otherwise (used by gates)
    show         — print consent record + status
    revoke       — delete consent record (does NOT delete cached photos;
                   for that, run forget_me.py)

Design choices:
- Consent is per-version. If privacy.md hash changes, consent expires.
- Consent record stays on the user's machine only — never transmitted.
- Non-interactive mode: --acknowledge flag for automation / Claude usage.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PRIVACY_DOC = SKILL_DIR / "privacy.md"
CONSENT_FILE = SKILL_DIR / ".consent.json"

CONSENT_VERSION = "2.0"  # bump when privacy.md is materially revised. v2.0 = OpenAI recipient (was v1.0 fal.ai)
RETENTION_DAYS = 3 * 365  # PIPA 제29조 기록 보관 요건


def hash_privacy_doc() -> str:
    if not PRIVACY_DOC.exists():
        return ""
    return hashlib.sha256(PRIVACY_DOC.read_bytes()).hexdigest()[:16]


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


# ─────────────────────────── Subcommands ────────────────────────────


def cmd_grant(args: argparse.Namespace) -> int:
    if not PRIVACY_DOC.exists():
        print(f"[consent] ERROR: privacy.md missing at {PRIVACY_DOC}", file=sys.stderr)
        return 2

    # Show the policy unless suppressed.
    if not args.acknowledge:
        print(PRIVACY_DOC.read_text(encoding="utf-8"))
        print()
        print("=" * 70)
        try:
            response = input(
                "위 내용에 동의하시면 [enter]를 눌러 진행하세요. "
                "거부 시 Ctrl-C로 중단하세요: "
            )
        except KeyboardInterrupt:
            print("\n[consent] 동의가 거부되었습니다.")
            return 1
        # Anything other than empty is also accepted (some terminals send '\r').
        del response

    record = {
        "version": CONSENT_VERSION,
        "privacy_doc_hash": hash_privacy_doc(),
        "granted_at": now_iso(),
        "expires_after_days": RETENTION_DAYS,
        "host": platform.node() or "unknown",
        "platform": platform.platform(),
        "method": "non-interactive" if args.acknowledge else "interactive",
    }
    CONSENT_FILE.write_text(
        json.dumps(record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.chmod(CONSENT_FILE, 0o600)
    print(f"✓ 동의 기록됨: {CONSENT_FILE}")
    print(f"  version={record['version']}, hash={record['privacy_doc_hash']}")
    print(f"  granted_at={record['granted_at']}")
    print(f"  Revoke with: python {Path(__file__).name} revoke")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Return 0 if consent is valid, 2 if missing/invalid/expired.

    Validity rules:
      1. .consent.json exists and parses
      2. version matches CONSENT_VERSION (bumps invalidate old consent)
      3. privacy_doc_hash matches current privacy.md (revisions invalidate)
      4. granted_at is within RETENTION_DAYS of now
    """
    if not CONSENT_FILE.exists():
        if args.verbose:
            print("[consent] no consent record. Run: consent.py grant", file=sys.stderr)
        return 2

    try:
        record = json.loads(CONSENT_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[consent] consent file corrupted: {e}", file=sys.stderr)
        return 2

    if record.get("version") != CONSENT_VERSION:
        if args.verbose:
            print(
                f"[consent] version mismatch (file={record.get('version')}, "
                f"required={CONSENT_VERSION}). Re-grant required.",
                file=sys.stderr,
            )
        return 2

    current_hash = hash_privacy_doc()
    if record.get("privacy_doc_hash") != current_hash:
        if args.verbose:
            print(
                "[consent] privacy.md was modified since consent was recorded. "
                "Re-grant required.",
                file=sys.stderr,
            )
        return 2

    try:
        granted_at = dt.datetime.fromisoformat(record["granted_at"])
        if granted_at.tzinfo is None:
            granted_at = granted_at.replace(tzinfo=dt.timezone.utc)
    except (KeyError, ValueError):
        return 2

    age_days = (dt.datetime.now(dt.timezone.utc) - granted_at).days
    if age_days > record.get("expires_after_days", RETENTION_DAYS):
        if args.verbose:
            print(f"[consent] consent expired ({age_days}d old).", file=sys.stderr)
        return 2

    if args.verbose:
        print(f"✓ valid consent: {record['version']}, granted {age_days}d ago")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    del args
    if not CONSENT_FILE.exists():
        print("(no consent record)")
        return 1
    print(CONSENT_FILE.read_text(encoding="utf-8"))
    return 0


def cmd_revoke(args: argparse.Namespace) -> int:
    del args
    if CONSENT_FILE.exists():
        CONSENT_FILE.unlink()
        print(f"✓ 동의 기록 삭제: {CONSENT_FILE}")
        print("  주의: OpenAI 서버에 캐시된 입력 사진(최대 30일 보관)은 https://privacy.openai.com")
        print("        또는 dsar@openai.com 으로 직접 삭제 요청하세요.")
        print("  로컬 사진/생성물 일괄 삭제: python scripts/forget_me.py")
    else:
        print("(이미 동의 기록이 없습니다)")
    return 0


# ─────────────────────────── Main ───────────────────────────────────


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("grant", help="Record consent (interactive by default)")
    g.add_argument(
        "--acknowledge",
        action="store_true",
        help="Skip the interactive prompt (e.g., for automation). "
        "Use only when you have already read privacy.md.",
    )

    v = sub.add_parser("verify", help="Check if valid consent exists (exit 0/2)")
    v.add_argument("--verbose", action="store_true")

    sub.add_parser("show", help="Print the current consent record")
    sub.add_parser("revoke", help="Delete the consent record")

    args = p.parse_args(argv)

    handlers = {
        "grant": cmd_grant,
        "verify": cmd_verify,
        "show": cmd_show,
        "revoke": cmd_revoke,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
