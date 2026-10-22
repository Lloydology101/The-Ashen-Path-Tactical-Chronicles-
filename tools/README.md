# Tactical Chronicles — Stage Compatibility Checks

This is a **read-only structural smoke test** for the first two playable stage archives. It never modifies game files or browser saves.

## Usage

From the repository root (with `stages/` containing the two `.html.gz` files):

```sh
python tools/check_stages.py stages
python tools/check_stages.py stages --json
```

Expected: both stages and `OVERALL: PASS`. Python 3 standard library only.

## What it catches

Missing or corrupt gzip files; missing HTML/script/style structure; changed or missing save keys; missing save/load/reset/render functions; missing browser-storage calls; unexpectedly large loss of embedded artwork; unexpectedly small stage documents; and changes to the known enemy/ally-count load guards.

## What it does NOT prove

It does **not** run the JavaScript, test gameplay, validate save migration, or guarantee that images render. A PASS is necessary but not sufficient for release. The size and asset thresholds are deliberately conservative and will need revision when the game is modularized.

## Safe development workflow

1. Keep GitHub Pages publishing from `main`.
2. Add this script under `tools/check_stages.py` on `develop` only.
3. Run checks on each proposed stage update and manually playtest on a separate testing URL before merging.
4. Merge only after checks and playtests pass.

Note: a public repository makes `develop` files publicly readable. Do not upload the private Development Hub, secret project backups, or personal data.
