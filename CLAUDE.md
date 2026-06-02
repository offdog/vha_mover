# VHA_mover — CLAUDE.md

## Project overview

Desktop GUI tool (Python / Tkinter) for moving or copying rendered image folders
from an artist's work area into the VHA pipeline destination, with automatic
versioned backup of any files that would be overwritten.

Single-file project: `VHA_mover.py`

---

## Pipeline paths

| Role | Root |
|---|---|
| Pipeline base (destination root) | `S:\ANIMA\projects\VHA\pipeline\shots2d` |
| Typical source (artist work) | `S:\ANIMA\projects\VHA\Work\shots\...` |

### Destination path structure

```
{PIPELINE_BASE}\{ep}\{shot}\{cut}\lighting\{type}\current\img\full\data
```

### Backup path structure

```
{PIPELINE_BASE}\{ep}\{shot}\{cut}\lighting\{type}\{NN}\img\full\data
```

`{NN}` is a zero-padded integer that auto-increments (`01`, `02`, …).

### Source path structure

```
{WORK_BASE}\{ep}\{shot}\{cut}\lighting\{type}\{username}\maya\images\{version}
```

`{WORK_BASE}` = `S:\ANIMA\projects\VHA\Work\shots`. The `\maya\images` segment is
fixed; `ep / shot / cut / type / username / version` are picked via the cascading
source dropdowns (each level lists real sub-folders on disk). `{version}` is the
`v###` render folder under `maya\images`.

---

## Path types (`PATH_TYPES`)

Defined at module level. Each entry is `(display_label, folder_name)`.

| Label | Folder |
|---|---|
| chara | chara |
| bg | bg |
| bgChaShw | bgChaShw |
| fx | fx |
| effect | effect |
| interact | interact |
| motionVector | motionVector |

---

## Key functions

| Function | Purpose |
|---|---|
| `parse_shot_info(path)` | Regex-extracts `(ep, shot, cut)` from any path |
| `detect_type_from_path(path)` | Finds `\lighting\{TYPE}\` in path and returns the type folder name, or `None` |
| `dst_type_for_source(src_type)` | Maps a source type folder to a destination type; unknown source types (e.g. `default`) fall back to `chara` |
| `build_dst(ep, shot, cut, type_folder)` | Constructs the full destination path |
| `build_backup_root(ep, shot, cut, type_folder)` | Constructs the versioned backup root |
| `next_backup_version(backup_root)` | Scans existing numeric sub-folders and returns the next version path + label |
| `build_src_images(ep, shot, cut, type_folder, username)` | Constructs the `...\maya\images` folder that holds the version sub-folders |
| `build_src(ep, shot, cut, type_folder, username, version)` | Constructs the full source path (ends `\maya\images\{version}`) |
| `list_subdirs(path)` | Sorted sub-folder names of `path`, or `[]` if unreachable (powers the cascading dropdowns) |
| `load_config()` / `save_config(cfg)` | Read/write JSON config at `%APPDATA%\VHA_mover\config.json` (remembers `last_username`) |

---

## UI components

| Class | Role |
|---|---|
| `App` | Main window, orchestrates all state |
| `TypeSelector` | Pill-button group for picking path type |
| `ToggleButton` | Two-state toggle (MOVE/COPY, Backup ON/OFF) |
| `Dropdown` | Themed `Menubutton`+`Menu` dropdown with runtime-set options; used for the cascading source picker |

---

## Cascading source picker

The SOURCE section is six `Dropdown`s (`ep → shot → cut → type → user → v`). Each
selection populates the next level from real sub-folders on disk via
`list_subdirs()`; changing a higher level clears the deeper ones. When `user` is
chosen, the last username is saved to config, the version (`v`) level is populated
and the **latest** version is auto-selected. Choosing a version is the completion
point: `build_src()` assembles the full path, the destination `TypeSelector` is
synced via `dst_type_for_source()` + its public `set()`, and the action panel is shown.

The source `type` dropdown also offers the source-only **`default`** folder. Source
`default` maps to destination type **`chara`** (`dst_type_for_source`) — the source
path keeps `\lighting\default\…` while the destination uses `\lighting\chara\…`.

On launch the last completed selection is restored automatically: `_populate_ep(restore=True)`
sets `self._restoring`, and each `_on_*_change` re-selects the saved `last_ep/shot/cut/type`
(then user + latest version auto-fill). The flag is cleared once `type` is reached or a
saved level no longer exists, so manual selection and Clear/Refresh are unaffected.

A **Browse…** button remains as a fallback for non-standard paths (uses
`parse_shot_info()` + `detect_type_from_path()`); **↻ Refresh** re-lists episodes.

## Auto-detect type feature (Browse fallback)

When the user browses a source folder, `detect_type_from_path()` is called on
the selected path. If the path contains `\lighting\{TYPE}\`, the TypeSelector
is automatically switched to that type and the destination path is recalculated.
A `\lighting\default\` segment is detected and mapped to `chara`.

Detection uses regex `[/\\]lighting[/\\]([^/\\]+)` — exact segment match, so
`bgChaShw` and `bg` are never confused.

---

## Conventions

- All UI updates from background threads must go through `self.after(0, ...)`.
- `SKIP_FOLDERS = {"asset_tracking"}` — always excluded from move/copy/backup.
- Do not add new PATH_TYPES without updating `PATH_TYPES` at the top of the file
  (it drives both the UI and the detection validation).
- Version is stored in `VERSION` constant at the top of `VHA_mover.py`.
  Increment `1.02 → 1.03 → 1.04` for every feature or bug fix, and add a
  changelog entry here at the same time.

---

## Changelog

### v1.08 - 2026-06-02
- Added `fx` and `effect` render types between `bgChaShw` and `interact`

### v1.07 — 2026-05-29
- Source input replaced with cascading dropdowns (`ep → shot → cut → type → user → v`)
  that list real sub-folders on disk; `\maya\images` segment appended automatically and
  the version (`v###`) folder under it is the 6th level, defaulting to the latest version
