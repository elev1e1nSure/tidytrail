# TidyTrail

CLI tool for cleaning up download folders. Sorts files, finds duplicates, cleans trash.

## Install

```bash
pip install -e .
```

## Quick Start

```bash
# Interactive mode (run without args)
tidytrail

# Or use commands directly
tidytrail preview
tidytrail sort
tidytrail dupes
tidytrail old -d 90
tidytrail clean
```

## Commands

| Command | Description |
|---------|-------------|
| `preview` | Show sorting plan |
| `sort` | Organize files into folders |
| `dupes` | Find duplicates (MD5) |
| `old` | Show old files |
| `clean` | Remove trash and empty folders |

## Options

- `-r, --recursive` — scan subdirectories
- `-d, --days N` — days for `old` command
- `-y, --yes` — skip confirmation
- `-n, --dry-run` — show plan without executing

## Categories

- `images/` — photos, images, animations
- `docs/` — documents, PDF, Excel, Word
- `archives/` — zip, rar, 7z, tar
- `video/` — video
- `audio/` — music
- `code/` — source code
- `executables/` — exe, msi, dmg

## Examples

```bash
tidytrail                    # interactive menu
tidytrail preview            # show plan for Downloads
tidytrail sort -r            # sort including subfolders
tidytrail dupes              # find duplicates
tidytrail old -d 30          # files older than 30 days
tidytrail clean -r -y        # clean trash without confirmation
```