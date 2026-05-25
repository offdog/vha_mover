# VHA_mover v1.06

Desktop GUI tool for moving or copying rendered image folders from an artist's work area into the VHA pipeline destination, with automatic versioned backup of any files that would be overwritten.

## Requirements

- Python 3.x
- Tkinter (included with standard Python on Windows)

## Usage

```
python VHA_mover.py
```

1. **Browse** — pick the source folder (ep/shot/cut parsed automatically)
2. **Type** — select render type (chara, bg, bgChaShw, interact, motionVector); auto-detected from path when possible
3. **MOVE / COPY** — choose operation mode
4. **Backup ON / OFF** — toggle automatic versioned backup of overwritten files
5. **Run** — executes the operation; destination folder opens in Explorer on success

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

## Changelog

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
