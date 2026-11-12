# Release v0.16

## Contents
- PUBG 0.16 cosmetic source archive, split into eight ordered Lua segments.
- Python script to reconstruct the original Lua file.
- README documentation and usage notes.

## Rebuild
Run from the repository root:

```bash
python src/assemble_source.py
```

## Verification
The eight uploaded source segments were downloaded from GitHub and concatenated. The reconstructed content matched the original source byte-for-byte (5,067,004 characters as read by the file connector).

## Important
Unofficial community project. Not affiliated with PUBG or KRAFTON. Compatibility and account safety are not guaranteed. Use only where modifications are permitted.
