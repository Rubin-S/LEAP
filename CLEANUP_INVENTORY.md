# Cleanup Inventory

Snapshot date: 2026-03-30 (local) / 2026-03-29 UTC (server)

Scope:
- Local source repo: `D:\projects\LEAP\LEAP`
- Deployed server copy: `/home/myadmin/LEAP`

Status:
- Read-only inspection completed
- Inventory reflects the pre-cleanup snapshot
- Local cleanup batches 1 through 6 completed on 2026-03-30
- See `CLEANUP_EXECUTION_LOG.md` for the executed batch history
- Deployment currently healthy

## Local Tree

Top-level tree:

```text
LEAP/
  .github/
    workflows/
  .venv/
  assets/
    bootstrap/
    css/
    fonts/
    img/
      illustrations/
    js/
  backups_20250810_030313/
  backups_20250810_030511/
  boss/
  config/
  deploy_backups_1754794655/
  deploy_backups_1754794918/
  LeapWeb/
  media/
  staticfiles/
  templates/
    accounts/
    errors/
  website/
    migrations/
    templates/
  .env
  .env.example
  .gitignore
  db.sqlite3
  deploy_leap.sh
  manage.py
  requirements.txt
  server.log
  setup_leap_production.sh
```

Tracked source tree:
- `.github/workflows/ci.yml`
- `.github/workflows/deploy.yml`
- `LeapWeb/`
- `website/`
- `templates/`
- `assets/`
- `manage.py`
- `requirements.txt`
- `deploy_leap.sh`
- `.env.example`
- `.gitignore`

Ignored or untracked local clutter:
- `.venv/`
- `LeapWeb/settings.py.bak`
- `backups_20250810_030313/`
- `backups_20250810_030511/`
- `deploy_backups_1754794655/`
- `deploy_backups_1754794918/`
- `boss/`
- `config/`
- `db.sqlite3`
- `media/`
- `staticfiles/`
- `server.log`
- `setup_leap_production.sh`
- `__pycache__/` trees

## Server Tree

Top-level tree:

```text
/home/myadmin/LEAP/
  .env
  .env.before_restore_20260329212847.bak
  .env.example
  .git/
  .gitignore
  LeapWeb/
  assets/
  backups_20250810_030313/
  backups_20250810_030511/
  boss/
  config/
  db.sqlite3
  deploy_backups_1754794655/
  deploy_backups_1754794918/
  deploy_leap.sh
  gunicorn.sock
  manage.py
  media/
  myenv/
  nohup.out
  requirements.txt
  server.log
  staticfiles/
  templates/
  website/
    templates/   root-owned
```

Server-only runtime or deployment baggage:
- `.git/`
- `.env.before_restore_20260329212847.bak`
- `myenv/`
- `gunicorn.sock`
- `nohup.out`

Server ownership issues:
- `/home/myadmin/LEAP/website/templates` is `root:root`
- `/home/myadmin/LEAP/website/templates/about.html` is `root:root`
- `/home/myadmin/LEAP/website/templates/register.html` is `root:root`
- `/home/myadmin/LEAP/config/project` is `root:root`

Current runtime verification:
- Gunicorn running from `/home/myadmin/LEAP/myenv`
- `gunicorn.sock` exists
- `curl --unix-socket /home/myadmin/LEAP/gunicorn.sock http://localhost/` returned `301`
- `curl -I -L http://leapnitpy.org/` returned `200 OK`

## Deploy Excludes

Current deploy workflow excludes:
- `.git/`
- `.github/`
- `.venv/`
- `myenv/`
- `__pycache__/`
- `*.pyc`
- `.env`
- `*.sqlite3`
- `*.log`
- `backups_*`
- `deploy_backups_*`
- `staticfiles/`
- `media/`
- `boss/`
- `config/`
- `server.log`
- `nohup.out`
- `gunicorn.sock`
- `leapnitpy.org`
- `ngrok`
- `ngrok*`
- `setup_leap_production.sh`
- `website/templates/`

