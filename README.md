# VHA_mover v1.08

Desktop GUI tool for moving or copying rendered image folders from an artist's work area into the VHA pipeline destination, with automatic versioned backup of any files that would be overwritten.

## Requirements

- Python 3.x
- Tkinter (included with standard Python on Windows)

## Usage

```
python VHA_mover.py
```

1. **Pick shot** — choose `ep → shot → cut → type → user → v` from the cascading dropdowns
   (each lists real folders on disk; the `\maya\images` segment is added automatically and
   `v` is the version folder under it). The last-used username is remembered as the default,
   and the latest version is auto-selected. A **Browse…** button is also available for
   non-standard paths (ep/shot/cut and type are then parsed/auto-detected).
2. **MOVE / COPY** — choose operation mode
3. **Backup ON / OFF** — toggle automatic versioned backup of overwritten files
4. **Run** — executes the operation; destination folder opens in Explorer on success

## Pipeline paths

| Role | Path |
|---|---|
| Destination root | `S:\ANIMA\projects\VHA\pipeline\shots2d` |
| Typical source | `S:\ANIMA\projects\VHA\Work\shots\...` |

### Destination structure

```
{PIPELINE_BASE}\{ep}\{shot}\{cut}\lighting\{type}\current\img\full\data
```

### Backup structure

```
{PIPELINE_BASE}\{ep}\{shot}\{cut}\lighting\{type}\{NN}\img\full\data
```

`{NN}` auto-increments (`01`, `02`, …).

### Source structure

```
{WORK_BASE}\{ep}\{shot}\{cut}\lighting\{type}\{username}\maya\images\{version}
```

`{WORK_BASE}` = `S:\ANIMA\projects\VHA\Work\shots`; the `\maya\images` segment is fixed and
`{version}` is the `v###` render folder under it.

## Changelog

### v1.08 - 2026-06-02
- Added `fx` and `effect` render types between `bgChaShw` and `interact`

### v1.07 — 2026-05-29
- Source input replaced with cascading dropdowns (`ep → shot → cut → type → user → v`) that list real folders on disk; `\maya\images` appended automatically, with the version (`v###`) folder as the 6th level (latest auto-selected)
- Last source selection (`ep/shot/cut/type/user`) remembered and **restored automatically on launch** (stored in `%APPDATA%\VHA_mover\config.json`); version stays latest
- Source type `default` is selectable and maps to destination type `chara`
- **📂 Open** button in the SOURCE header opens the selected source folder in Explorer
- Custom window/taskbar icon (folder + down-arrow, embedded — no external file)
- **↻ Refresh** re-lists episodes; **Browse…** kept as a fallback for non-standard paths
- Fixed: log output from background threads no longer mutates the UI cross-thread (Tcl-error/crash risk)

### v1.06 — 2026-05-25
- Open destination folder in Explorer automatically after a successful (zero-error) move/copy

### v1.05 — 2026-05-12
- Bottom bar: SURFACE2 bg + ACCENT border for contrast against dark BG
- Bar track: BORDER fill + ACCENT2 border, height 18px
- "Clear Log" button: brighter fg=TEXT, bolder font, larger padding
- status_lbl fg upgraded from TEXT2 to TEXT for readability
- Fixed: bottom bar always visible (was hidden when window too short)

### v1.04 — 2026-05-12
- Replaced ttk.Progressbar with custom Canvas bar — full color control on dark theme
- Bar fills with ACCENT purple, turns SUCCESS green at 100%

### v1.03 — 2026-05-12
- Progress bar (determinate %) during run
- `done/total` counter label next to progress bar

### v1.02 — 2026-05-12
- Auto-detect render type from source path
- Window centered on screen at launch
- Version number shown in window title

### v1.01 — 2026-05-12
- Initial release: move/copy rendered frames to VHA pipeline destination
- Versioned backup of duplicate files
- TypeSelector pill-group, MOVE/COPY and Backup ON/OFF toggles
- ep / shot / cut auto-parsed from source path
