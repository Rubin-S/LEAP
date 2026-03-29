# Cleanup Execution Log

## Batch 1 - Low-Risk Local Junk Removal

Date:
- 2026-03-30

Scope:
- Local repo only: `D:\projects\LEAP\LEAP`
- No server changes
- No deploy changes

Planned items:
- `LeapWeb/settings.py.bak`
- `templates/gallery.html`
- `templates/hello.html`
- `website/__pycache__/`
- `website/migrations/__pycache__/`

Why this batch was safe:
- `LeapWeb/settings.py.bak` was an ignored backup file with no references.
- `templates/gallery.html` was zero-byte and had no template, view, URL, or include references.
- `templates/hello.html` was zero-byte and had no template, view, URL, or include references.
- Both `__pycache__/` directories contained only Python bytecode caches.

Executed actions:
- Deleted `LeapWeb/settings.py.bak`
- Deleted `templates/gallery.html`
- Deleted `templates/hello.html`
- Removed `website/__pycache__/`
- Removed `website/migrations/__pycache__/`

Validation:
- Ran `.\.venv\Scripts\python.exe manage.py check`
- Result: passed with 3 pre-existing allauth deprecation warnings only
- Confirmed both `__pycache__/` directories were removed
- Confirmed `LeapWeb/settings.py.bak` was removed
- Inspected `git status --short`

Git-visible outcome:
- Deleted tracked file: `templates/gallery.html`
- Deleted tracked file: `templates/hello.html`
- Untracked docs present: `CLEANUP_INVENTORY.md`, `RENAME_PLAN.md`, `DELETE_ARCHIVE_PLAN.md`, `CLEANUP_EXECUTION_LOG.md`

Notes:
- `server.log` was intentionally not removed in this batch to stay aligned with the rule against deleting logs before explicit archive/review.
- No application code, deploy workflow, or server runtime path changed in this batch.

## Batch 2 - Archive Legacy Backup Directories

Date:
- 2026-03-30

Scope:
- Local repo only
- Moved outside repo root to `D:\projects\LEAP\_cleanup_archive\LEAP\2026-03-30_batch2`

Executed actions:
- Archived `boss/`
- Archived `backups_20250810_030313/`
- Archived `backups_20250810_030511/`
- Archived `deploy_backups_1754794655/`
- Archived `deploy_backups_1754794918/`

Validation:
- Ran `.\.venv\Scripts\python.exe manage.py check`
- Result: passed with the same 3 pre-existing allauth deprecation warnings
- Confirmed the repo root no longer contained those directories

## Batch 3 - Archive Root-Level Local Residue

Date:
- 2026-03-30

Scope:
- Local repo only
- Moved outside repo root to `D:\projects\LEAP\_cleanup_archive\LEAP\2026-03-30_batch3`

Executed actions:
- Archived `config/`
- Archived `db.sqlite3`
- Archived `server.log`
- Archived `setup_leap_production.sh`

Validation:
- Ran `.\.venv\Scripts\python.exe manage.py check`
- Result: passed with the same 3 pre-existing allauth deprecation warnings
- Confirmed the repo root no longer contained those items

## Batch 4 - Root Template Placement

Date:
- 2026-03-30

Executed actions:
- Replaced zero-byte `templates/about.html` with working content
- Added `templates/register.html`

Why this batch was safe:
- `website.views.about` renders `about.html`
- `website.views.register` renders `register.html`
- Django template resolution now prefers the root template directory for both names

Validation:
- Ran `.\.venv\Scripts\python.exe manage.py check`
- Verified template origins:
  - `about.html -> D:\projects\LEAP\LEAP\templates\about.html`
  - `register.html -> D:\projects\LEAP\LEAP\templates\register.html`

## Batch 5 - Remove Duplicate App-Level Templates

Date:
- 2026-03-30

Executed actions:
- Deleted `website/templates/about.html`
- Deleted `website/templates/register.html`

Why this batch was safe:
- Root replacements had already been created and validated
- The server deploy excludes `website/templates/`, so future deploys rely on the root replacements

Validation:
- Ran `.\.venv\Scripts\python.exe manage.py check`
- Re-verified template origins stayed on the root `templates/` directory

## Batch 6 - Remove Dead Tracked Templates

Date:
- 2026-03-30

Executed actions:
- Deleted `templates/announcements.html`
- Deleted `templates/concepts_list.html`
- Deleted `templates/concept_detail.html`

Why this batch was safe:
- No live render or URL references were found
- The concept templates referenced a missing `study:` namespace and were already dead

Validation:
- Ran `.\.venv\Scripts\python.exe manage.py check`
- Re-ran a reference scan and found no remaining code references to those template names
