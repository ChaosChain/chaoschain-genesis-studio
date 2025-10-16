# Cleanup: Remove Old Storage Directory

## Problem

We have TWO storage directories:
1. `sdk/chaoschain_sdk/storage/` (OLD - deprecated)
2. `sdk/chaoschain_sdk/providers/storage/` (NEW - active)

This is confusing and bloats the codebase.

## Verification

✅ Nothing imports from old `storage/` directory
✅ All code uses `providers/storage/`
✅ Old directory is marked DEPRECATED
✅ Old API (`upload_json`) replaced with new API (`put/get`)

## Action

**DELETE** the old directory entirely:

```bash
rm -rf sdk/chaoschain_sdk/storage/
```

## Impact

- ✅ Cleaner codebase
- ✅ No confusion for contributors
- ✅ Smaller package size
- ✅ No breaking changes (nothing uses it)

## Migration Path (if needed)

If anyone was using the old API:
```python
# OLD (removed)
from chaoschain_sdk.storage import UnifiedStorageManager
storage = UnifiedStorageManager()
storage.upload_json(data, "file.json")

# NEW (correct)
from chaoschain_sdk.providers.storage import LocalIPFSStorage
storage = LocalIPFSStorage()
result = storage.put(json.dumps(data).encode(), mime="application/json")
```

## Ready to Delete?

YES! Execute:
```bash
git rm -rf sdk/chaoschain_sdk/storage/
git commit -m "chore: Remove deprecated storage/ directory - superseded by providers/storage/"
```
