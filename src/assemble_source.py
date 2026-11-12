from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTS = ROOT / "parts"
OUTPUT = ROOT / "ManhDuathoi-Skin-0.16-Cosmetic-Refine.lua"

part_files = sorted(PARTS.glob("source-*.lua.part"))
if len(part_files) != 8:
    raise SystemExit(f"Expected 8 source parts, found {len(part_files)}")

with OUTPUT.open("wb") as out:
    for part in part_files:
        out.write(part.read_bytes())

print(f"Rebuilt: {OUTPUT}")
print(f"Size: {OUTPUT.stat().st_size:,} bytes")