Implication:
- `website/templates/` is tracked locally but does not deploy
- server runtime depends on the root `templates/` directory, not the app template folder

## High-Risk Findings

1. `templates/about.html` is a tracked zero-byte file and is actively referenced by `website.views.about`.
2. `website/templates/about.html` is a non-empty legacy fallback, but it is shadowed locally and blocked on the server by `root:root`.
3. `website/templates/register.html` is still the live template source for `views.register`, but it is inside a deploy-excluded and root-owned folder.
4. `templates/gallery.html` and `templates/hello.html` are zero-byte files with no references.
5. `templates/announcements.html`, `templates/concepts_list.html`, and `templates/concept_detail.html` appear orphaned; the concept templates reference a non-existent `study:` URL namespace.
6. `templates/dashboard.html` references `img/firess.png`, but that file exists only in `staticfiles/img`, not in `assets/img`.
7. `templates/study.html` and `templates/video.html` reference `img/leap-preview.jpg`, but that file does not exist in the repo or on the server.
8. `templates/base.html` references `bootstrap/js/bootstrap.bundle.min.js`, but only `bootstrap.min.js` exists in source and staticfiles.
9. `website/views.py` contains duplicated imports and two different `submit_test` definitions; the later definition overrides the earlier one.
10. Both local and server copies still contain large backup trees, stale logs, sqlite artifacts, and pycache output.

## Suspicious Inventory And Classification

