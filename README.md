# PUBG 0.16 Cosmetic Lab

Unofficial PUBG 0.16 cosmetic modification source archive.

> **Disclaimer:** This is an unofficial, community-maintained project and is not affiliated with, endorsed by, or supported by PUBG or KRAFTON. Use only in environments where modifications are permitted. Compatibility and account-safety are not guaranteed.

## Tài liệu hướng dẫn

- [MODDING_GUIDE.md](MODDING_GUIDE.md) — hướng dẫn phát triển dự án mod Lua: kiến trúc, cấu hình, tổ chức dữ liệu, kiểm thử và quản lý Git.
- [USER_GUIDE.md](USER_GUIDE.md) — hướng dẫn tải repository, khôi phục mã nguồn Lua và đọc cấu hình hiện có.

## Source

The original Lua source is stored in eight sequential parts under `src/parts/` because the GitHub upload interface limits the size of a single write.

### Rebuild the original Lua file

Requirements: Python 3.

From the repository root, run:

```bash
python src/assemble_source.py
```

The script joins the eight parts in filename order and creates:

```
src/ManhDuathoi-Skin-0.16-Cosmetic-Refine.lua
```

Do not reorder, edit, or omit the part files before rebuilding.

## Repository layout

- `src/parts/` — sequential source segments
- `src/assemble_source.py` — rebuild script
- `README.md` — project information and instructions

## Notes

- The source references internal game modules and APIs; it may not work across game versions.
- The repository does not include game assets or proprietary PUBG files.
- No license is declared. All rights remain with their respective owners.
