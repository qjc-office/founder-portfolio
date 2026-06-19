#!/usr/bin/env python3
"""Generate stylized founder portraits via OpenAI gpt-image-2 (image-to-image).

Pipeline:
1. Read source photo from --source.
2. For each preset, call OpenAI Images Edit API (model=gpt-image-2)
   with the source image + preset prompt.
3. Decode base64 PNG (or fetch returned URL) and save to --out-dir.

Required env:
    OPENAI_API_KEY — issued by user at https://platform.openai.com/api-keys

PIPA / GDPR posture (privacy.md v2.0):
- Source image: uploaded as multipart/form-data to OpenAI Images API.
- OpenAI default policy: API input data retained ≤30 days for abuse monitoring,
  not used for training (since 2023-03-01).
- User explicitly chose OpenAI gpt-image-2 over fal.ai (2026-05-06 directive),
  acknowledging the policy gray zone for self-uploaded portraits as a
  matter of personal responsibility under PIPA Article 22-2 explicit consent.
"""

from __future__ import annotations

import argparse
import base64
import os
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

PRESETS: dict[str, str] = {
    "editorial": (
        "Transform this portrait into a Hasselblad H5D editorial magazine cover style: "
        "soft window light, charcoal blazer, calm gaze, minimal background, 85mm f/1.4. "
        "Preserve the subject's facial features exactly."
    ),
    "corporate": (
        "Transform this portrait into a polished corporate headshot: studio softbox lighting, "
        "navy business suit, clean neutral background, confident slight smile, "
        "head-and-shoulders, 50mm f/2.8. Preserve the subject's facial features exactly."
    ),
    "cinematic": (
        "Transform this portrait into a cinematic founder portrait: dramatic side light, "
        "contemplative pose, 35mm film grain, shallow depth of field, anamorphic. "
        "Preserve the subject's facial features exactly."
    ),
    "monochrome": (
        "Transform this portrait into a fine art black and white photograph: "
        "high contrast lighting, deep shadows, professional editorial monochrome aesthetic. "
        "Preserve the subject's facial features exactly."
    ),
    "warm": (
        "Transform this portrait into a golden hour outdoor portrait: warm tones, natural light, "
        "candid founder moment, soft bokeh. Preserve the subject's facial features exactly."
    ),
}

DEFAULT_MODEL = "gpt-image-2"
DEFAULT_SIZE = "1024x1024"
# Per QJC default policy (rules/image-generation.md, 2026-05-02):
# medium ≈ $0.04/image. Use --quality high only for print/signage/premium contexts.
DEFAULT_QUALITY = "medium"

RATE_BY_QUALITY = {"low": 0.011, "medium": 0.042, "high": 0.167}


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--source", type=Path, required=True, help="Source photo path")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path.cwd() / "generated",
        help="Output directory (default: ./generated/)",
    )
    p.add_argument(
        "--presets",
        default="all",
        help="Comma-separated list of presets, or 'all'. "
        f"Available: {', '.join(PRESETS)}",
    )
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenAI model (default {DEFAULT_MODEL})")
    p.add_argument("--size", default=DEFAULT_SIZE, help=f"Output size (default {DEFAULT_SIZE})")
    p.add_argument(
        "--quality",
        default=DEFAULT_QUALITY,
        choices=["low", "medium", "high"],
        help=f"Render quality (default {DEFAULT_QUALITY}; "
        "high reserved for print/signage per QJC policy)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan, don't call OpenAI (safe to run without OPENAI_API_KEY)",
    )
    p.add_argument(
        "--consent-acknowledge",
        action="store_true",
        help="Bypass consent gate (assumes user has read privacy.md v2.0). "
        "Use only in non-interactive/automation contexts.",
    )
    return p.parse_args(argv)


