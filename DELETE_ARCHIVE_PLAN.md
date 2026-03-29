# Delete And Archive Plan

Status:
- Batches 1 through 6 completed locally on 2026-03-30
- Remaining items below are still pending review or execution

## Completed Local Actions

| Path | Final Action | Why |
|---|---|---|
| `LeapWeb/settings.py.bak` | deleted safely | ignored backup file with no references |
| `templates/gallery.html` | deleted safely | zero-byte, unreferenced placeholder |
| `templates/hello.html` | deleted safely | zero-byte, unreferenced placeholder |
| `website/__pycache__/` | deleted safely | runtime bytecode cache only |
| `website/migrations/__pycache__/` | deleted safely | runtime bytecode cache only |
| `boss/` | archived outside repo root | junk directory with no project linkage |
| `backups_20250810_030313/` | archived outside repo root | legacy backup directory |
| `backups_20250810_030511/` | archived outside repo root | legacy backup directory with env/nginx backups |
| `deploy_backups_1754794655/` | archived outside repo root | legacy deploy rollback leftovers |
| `deploy_backups_1754794918/` | archived outside repo root | legacy deploy rollback leftovers |
| `config/` | archived outside repo root | local code-server and shell residue |
| `db.sqlite3` | archived outside repo root | stale sqlite artifact in postgres project |
| `server.log` | archived outside repo root | local runtime artifact retained outside repo |
| `setup_leap_production.sh` | archived outside repo root | legacy setup helper not used by active deploy |
| `templates/announcements.html` | deleted safely | orphaned static stub with no live references |
| `templates/concepts_list.html` | deleted safely | orphaned template referencing missing `study:` namespace |
| `templates/concept_detail.html` | deleted safely | orphaned template referencing missing `study:` namespace |
| `website/templates/about.html` | removed after root replacement | superseded by root `templates/about.html` |
| `website/templates/register.html` | removed after root replacement | superseded by root `templates/register.html` |

## Remaining Local Candidates

| Path | Classification | Why | References | Safe To Remove Now |
|---|---|---|---|---|
| `assets/css/styles.css` | delete candidate | unreferenced tracked asset | none found | only after smoke test |
| `assets/css/styles.min.css` | delete candidate | unreferenced tracked asset | none found | only after smoke test |
| `assets/img/*` unreferenced set | archive or delete candidate | many tracked assets have zero refs | none found | only after visual audit |

## Server Candidates

| Path | Classification | Why | Safe To Remove Now |
|---|---|---|---|
| `/home/myadmin/LEAP/nohup.out` | keep as runtime / rotate later | active gunicorn stdout/stderr file | no |
| `/home/myadmin/LEAP/server.log` | keep as runtime / rotate later | active gunicorn access/error log | no |
| `/home/myadmin/LEAP/gunicorn.sock` | keep as runtime | active socket | no |
| `/home/myadmin/LEAP/.env.before_restore_20260329212847.bak` | archive | useful rollback file after env repair | not yet |
| `/home/myadmin/LEAP/backups_20250810_030313/` | archive | legacy backup | not yet |
| `/home/myadmin/LEAP/backups_20250810_030511/` | archive | legacy backup | not yet |
| `/home/myadmin/LEAP/deploy_backups_1754794655/` | archive | legacy deploy backup | not yet |
| `/home/myadmin/LEAP/deploy_backups_1754794918/` | archive | legacy deploy backup | not yet |
| `/home/myadmin/LEAP/db.sqlite3` | archive | stale sqlite artifact in postgres deployment | not yet |
| `/home/myadmin/LEAP/.git/` | legacy junk | server is not a dev repo | manual cleanup later |
| `/home/myadmin/LEAP/config/` | manual follow-up | contains non-project residue and root-owned subdir | no |
| `/home/myadmin/LEAP/boss/` | delete candidate | no runtime linkage | yes after one more review |
| `/home/myadmin/LEAP/website/templates/` | manual/root-required cleanup | root-owned and blocked from deploy | no |

## Blocked Or Deferred

Do not remove yet:
- `media/`
- `staticfiles/`
- `.env`
- `myenv/`
- any migration `.py` files
- any root-owned file or directory
- any template currently used by a view without first relocating or replacing it

## Recommended First Execution Batches

1. Documentation-only batch: done in this step.
2. Low-risk local cleanup batch:
   completed for `LeapWeb/settings.py.bak`, `templates/gallery.html`, `templates/hello.html`, and local `__pycache__/`.
3. Local archive batch:
   completed for `boss/`, backup directories, `config/`, `db.sqlite3`, `server.log`, and `setup_leap_production.sh`.
4. Template hygiene batch:
   completed for `templates/about.html`, `templates/register.html`, and the duplicate app-level template removals.
5. Static hygiene batch:
   repair missing source assets and broken references before deleting any stale asset files.
