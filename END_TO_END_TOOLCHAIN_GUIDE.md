# End-to-End PUBG Cosmetic Toolchain Guide

> **Scope:** This is a development roadmap for authorized offline/test environments or an officially supported modding interface. It does not cover attaching to the live PUBG process, memory reading/writing, code injection, anti-cheat bypass, protected traffic interception, or unauthorized in-game overlays. PUBG/KRAFTON may prohibit modifications. Use only data and interfaces you are permitted to inspect and modify.

This guide separates three projects:
1. SDK analysis and metadata export.
2. Skin ID Dumper: scan an approved source and build a searchable catalog.
3. Cosmetic Mod: consume that catalog in a test harness through a documented adapter.

The existing 0.16 Lua source references internal game modules. That does not prove a public SDK, safe runtime hook, or supported in-game UI API exists. Verify every dependency; do not invent offsets, class names, function addresses, or undocumented APIs.

---

# 0. Confirm the permitted data source

Before coding, identify the source the dumper is allowed to read:

- Official SDK or metadata export supplied for mod development.
- Developer/test build you own or are explicitly authorized to inspect.
- Local JSON, CSV, XML, or other exported catalog files.
- Documented plugin API that explicitly permits cosmetic metadata access.

If there is no documented plugin API, the first dumper must be a desktop/offline tool that imports approved exports. An in-game panel can only be added when an official or explicitly authorized plugin interface supports UI creation and data access.

Create docs/DATA_SOURCE.md and record:

| Field | Record |
|---|---|
| Source | SDK, test build, export, or plugin |
| Permission | Owner and permitted use |
| Version | SDK/build/catalog version |
| Format | JSON, CSV, XML, generated metadata |
| Access | Documented API or file import |
| Restrictions | What must not be read, changed, or redistributed |

Do not proceed until the source and permission are clear.

# Part I — SDK analysis and metadata export

## 1. Prepare the environment

Recommended Windows setup:
- Windows 10/11
- Git
- Visual Studio Code
- Python 3.11+
- Lua 5.4 interpreter for standalone Lua examples
- Official SDK tools, if supplied by the SDK owner
- Separate test-data folder; never experiment on a live account

Create this structure:

~~~text
pubg-cosmetic-lab/
├── docs/
├── sdk/
│   ├── input/          # authorized exports; do not commit restricted files
│   └── reports/
├── dumper/
├── catalog/
├── mod/
├── tests/
└── README.md
~~~

Initialize Git:

~~~bash
git init
git branch -M main
~~~

Add a .gitignore:

~~~gitignore
.venv/
__pycache__/
*.log
sdk/input/
*.pak
*.ucas
*.utoc
*.uasset
*.umap
.env
~~~

Only include extensions that match the actual SDK package. Never commit proprietary or restricted files.

## 2. Understand SDK metadata

An SDK export may describe classes, structs, enums, properties, functions, asset names, and identifiers. The exact contents depend on the SDK. Start with documentation and generated metadata; do not assume names or offsets from another version.

For every discovered type, record:
- Fully qualified type name
- Parent/base type, if documented
- Properties and declared types
- Enum names and values
- Function signatures, if documented
- SDK/build version
- Whether it is relevant to cosmetics

Do not invent memory offsets, object pointers, function addresses, or undocumented calling conventions. They are not stable API contracts.

## 3. Normalize the inventory

Create sdk/inventory.schema.json. This illustrative sample does not claim to describe PUBG's real SDK:

~~~json
{
  "schema_version": 1,
  "source": {
    "name": "authorized-sdk-export",
    "version": "REPLACE_WITH_REAL_VERSION"
  },
  "types": [
    {
      "name": "Example.CosmeticRecord",
      "kind": "class",
      "properties": [
        { "name": "Id", "type": "integer" },
        { "name": "DisplayName", "type": "string" }
      ]
    }
  ]
}
~~~

## 4. Build an export parser

For the first iteration, support JSON and CSV exports. Keep parsing separate from the UI:

- sdk/parser.py — reads permitted export files.
- sdk/normalize.py — maps source fields to a stable schema.
- sdk/validate.py — checks required fields and types.
- sdk/report.py — writes a readable inventory report.

Fail closed: unknown formats, malformed files, and missing required fields must produce clear errors rather than guessed data.

### SDK phase acceptance checklist

- [ ] Data source and permission documented.
- [ ] SDK/build version recorded.
- [ ] Parser reads a small sample export.
- [ ] Unknown fields are preserved or reported.
- [ ] Invalid input produces useful errors.
- [ ] No live-process access or undocumented offsets are required.
- [ ] Inventory report can be regenerated deterministically.

---

# Part II — Build the Skin ID Dumper

## 5. Define the dumper's responsibilities

The dumper turns an approved metadata source into a normalized catalog. It must not change the game or unlock items.

Expected features:
- Select an approved export folder/file.
- Scan supported files.
- Show progress and current file.
- Pause/cancel long scans.
- Display discovered records in a table.
- Search by ID or name.
- Filter by category, weapon, vehicle, or source version when available.
- Detect duplicate IDs and malformed records.
- Export JSON, CSV, and TXT.
- Save a scan report with source version and timestamp.

