# Rename Plan

Status:
- Partial execution completed on 2026-03-30
- High-risk template placement work is finished
- Renames are limited to items with proven references

## Completed Template Moves

| Path | Final Action | Why |
|---|---|---|
| `website/templates/register.html` | replaced with root `templates/register.html` and local duplicate removed | live route depended on a deploy-excluded, root-owned folder on the server |
| `website/templates/about.html` | merged into root `templates/about.html` and local duplicate removed | root template was zero-byte and shadowed the app template |

## Remaining Rename Or Move Candidates

| Path | Proposed Action | Why | References | Risk | Preconditions |
|---|---|---|---|---|---|
| `templates/_test_item.html` | rename to `templates/_profile_test_item.html` | current name is vague | `templates/profile.html` includes it twice | medium | update include references in one batch |
| `assets/img/loGOO.jpg` | rename only if kept | inconsistent casing and low-signal name | no code refs found | low | only after visual audit proves it is needed |
| `assets/img/PIC1.jpg` | rename only if kept | low-signal filename | no code refs found | low | only after visual audit proves it is needed |
| `assets/img/image.png` | rename only if kept | generic filename | no code refs found | low | only after visual audit proves it is needed |
| `assets/img/photo-1732919258508-3fd53a8007b6.jpg` | rename only if kept | upload-style filename | no code refs found | low | only after visual audit proves it is needed |

## Explicit Non-Renames

Do not rename these casually:
- `website/` package
- `LeapWeb/` project package
- migration files under `website/migrations/`
- route-linked templates such as `analyse.html` while URL and view names still use `analyse`
- deploy script paths used by `.github/workflows/deploy.yml`
- gunicorn/runtime paths under `/home/myadmin/LEAP`

## Rename Sequence

1. Template placement: completed.
2. Fix missing static source files and broken template references.
3. Rename only low-risk partials or assets that are still in active use.
4. Leave dead files for delete/archive, not rename.