def check_consent(non_interactive: bool) -> int:
    """Return 0 if consent OK; 2 if missing/expired (caller should abort).

    Skipped on --dry-run (no data leaves the machine) and on
    --consent-acknowledge (caller has explicitly acknowledged).
    """
    if non_interactive:
        return 0
    consent_script = SCRIPT_DIR / "consent.py"
    proc = subprocess.run(
        [sys.executable, str(consent_script), "verify", "--verbose"],
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return 0
    print("[generate] PIPA 제28조의8 동의가 필요합니다 (얼굴 사진 국외 이전).", file=sys.stderr)
    if proc.stderr.strip():
        print(f"  사유: {proc.stderr.strip()}", file=sys.stderr)
    print(f"  약관 열람: {SKILL_DIR / 'privacy.md'}", file=sys.stderr)
    print(f"  동의 기록: python {consent_script} grant", file=sys.stderr)
    print(f"  자동화용:  --consent-acknowledge 플래그 추가 (이미 동의했다고 가정)", file=sys.stderr)
    return 2


def extract_image_bytes(data_item) -> bytes:
    """OpenAI Images API returns either b64_json or a CDN url. Handle both."""
    payload = getattr(data_item, "b64_json", None)
    if payload:
        return base64.b64decode(payload)
    url = getattr(data_item, "url", None)
    if url:
        with urlopen(url, timeout=30) as r:
            return r.read()
    raise RuntimeError("response data has neither b64_json nor url")


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if not args.source.exists():
        print(f"[generate] ERROR: source not found: {args.source}", file=sys.stderr)
        return 2

    if args.presets == "all":
        presets = list(PRESETS)
    else:
        presets = [p.strip() for p in args.presets.split(",") if p.strip()]
        unknown = [p for p in presets if p not in PRESETS]
        if unknown:
            print(
                f"[generate] ERROR: unknown presets: {unknown}. "
                f"Available: {', '.join(PRESETS)}",
                file=sys.stderr,
            )
            return 2

    print(f"[generate] source={args.source} ({args.source.stat().st_size // 1024} KB)")
    print(f"[generate] out_dir={args.out_dir}")
    print(f"[generate] presets={presets}")
    print(f"[generate] model={args.model} size={args.size} quality={args.quality}")

    if args.dry_run:
        print("\n=== DRY RUN — would issue these requests ===")
        for name in presets:
            print(f"  • {name}: {PRESETS[name][:80]}…")
        rate = RATE_BY_QUALITY.get(args.quality, 0.042)
        cost = len(presets) * rate
        print(
            f"\nEstimated cost: {len(presets)} × ${rate:.3f} = ${cost:.2f} "
            f"(OpenAI {args.model} {args.quality}, {args.size})"
        )
        return 0

    consent_status = check_consent(non_interactive=args.consent_acknowledge)
    if consent_status != 0:
        return consent_status

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[generate] ERROR: OPENAI_API_KEY env var not set.", file=sys.stderr)
        print("  Get one at https://platform.openai.com/api-keys", file=sys.stderr)
        print("  export OPENAI_API_KEY=sk-...  # or add to ~/.claude/.env.secrets", file=sys.stderr)
        return 2

    try:
        from openai import OpenAI
    except ImportError:
        print(
            "[generate] ERROR: openai package not installed. "
            "Run scripts/bootstrap.sh to (re)install dependencies.",
            file=sys.stderr,
        )
        return 2

    client = OpenAI(api_key=api_key)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    successes: list[Path] = []
    failures: list[tuple[str, str]] = []

    for name in presets:
        prompt = PRESETS[name]
        print(f"[generate] preset={name} → openai/{args.model}")
        try:
            with open(args.source, "rb") as image_fh:
                # gpt-image-2 supports image-to-image via the edits endpoint.
                # mask is optional (covers full image when omitted).
                result = client.images.edit(
                    model=args.model,
                    image=image_fh,
                    prompt=prompt,
                    size=args.size,
                    quality=args.quality,
                    n=1,
                )
            if not result.data:
                failures.append((name, f"empty data array: {result}"))
                print(f"  ✗ empty data array", file=sys.stderr)
                continue
            bytes_ = extract_image_bytes(result.data[0])
            dest = args.out_dir / f"{name}.png"
            dest.write_bytes(bytes_)
            print(f"  ✓ {dest} ({len(bytes_) // 1024} KB)")
            successes.append(dest)
        except Exception as e:
            failures.append((name, str(e)))
            print(f"  ✗ failed: {e}", file=sys.stderr)
            continue

    print(f"\n[generate] {len(successes)} succeeded, {len(failures)} failed.")
    if failures:
        for fname, msg in failures:
            print(f"  ✗ {fname}: {msg[:160]}", file=sys.stderr)

    return 0 if successes else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