### About the requested in-game button

A panel appearing inside PUBG requires an official or explicitly authorized plugin/modding API that provides UI creation and data access. This repository does not document such an API. Build the first version as a desktop GUI. A UI adapter can be added later for a permitted test runtime without rewriting the scanner.

## 6. Recommended architecture

~~~text
dumper/
├── app.py
├── ui/
│   ├── main_window.py
│   └── progress_view.py
├── sources/
│   ├── base.py
│   ├── json_source.py
│   └── csv_source.py
├── scanner/
│   ├── scan_service.py
│   ├── normalize.py
│   └── validate.py
├── exporters/
│   ├── json_exporter.py
│   ├── csv_exporter.py
│   └── txt_exporter.py
└── models/
    └── cosmetic.py
~~~

Keep layers independent:
1. Source reader opens approved files.
2. Scanner extracts candidate records.
3. Normalizer converts records to a common schema.
4. Validator checks data quality.
5. UI displays status and results.
6. Exporter writes files.

This lets you replace a JSON source with another permitted source without rewriting the interface.

## 7. Define a stable cosmetic record

Use a schema like this:

~~~json
{
  "schema_version": 1,
  "source_version": "example-export-1",
  "generated_at": "2026-01-01T00:00:00Z",
  "items": [
    {
      "id": "REPLACE_WITH_VERIFIED_ID",
      "name": "Example item",
      "category": "weapon_skin",
      "weapon": "REPLACE_WITH_VERIFIED_WEAPON",
      "rarity": null,
      "source": "authorized-json-export"
    }
  ]
}
~~~

These values are examples/placeholders, not real PUBG IDs. Keep IDs as strings so leading zeroes or non-numeric identifiers are not lost.

Suggested categories, only when supported by the source:
- weapon_skin
- character_outfit
- helmet
- backpack
- vehicle_skin
- melee
- other

## 8. Implement the scan pipeline

1. User selects an export file/folder.
2. Validate that the path is readable and inside the selected input area.
3. Enumerate supported file extensions only.
4. Parse each file with size and error limits.
5. Normalize candidate records.
6. Validate required fields.
7. Deduplicate by category, ID, and source version.
8. Record rejected rows and reasons.
9. Show the result table.
10. Export only after user confirmation.

Never silently discard duplicates. Show duplicate records and their source locations.

## 9. Design the GUI

Suggested layout:

~~~text
┌─────────────────────────────────────────────────────────────┐
│ Cosmetic ID Dumper                                          │
├─────────────────────────────────────────────────────────────┤
│ Source: [Select export folder...] [Load]                    │
│ [Start scan] [Cancel] [Export JSON] [Export CSV] [Export TXT]│
│ Progress:  [====================          ] 65%              │
│ Search: [____________________] Category: [All v]             │
├────────────┬───────────────────┬──────────────┬──────────────┤
│ ID         │ Name              │ Category     │ Source       │
├────────────┼───────────────────┼──────────────┼──────────────┤
│ ...        │ ...               │ ...          │ ...          │
└────────────┴───────────────────┴──────────────┴──────────────┘
│ Found: N | Duplicates: N | Invalid: N                        │
└─────────────────────────────────────────────────────────────┘
~~~

Use PySide6 or another maintained desktop GUI toolkit. Run scanning in a worker thread so the window remains responsive. Cancel must stop the worker cleanly. Do not report success until parsing, validation, and export have completed.

## 10. Export formats

JSON is the canonical format because it preserves metadata. CSV is useful for spreadsheets. TXT is one ID per line.

Where possible, every export should include:
- Schema version
- Source/build version
- Generation timestamp
- Total records
- Duplicate count
- Invalid-record count
- Export tool version

Example CSV header:

~~~csv
id,name,category,weapon,source_version
~~~

## 11. Dumper test plan

Create synthetic fixtures; do not use guessed real PUBG IDs. Test:
- Valid record
- Missing ID
- Empty name
- Duplicate ID
- Unknown category
- Malformed JSON
- Very large input
- Unicode names
- Interrupted scan
- Export/import round-trip

### Dumper phase acceptance checklist

- [ ] GUI loads approved JSON/CSV data.
- [ ] Scan progress is visible.
- [ ] Cancel works.
- [ ] Search and category filters work.
- [ ] Duplicate and invalid rows are reported.
- [ ] JSON/CSV/TXT exports are valid.
- [ ] Exported JSON can be loaded again.
- [ ] No protected process or anti-cheat interaction is involved.

---

# Part III — Build the cosmetic catalog

## 12. Separate raw and curated data

~~~text
catalog/
├── raw/                  # generated exports; normally gitignored
├── curated/
│   ├── weapons.json
│   ├── outfits.json
│   ├── vehicles.json
│   └── other.json
├── schemas/
│   └── cosmetic.schema.json
└── reports/
~~~

