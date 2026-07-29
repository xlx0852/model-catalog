#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog.json"
CHECKSUM = ROOT / "catalog.sha256"


def fail(message: str) -> None:
    raise SystemExit(f"catalog validation failed: {message}")


def validate(data: dict) -> None:
    version = data.get("version")
    if not isinstance(version, int) or version < 1:
        fail("version must be a positive integer")
    platforms = data.get("platforms")
    if not isinstance(platforms, dict) or not platforms:
        fail("platforms must be a non-empty object")

    for platform, config in platforms.items():
        if not isinstance(config, dict):
            fail(f"platform {platform!r} must be an object")
        models = config.get("models", [])
        if not isinstance(models, list):
            fail(f"platform {platform!r} models must be an array")
        ids = []
        for model in models:
            model_id = model.get("id") if isinstance(model, dict) else None
            if not isinstance(model_id, str) or not model_id.strip():
                fail(f"platform {platform!r} contains a model without an id")
            ids.append(model_id.strip())
        duplicates = sorted({model_id for model_id in ids if ids.count(model_id) > 1})
        if duplicates:
            fail(f"platform {platform!r} has duplicate model ids: {duplicates}")

        known = set(ids)
        known.update(config.get("default_mapping", {}).keys())
        for alias, target in config.get("aliases", {}).items():
            if not alias.strip() or not target.strip():
                fail(f"platform {platform!r} contains an empty alias")
            if target not in known:
                fail(f"platform {platform!r} alias {alias!r} targets unknown model {target!r}")

    pricing = data.get("fallback_pricing")
    if not isinstance(pricing, dict):
        fail("fallback_pricing must be an object")
    for name, entry in pricing.items():
        if not isinstance(entry, dict):
            fail(f"fallback price {name!r} must be an object")
        for key, value in entry.items():
            if "cost" in key or "price" in key:
                if isinstance(value, (int, float)) and value < 0:
                    fail(f"fallback price {name!r}.{key} cannot be negative")
        seen = {name}
        target = entry.get("alias_of")
        while target:
            if target in seen:
                fail(f"fallback pricing alias cycle includes {target!r}")
            seen.add(target)
            target_entry = pricing.get(target)
            if not isinstance(target_entry, dict):
                fail(f"fallback price {name!r} aliases unknown entry {target!r}")
            target = target_entry.get("alias_of")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-checksum", action="store_true")
    args = parser.parse_args()
    raw = CATALOG.read_bytes()
    data = json.loads(raw)
    validate(data)
    digest = hashlib.sha256(raw).hexdigest()
    if args.write_checksum:
        CHECKSUM.write_text(f"{digest}  catalog.json\n", encoding="utf-8")
    elif CHECKSUM.exists() and CHECKSUM.read_text(encoding="utf-8").split()[0] != digest:
        fail("catalog.sha256 does not match catalog.json")
    print(f"catalog v{data['version']} valid: sha256={digest}")


if __name__ == "__main__":
    main()
