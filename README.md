# Vault Migration

Password migration from legacy managers into a self-hosted Vaultwarden instance.

## Imports (2026-03-26)

### Clipperz.is (701 entries)
- Exported as HTML+JSON from clipperz.is
- Converted to Bitwarden JSON format using `clipperz_to_bitwarden.py`
- Imported via `bw import bitwardenjson`
- Some entries with non-standard field names (e.g. Wikipedia's `wpName`) ended up as custom fields rather than username — may need manual cleanup

### Google Chrome (1719 entries)
- Exported as CSV from Chrome's built-in password manager
- Imported directly via `bw import chromecsv` (native format, no conversion needed)

## Post-import cleanup
- Duplicates likely exist between the two imports — use Vaultwarden's Tools > Reports to deduplicate
- All export files were securely shredded (`shred -u`) after import

## Files
- `clipperz_to_bitwarden.py` — Clipperz HTML+JSON to Bitwarden JSON converter