The raw dump is evidence of what the source contained. The curated catalog is the cleaned dataset used by the mod. Never edit the raw dump in place.

## 13. Validate and version the catalog

For every release, store:
- Game/test-build version
- Source SDK/export version
- Catalog schema version
- Dumper version
- Generation date
- Record count by category
- Duplicate and invalid counts
- Hash/checksum of the exported file

When a new source version arrives, generate a diff showing added IDs, removed IDs, renamed entries, category changes, and conflicts. Do not assume an ID has the same meaning across every game version.

---

# Part IV — Build the cosmetic mod

## 14. Separate catalog data from mod logic

~~~text
mod/
├── main.lua
├── config.lua
├── adapters/
│   └── supported_runtime.lua
├── catalog/
│   ├── weapons.lua
│   └── vehicles.lua
├── presets/
├── ui/
├── tests/
└── README.md
~~~

The adapter is the only layer that talks to a runtime. It must use a documented, permitted API. If no supported runtime exists, run the mod logic in a local simulator and do not connect it to the retail game.

## 15. Define configuration

Example configuration for a local test harness:

~~~lua
return {
    enabled_on_start = false,
    open_menu_on_start = false,
    persist_selection = false,
    default_selection = {},
    catalog_schema_version = 1
}
~~~

Keep defaults conservative. A mod should start disabled in a test harness until the user enables it.

## 16. Build selection and presets

Implement independently:
1. Load catalog.
2. Validate catalog schema.
3. Display available categories.
4. Search by name or ID.
5. Select an item.
6. Save selection as a preset.
7. Load/delete a preset.
8. Reset to defaults.
9. Export/import user presets.

A preset should reference catalog IDs, not duplicate full records. If an ID is missing in a newer catalog, show a warning and skip that selection safely.

## 17. Define a runtime adapter contract

Do not invent PUBG function names. Define an interface for your own local simulator:

~~~lua
local Adapter = {}

function Adapter:get_capabilities()
    return {
        catalog_read = true,
        cosmetic_preview = false,
        apply_cosmetic = false
    }
end

function Adapter:preview(item)
    return false, "Preview is not supported by this test adapter"
end

return Adapter
~~~

This is a placeholder for your own test harness, not a PUBG API. A real adapter may only be written against a documented SDK/plugin contract and within its permitted scope.

## 18. Test without a live game

Build a simulator with fake characters, weapons, and cosmetic slots. Verify:
- Catalog loads.
- Invalid catalog is rejected.
- Search and selection work.
- Presets save and reload.
- Missing IDs are handled.
- Unsupported adapter capabilities are disabled in the UI.
- No data is written outside the project/test directory.

### Mod phase acceptance checklist

- [ ] Catalog schema is validated.
- [ ] UI is independent of runtime.
- [ ] Presets use stable IDs.
- [ ] Missing IDs produce warnings.
- [ ] Test adapter has no live-game access.
- [ ] Runtime integration is documented and explicitly permitted before implementation.

---

# Part V — Release and maintenance

## 19. Version components separately

Use separate versions for:
- SDK inventory format: schema_version
- Dumper: semantic version such as 1.0.0
- Catalog: source/build-specific version
- Mod: semantic version plus compatible catalog schema

Do not call a catalog "latest" unless its source version and generation date are recorded.

## 20. Release checklist

- [ ] Remove private/restricted SDK files.
- [ ] Include source attribution and permissions.
- [ ] Include sample synthetic data.
- [ ] Include install and build instructions.
- [ ] Include known limitations.
- [ ] Run tests from a clean checkout.
- [ ] Generate checksums for release artifacts.
- [ ] State that the project is unofficial and not affiliated with PUBG/KRAFTON.

## 21. What is needed to make this PUBG-specific

The current repository contains a Lua source archive that references internal game modules, but it does not document a supported PUBG SDK export format, authorized runtime plugin API, or verified in-game UI extension contract.

To turn this roadmap into a precise version-specific implementation, add:
1. SDK/export format you are authorized to use.
2. Exact source files or code excerpts implementing the existing 0.1–0.16 dump UI and scanner.
3. Documented plugin/runtime API permitting UI and metadata access.
4. A small sample export with sensitive or proprietary content removed.

Without these, PUBG-specific offsets, class names, function names, live scanning methods, or in-game button implementation would be guesswork.

## Recommended build order

| Milestone | Result |
|---|---|
| M1 — SDK inventory | Parsed, versioned metadata report |
| M2 — Dumper core | Scanner, validation, exporters |
| M3 — Dumper GUI | Searchable table, progress, cancel |
| M4 — Catalog | Clean, versioned cosmetic database |
| M5 — Mod core | Config, selection, presets |
| M6 — Test UI | Working local simulator |
| M7 — Supported adapter | Only after an authorized API contract is supplied |
| M8 — Release | Reproducible package and documentation |

**Golden rule:** prove each layer with tests before connecting it to the next one. The dumper should work without the mod, and the mod's catalog and preset logic should work without PUBG running.