- Added `WORK_BASE` constant, `build_src_images()` / `build_src()`, `list_subdirs()`, and
  JSON config (`load_config` / `save_config`)
- Config remembers the full last source selection (`last_ep/shot/cut/type/username`) and
  **restores it automatically on launch** (`_populate_ep(restore=True)` + a `_restoring`
  flag that chains the auto-selects; Clear/Refresh do not restore). Version stays latest.
- Source type dropdown also offers the source-only `default` folder; it maps to
  destination type `chara` via `dst_type_for_source()` (also applied in the Browse fallback)
- SOURCE header gained a **📂 Open** button (`open_src`) that opens the selected source
  folder in Explorer; enabled only when the folder exists (`_refresh_src_open`)
- Custom window/taskbar icon (folder + down-arrow in ACCENT purple) embedded as base64
  PNG (`_ICON_256_B64` / `_ICON_64_B64`) and set via `_set_window_icon()` — stays single-file
- New themed `Dropdown` component; `TypeSelector` / `Dropdown` gained public `set()`
- **↻ Refresh** re-lists episodes; **Browse…** kept as fallback for non-standard paths
- Fixed: `self.log()` from worker threads now marshals through `self.after(0, ...)`
  (was mutating the Tk Text widget cross-thread — Tcl-error/crash risk); `os.startfile`
  on success also scheduled on the main loop

### v1.06 — 2026-05-25
- Open destination folder in Explorer automatically after a successful (zero-error) move/copy

### v1.05 — 2026-05-12
- Bottom bar: SURFACE2 bg + ACCENT border for contrast against dark BG
- Bar track: BORDER fill + ACCENT2 border, height 18px
- "Clear Log" button: brighter fg=TEXT, bolder font, larger padding
- status_lbl fg upgraded from TEXT2 to TEXT for readability
- Fixed: bottom bar packed with side="bottom" before log frame so it's always visible (was hidden when window too short)

### v1.04 — 2026-05-12
- Replaced ttk.Progressbar with custom Canvas bar — full color control on dark theme
- Bar fills with ACCENT purple, turns SUCCESS green at 100%
- Bottom bar wrapped in SURFACE panel with border for visibility
- Labels reset color correctly on each new run

### v1.03 — 2026-05-12
- Progress bar (determinate %) during run — covers backup phase + move/copy phase
- Added `done/total` counter label next to progress bar

### v1.02 — 2026-05-12
- Auto-detect type (`chara`, `bgChaShw`, etc.) from source path via `\lighting\{TYPE}\` pattern
- Window centered on screen at launch
- Window height increased (960 px) for a taller log area
- Version number shown in window title

### v1.01 — 2026-05-12
- Initial release: move/copy rendered frames to VHA pipeline destination
- Versioned backup of duplicate files
- TypeSelector pill-group, MOVE/COPY and Backup ON/OFF toggles
- ep / shot / cut auto-parsed from source path
