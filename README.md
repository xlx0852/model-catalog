# model-catalog

Shared, versioned model metadata for [sub2api](https://github.com/Wei-Shaw/sub2api).

This repository contains public model metadata only. Do not add API keys, account data,
private upstream URLs, tenant pricing, or routing secrets.

## Published files

- `catalog.json`: latest validated catalog
- `catalog.sha256`: SHA-256 checksum for `catalog.json`
- `schema.json`: JSON Schema for editor and CI validation
- `versions/<version>/`: immutable release snapshots

Consumers should download `catalog.json`, verify `catalog.sha256`, validate the document,
and retain their last known-good or embedded catalog if an update fails.

## Updating the catalog

1. Edit `catalog.json` and increment its integer `version`.
2. Set `updated_at` to the publication time in UTC.
3. Run `python3 scripts/validate_catalog.py --write-checksum`.
4. Copy the validated files into `versions/<version>/` for a release.
5. Open a pull request. CI must pass before merging.

The validation script rejects empty platform maps, duplicate or empty model IDs, invalid
aliases/defaults, negative prices, and cyclic fallback-pricing aliases.
