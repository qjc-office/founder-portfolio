#!/usr/bin/env python3
"""PIPA Article 36-37 right-to-deletion implementation.

Deletes:
  - The consent record (.consent.json)
  - Generated AI portraits (any directory under the skill dir matching
    'generated/' or passed via --generated-dir)
  - Optionally: rendered PDFs in a user-specified output dir

Does NOT delete:
  - profile.yaml (user-authored content; user removes manually)
  - Source photos in assets/photos/ unless --include-source is passed
  - Cached input photos on OpenAI's servers — user must submit DSAR at
    https://privacy.openai.com or dsar@openai.com (≤30 days OpenAI retention)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CONSENT_FILE = SKILL_DIR / ".consent.json"
DEFAULT_GENERATED_DIRS = [
    SKILL_DIR / "assets" / "photos" / "generated",
    Path.cwd() / "generated",
]


def remove_path(p: Path, label: str) -> int:
    """Remove a file or dir. Return 1 if something removed, 0 otherwise."""
    if not p.exists():
        return 0
    if p.is_dir():
        shutil.rmtree(p, ignore_errors=True)
    else:
        p.unlink()
    print(f"  ✓ removed {label}: {p}")
    return 1


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument(
        "--generated-dir",
        type=Path,
        action="append",
        help="Additional directory containing generated portraits "
        "(can be repeated; defaults include skill/assets/photos/generated/ "
        "and cwd/generated/)",
    )
    p.add_argument(
        "--include-source",
        action="store_true",
        help="Also delete user-uploaded source photos in assets/photos/ "
        "(only files added by the user — bundled defaults p1-p7 are kept)",
    )
    p.add_argument(
        "--include-pdfs",
        type=Path,
        help="Also delete generated PDF files in this directory "
        "(only those matching *_swiss-*.pdf)",
    )
    p.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )
    args = p.parse_args(argv)

    targets_generated = list(DEFAULT_GENERATED_DIRS)
    if args.generated_dir:
        targets_generated.extend(args.generated_dir)

    print("[forget-me] Will remove the following:")
    print(f"  • consent record: {CONSENT_FILE}")
    print("  • generated portrait dirs:")
    for d in targets_generated:
        print(f"      {d}{' (exists)' if d.exists() else ' (does not exist, skipped)'}")
    if args.include_source:
        print("  • user-uploaded source photos in assets/photos/ (excluding bundled defaults)")
    if args.include_pdfs:
        print(f"  • generated PDFs matching *_swiss-*.pdf in {args.include_pdfs}")

    if not args.yes:
        try:
            response = input("\n진행하시겠습니까? [y/N]: ").strip().lower()
        except KeyboardInterrupt:
            print("\n중단됨.")
            return 1
        if response not in ("y", "yes"):
            print("중단됨.")
            return 1

    print()
    removed = 0
    removed += remove_path(CONSENT_FILE, "consent record")

    for d in targets_generated:
        removed += remove_path(d, "generated dir")

    if args.include_source:
        BUNDLED = {f"p{i}_" for i in range(1, 8)}  # p1_vogue, p2_gq_charcoal, etc.
        photos_dir = SKILL_DIR / "assets" / "photos"
        if photos_dir.exists():
            for photo in photos_dir.iterdir():
                if photo.is_file() and not any(photo.name.startswith(b) for b in BUNDLED):
                    removed += remove_path(photo, "user source photo")

    if args.include_pdfs and args.include_pdfs.exists():
        for pdf in args.include_pdfs.glob("*_swiss-*.pdf"):
            removed += remove_path(pdf, "generated PDF")

    print(f"\n[forget-me] {removed} item(s) removed.")
    print(
        "Reminder: OpenAI 서버에 남은 입력 사본은 본 명령으로 삭제할 수 없습니다.\n"
        "          삭제 요청: https://privacy.openai.com 또는 dsar@openai.com\n"
        "          (OpenAI default 보관 기간: 최대 30일, 학습 미사용)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
