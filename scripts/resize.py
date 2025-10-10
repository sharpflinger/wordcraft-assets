#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from PIL import Image

TARGET_SIZE = 240
IMAGES_DIR = Path(__file__).resolve().parent.parent / "word-images"

def get_images():
    exts = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp")
    return [p for p in IMAGES_DIR.rglob("*") if p.suffix.lower() in exts]

def resize_image(img_path: Path, safe: bool, backup_dir: Path):
    try:
        if safe:
            backup_dir.mkdir(exist_ok=True)
            backup_path = backup_dir / img_path.name
            if not backup_path.exists():
                backup_path.write_bytes(img_path.read_bytes())  # копируем оригинал

        with Image.open(img_path) as img:
            w, h = img.size
            if w <= TARGET_SIZE and h <= TARGET_SIZE:
                return "skip"

            img.thumbnail((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
            # сохраняем с оптимизацией и качеством
            save_kwargs = {}
            if img_path.suffix.lower() in [".jpg", ".jpeg"]:
                save_kwargs = {"quality": 85, "optimize": True}
            elif img_path.suffix.lower() == ".png":
                save_kwargs = {"optimize": True}
            img.save(img_path, **save_kwargs)
            return "resized"
    except Exception as e:
        print(f"❌ Failed to process {img_path}: {e}")
        return "error"

def main():
    parser = argparse.ArgumentParser(description="Resize images exceeding target size.")
    parser.add_argument("--check", "-c", action="store_true", help="Only report images that exceed target size.")
    parser.add_argument("--write", "-w", action="store_true", help="Resize images exceeding target size.")
    parser.add_argument("--safe", "-s", action="store_true", help="Backup original before resizing.")
    args = parser.parse_args()

    if args.safe and not args.write:
        parser.error("--safe can only be used with --write")

    images = get_images()
    if not images:
        print("No images found.")
        return

    need_count = 0
    resized = 0
    skipped = 0

    backup_dir = IMAGES_DIR / "backup" if args.safe else None

    for img_path in images:
        try:
            with Image.open(img_path) as img:
                w, h = img.size
            if w > TARGET_SIZE or h > TARGET_SIZE:
                need_count += 1
                if args.write:
                    result = resize_image(img_path, args.safe, backup_dir)
                    if result == "resized":
                        resized += 1
                    elif result == "error":
                        pass
                continue
            skipped += 1
        except Exception as e:
            print(f"Error reading {img_path}: {e}")

    if args.check:
        print(f"{need_count} image(s) exceed {TARGET_SIZE}px.")
    else:
        print(f"{resized} image(s) resized.")
        print(f"{skipped} image(s) already within {TARGET_SIZE}px bounds.")
        if args.safe:
            print("Backups saved with _full suffix.")

if __name__ == "__main__":
    main()