| Path | Exists | Classification | Why | References | Safe Next Step |
|---|---|---|---|---|---|
| `backups_20250810_030313/` | local, server | archive | legacy backup directory with nginx backup only | none in code or workflow | archive first, then remove from project root later |
| `backups_20250810_030511/` | local, server | archive | legacy backup directory with `.env.bak` files | none in code or workflow | archive first, keep off repo root |
| `deploy_backups_1754794655/` | local, server | archive | deployment rollback leftovers | none in code or workflow | archive first |
| `deploy_backups_1754794918/` | local, server | archive | deployment rollback leftovers | none in code or workflow | archive first |
| `boss/` | local, server | delete safely | contains only `h.txt`; no app/runtime linkage | none | low-risk removal candidate |
| `config/` | local, server | local-only junk / manual follow-up | code-server and shell-home residue, not project code | none in app, excluded from deploy | local: remove from repo root later; server: manual cleanup only |
| `LeapWeb/settings.py.bak` | local | delete safely | ignored backup file | none | safe low-risk removal |
| `db.sqlite3` | local, server | archive | Django settings use PostgreSQL, not sqlite; file is likely stale local/proto data | no code path uses sqlite | archive before deletion |
| `server.log` | local, server | runtime artifact | live gunicorn access/error log | deploy script and gunicorn command | local: ignore/remove; server: keep or rotate |
| `nohup.out` | server | server-only runtime artifact | gunicorn stdout/stderr target | deploy script | keep/runtime rotate only |
| `gunicorn.sock` | server | server-only runtime artifact | live gunicorn socket | deploy script, gunicorn | keep |
| `.env.before_restore_20260329212847.bak` | server | archive | safety backup created during production env repair | none in runtime | keep until manual env review |
| `.git/` | server | legacy junk | server is deployed copy, not dev repo | none in deploy path | manual cleanup later |
| `myenv/` | server | keep as runtime | active production venv | deploy script, gunicorn | keep |
| `website/templates/` | local, server | move / manual-root follow-up | tracked locally, excluded from deploy, root-owned on server | Django template loader fallback | relocate live templates out of this folder before cleanup |
| `templates/about.html` | local, server | move/fix, not delete | zero-byte file shadows legacy fallback and is actively rendered | `website.views.about` | replace with real template before any deletion |
| `website/templates/about.html` | local, server | move then archive | non-empty legacy template shadowed by root template | fallback only | merge content or replace root template first |
| `website/templates/register.html` | local, server | move, not delete | live register route depends on it; server copy is root-owned and blocked from deploy | `website.views.register` | create root `templates/register.html` first |
| `templates/gallery.html` | local, server | delete safely | zero-byte, no references | none | safe low-risk removal |
| `templates/hello.html` | local, server | delete safely | zero-byte, no references | none | safe low-risk removal |
| `templates/announcements.html` | local, server | archive | static hard-coded announcement block; no view renders it | none | archive or delete after review |
| `templates/concepts_list.html` | local, server | archive | no route renders it and it references missing `study:` namespace | none | archive or delete after review |
| `templates/concept_detail.html` | local, server | archive | no route renders it and it references missing `study:` namespace | none | archive or delete after review |
| `templates/about.html`, `templates/gallery.html`, `templates/hello.html` | local, server | high-visibility template hygiene issue | zero-byte tracked templates in live template root | route for `about`; none for others | handle in early cleanup batch |
| `assets/css/styles.css` | local, server | delete candidate | tracked but no template references found | none | verify with browser smoke test, then remove |
| `assets/css/styles.min.css` | local, server | delete candidate | tracked but no template references found | none | verify with browser smoke test, then remove |
| `assets/bootstrap/js/bootstrap.min.js` | local, server | replace/fix | tracked file exists, but live template expects `bootstrap.bundle.min.js` | `templates/base.html` | fix reference or source asset before deletion |
| `assets/img/loGOO.jpg` | local, server | rename-or-delete candidate | low-signal filename; no code references found | none | visual audit first |
| `assets/img/PIC1.jpg` | local, server | rename-or-delete candidate | low-signal filename; no code references found | none | visual audit first |
| `assets/img/image.png` | local, server | rename-or-delete candidate | generic filename; no code references found | none | visual audit first |
| `assets/img/photo-1732919258508-3fd53a8007b6.jpg` | local, server | rename-or-delete candidate | upload-style filename; no code references found | none | visual audit first |
| `assets/img/austin.png`, `Gata.jpg`, `kaushik.png`, `naufil.png`, `ojas.png`, `snehan.png`, `NITPY.webp` | local, server | likely unused asset set | no code references found | none | visual audit before delete |
| `assets/img/illustrations/404.svg`, `javascript.svg`, `meeting.svg`, `presentation.svg`, `study.avif`, `teamwork.svg`, `web-development.svg` | local, server | likely unused asset set | no code references found | none | visual audit before delete |
| `img/firess.png` | missing in source, present only in staticfiles | broken reference | dashboard expects it, but source asset missing | `templates/dashboard.html` | recover source or change template |
| `img/flame.png` | missing in source, present only in staticfiles | stale collected asset | file exists only in collected output | no current code refs found | decide whether to restore or remove from staticfiles |
| `img/leap-preview.jpg` | missing in source and server | broken reference | OG metadata points to missing image | `templates/study.html`, `templates/video.html` | add source asset or remove reference |
| `bootstrap/js/bootstrap.bundle.min.js` | missing in source and server | broken reference | base template references nonexistent static file | `templates/base.html` | fix before asset cleanup |
| `website/tests.py` | local, server | keep as-is | placeholder test module, harmless but low value | default Django test discovery | keep until real tests replace it |
| `website/views.py` | local, server | refactor later | duplicate imports and duplicate `submit_test` definitions | imported by URLconf | refactor in a high-risk code batch, not as file cleanup |
| `website/migrations/__pycache__/` | local, server | runtime artifact | pyc cache includes stale names from old migration histories | none | safe delete later |
| `website/__pycache__/`, `LeapWeb/__pycache__/` | local, server | runtime artifact | pyc cache only | none | safe delete later |
| `media/` | local, server | keep as runtime data | user uploads and production content | models and Django media serving | do not delete |
| `staticfiles/` | local, server | keep as runtime artifact | collectstatic output | deploy script and runtime | do not delete blindly |
