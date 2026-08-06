#!/usr/bin/env python3
"""
Sinh manifest.json cho một bản phát hành FSales.

VÌ SAO CÓ FILE NÀY
------------------
Trước đây manifest gõ tay ⇒ dễ sai `version`, quên `sha256`, hoặc dán
nhầm hash của bản khác. Script này đọc thẳng file .exe nên không sai được.

DÙNG
----
    python tao-manifest.py 3.0.22 --notes "Nội dung thay đổi"

    # nếu vẫn muốn dùng Google Drive:
    python tao-manifest.py 3.0.22 --drive-id 1AbC... --notes "..."

Ghi ra 2 chỗ:
    updates/<version>/manifest.json   (lưu trữ)
    updates/latest/manifest.json      ← app ĐỌC FILE NÀY

CÁCH PHÁT HÀNH ĐANG DÙNG (chốt 6/8/2026): **GitHub Releases**
Không đẩy file .exe vào git nữa — repo đã phình 1,5 GB vì 16 bộ cài cũ.
  1. Tạo release tag v<version> trên GitHub
  2. Đính kèm Fsales-Setup-EXE-<version>.exe vào release đó
  3. Chạy script này rồi commit 2 file manifest.json (nhẹ, vài KB)
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = "TungFireSmart/Fsales_update"
GOC = Path(__file__).resolve().parent


def sha256_va_size(f: Path):
    h = hashlib.sha256()
    n = 0
    with open(f, 'rb') as fh:
        while True:
            khoi = fh.read(1024 * 1024)
            if not khoi:
                break
            h.update(khoi)
            n += len(khoi)
    return h.hexdigest(), n


def main():
    p = argparse.ArgumentParser()
    p.add_argument("version")
    p.add_argument("--notes", default="")
    p.add_argument("--drive-id", default=None,
                   help="File id trên Google Drive; bỏ trống thì dùng GitHub raw")
    a = p.parse_args()

    v = a.version
    exe = GOC / "updates" / v / f"Fsales-Setup-EXE-{v}.exe"
    if not exe.exists():
        sys.exit(f"❌ Không thấy bộ cài: {exe}")

    sha, size = sha256_va_size(exe)

    if a.drive_id:
        url = (f"https://drive.usercontent.google.com/download"
               f"?id={a.drive_id}&export=download&confirm=t")
    else:
        # GitHub Releases — cách đang dùng. Không làm phình repo như
        # raw.githubusercontent (vốn đòi file .exe phải nằm trong git).
        url = (f"https://github.com/{REPO}/releases/download"
               f"/v{v}/{exe.name}")

    manifest = {
        "version": v,
        "installer_url": url,
        "notes": a.notes,
        "sha256": sha,
        "size": size,
    }

    for dich in (GOC / "updates" / v / "manifest.json",
                 GOC / "updates" / "latest" / "manifest.json"):
        dich.parent.mkdir(parents=True, exist_ok=True)
        with open(dich, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print(f"✅ {dich}")

    # file .sha256 theo đúng nếp cũ của repo
    sha_file = exe.with_suffix(exe.suffix + ".sha256")
    sha_file.write_text(f"{sha}  {exe.name}\n", encoding="utf-8")
    print(f"✅ {sha_file}")

    print(f"\n   version : {v}")
    print(f"   size    : {size:,} byte")
    print(f"   sha256  : {sha}")
    print(f"   url     : {url}")
    print("\n⚠️  Mở URL trên bằng trình duyệt ẩn danh để chắc chắn nó tải về "
          "FILE .EXE THẬT,\n   chứ không phải một trang HTML.")


if __name__ == "__main__":
    main()
