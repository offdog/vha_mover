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

---

## Path types (`PATH_TYPES`)

Defined at module level. Each entry is `(display_label, folder_name)`.

| Label | Folder |
|---|---|
| chara | chara |
| bg | bg |
| bgChaShw | bgChaShw |
| interact | interact |
| motionVector | motionVector |

---

## Key functions

| Function | Purpose |
|---|---|
| `parse_shot_info(path)` | Regex-extracts `(ep, shot, cut)` from any path |
| `detect_type_from_path(path)` | Finds `\lighting\{TYPE}\` in path and returns the type folder name, or `None` |
| `build_dst(ep, shot, cut, type_folder)` | Constructs the full destination path |
| `build_backup_root(ep, shot, cut, type_folder)` | Constructs the versioned backup root |
| `next_backup_version(backup_root)` | Scans existing numeric sub-folders and returns the next version path + label |

---

## UI components

| Class | Role |
|---|---|
| `App` | Main window, orchestrates all state |
| `TypeSelector` | Pill-button group for picking path type |
| `ToggleButton` | Two-state toggle (MOVE/COPY, Backup ON/OFF) |

---

## Auto-detect type feature

When the user browses a source folder, `detect_type_from_path()` is called on
the selected path. If the path contains `\lighting\{TYPE}\`, the TypeSelector
is automatically switched to that type and the destination path is recalculated.

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
