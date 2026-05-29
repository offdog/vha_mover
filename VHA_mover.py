import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import threading
import re
import json


BG      = "#0f0f11"
SURFACE = "#1a1a1f"
SURFACE2= "#22222a"
BORDER  = "#2e2e38"
ACCENT  = "#6c63ff"
ACCENT2 = "#a89cff"
TEXT    = "#f0eeff"
TEXT2   = "#8a84b0"
SUCCESS = "#3ecf8e"
WARNING = "#f5a623"
ERROR   = "#e84393"
WHITE   = "#ffffff"

VERSION = "1.07"

PIPELINE_BASE = r"S:\ANIMA\projects\VHA\pipeline\shots2d"
WORK_BASE     = r"S:\ANIMA\projects\VHA\Work\shots"
CONFIG_PATH   = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                             "VHA_mover", "config.json")
SKIP_FOLDERS  = {"asset_tracking"}

# path types: display label → subfolder name under lighting\
PATH_TYPES = [
    ("chara",        "chara"),
    ("bg",           "bg"),
    ("bgChaShw",     "bgChaShw"),
    ("interact",     "interact"),
    ("motionVector", "motionVector"),
]

# Window/taskbar icon — folder + down-arrow in ACCENT purple, embedded as PNG
# (base64) so the project stays single-file. Tk 8.6+ decodes PNG in PhotoImage.
_ICON_256_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAEaElEQVR42u3dQU4jSRBA0ciUbwpL"
    "OA0s4azuJVKvUEuY7PrvnWBcrvgVWaI9MwAAAAAAAAAAAAAAAADA2Vbpw7483e++cr7j/XMtATDs"
    "cOkoLEMP3RgsQw/dGCxDD90YLIMP3RAsgw/dEGzDD937d7lw0N0GtuGH7n29XCDobgPb8EP3ft8u"
    "BnTv++0iQPf+XwYfuu8FtuGH7jawDT90I7Bdcujanv7Q3QK24YduBLbhh24EtuGHbgS8BITxEtDT"
    "H4JbwDb80I2AIwA4Anj6Q3EL2IYfuhFwBABHAE9/KG4BNgCwAXj6Q3ELsAGADQAQAOs/pI4BNgCw"
    "AQACYP2H1DHABgA2AEAArP+QOgbYAMAGAAgAIACAAIwXgDCXfhFoAwAbACAAgAAAAgAIACAAgAAA"
    "AgAIACAAgAAAAgAIACAAgAAAAgAIACAAgAAAAgAIAPAoN5fgy9tH57O+Pvu+EYDc4P/9mYXAEcDw"
    "+/wIgJvfdUAA3PSuBwLgZnddEABAADzlXB8EABAAQAAAAQAEABAAQAAAAQAEABAAYPwgCOPPgccv"
    "IgkAHBC5cgwcARCDDwGAfASKIRAACG8D25cL3fvEBgDjHYCqQ/B+2b5M6N43jgDgCAAIgDUOUveP"
    "DQBsAIAAAAIAjH8OzPh37+NFqg2A9I9e+PEMASD+izciIADEf+5KBASA+G/diYAAAAIACAAgAIAA"
    "AAIACAAgAIAAAAIACAAgAIAAAAIACAAgAIAAAAIACAAgAIAAAAIACAAgAIAAAAIACAAgAIAAADNz"
    "cwkm8X/1PfG/9e3D924DIDkMhl8AiA6F4RcAosNh+AWA6JAYfgEgOiyGXwCIDo3hFwCiw2P4BYDo"
    "EBl+AQAEgNrT1NNfAIgOleEXAKLDZfgFgOiQGX4BIDpshl8AiA6d4RcAosNn+AWAaAQMvwAQjYDh"
    "FwCiETD8AkA0AoZfAIhGwPALANEIGH4BIBoBwy8ARCNg+AUAEABqW4CnvwAQjYDhFwCiETD8AkA0"
    "AoZfAIhGwPALANEIGH4BIBoBwy8A2AQQAEAAAAG4gtdnXzLuHxsAIABALACOAbhv4huACOB+cQQA"
    "qgGwBeA+iW8AIoD748ut/CX7M1jqD4btS8fwdz/7zZc//mGMoRcA3BQ4Anzb++daLh+c4V/n0d8B"
    "gA0AEABAAAABGC8CYS77AtAGADYAQAAcAyC1/tsAwAYACIBjAKTWfxsA2AAAAXAMgNT6bwMAG8B5"
    "VQIeM2c2ALAB2AKg9vT/sQ1ABOD/mCtHAHAEsAVA7en/4xuACMDZc+QIAI4AtgCoPf0ftgGIAJw5"
    "N/tKHwYM/8HvAEQAzpoTLwFhvAS0BUDs6f9rG4AIwBlz8euD+PJ0v/vqMfjRnwSzDWD4478JKAIY"
    "/viPgooAhv/xjhw67wUw+OG/A7ANYPjDG4BtAIPvLwFtAxj++gZgG8DgC4AQYPAFQAww9AIgBhh6"
    "ARADDL0AiAKGHQAAAAAAAAAAAAAAALi2PzBJfN0Ss8AFAAAAAElFTkSuQmCC"
)
_ICON_64_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAABNUlEQVR42u1bSRLCMAxrNPwUjvQ1"
    "cIS3ljvTQpo48SadCbU0xpVbtCwEQWRGaT14v26bNTLPdylDBbBIulcMRCR/pl5EJH+mbkQlX1s/"
    "IpOv4YHo5P/xQQbyv3hhSQ4KkKX9j/ixAygABaAAqXGR+JLHq/3senPeAT3kJc6rCiBVvKYIHIIc"
    "gkagNUhDdECPePA6vaXq4QzQuvDe71ajq2CFvJYrpA+gABSAAlAA+gCFW17t50d7A1j26TOMEaz6"
    "9FmuEBaXlZmWGNY2ttn7ADzt7mFug0cipNkG98hqdQYsPMVJ/Vjc9YuR1LuA9js9qXqgcVEr5EWW"
    "IWud0N0BLX8594RvfhyCFEAoeeE1RAHJ+InHBAmkMzje4jMYEUTylB3CqDSWl+AURkbSPKTG0ucG"
    "CSI5Pg1ebjuUGwu6AAAAAElFTkSuQmCC"
)


def parse_shot_info(path):
    pattern = re.compile(r'(ep[^/\\]+)[/\\](s[^/\\]+)[/\\](c[^/\\]+)', re.IGNORECASE)
    m = pattern.search(path)
    if m:
        return m.group(1), m.group(2), m.group(3)
    return None, None, None


def dst_type_for_source(src_type):
    """Map a source type folder to a destination path type.

    Known PATH_TYPES map to themselves; anything else (e.g. the source-only
    `default` folder) falls back to `chara`.
    """
    known = {v for _, v in PATH_TYPES}
    return src_type if src_type in known else "chara"


def detect_type_from_path(path):
    """Return the destination type implied by \lighting\{TYPE}\ in path, else None.

    Recognises the known PATH_TYPES plus the source-only `default` folder
    (mapped to `chara` via dst_type_for_source).
    """
    known = {v for _, v in PATH_TYPES}
    m = re.search(r'[/\\]lighting[/\\]([^/\\]+)', path, re.IGNORECASE)
    if not m:
        return None
    seg = m.group(1)
    if seg in known or seg == "default":
        return dst_type_for_source(seg)
    return None


def build_dst(ep, shot, cut, type_folder):
    suffix = os.path.join("lighting", type_folder, "current", "img", "full", "data")
    return os.path.join(PIPELINE_BASE, ep, shot, cut, suffix)


def build_backup_root(ep, shot, cut, type_folder):
    return os.path.join(PIPELINE_BASE, ep, shot, cut, "lighting", type_folder)


def next_backup_version(backup_root):
    existing = []
    if os.path.isdir(backup_root):
        for name in os.listdir(backup_root):
            if re.fullmatch(r'\d+', name):
                existing.append(int(name))
    nxt = max(existing, default=0) + 1
    ver = f"{nxt:02d}"
    full_path = os.path.join(backup_root, ver, "img", "full", "data")
    return full_path, ver


def list_subdirs(path):
    """Return sorted sub-folder names of path, or [] if unreachable."""
    try:
        return sorted(n for n in os.listdir(path)
                      if os.path.isdir(os.path.join(path, n)))
    except OSError:
        return []


def build_src_images(ep, shot, cut, type_folder, username):
    """Construct the `...\\maya\\images` folder that holds the version sub-folders."""
    return os.path.join(WORK_BASE, ep, shot, cut, "lighting",
                        type_folder, username, "maya", "images")


def build_src(ep, shot, cut, type_folder, username, version):
    """Construct the full source path for a rendered-frames version folder."""
    return os.path.join(build_src_images(ep, shot, cut, type_folder, username),
                        version)


def load_config():
    """Read the JSON config, returning {} on any error."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_config(cfg):
    """Write the JSON config, ignoring write errors."""
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except OSError:
        pass


# ── Path-type toggle row ──────────────────────────────────────────
class TypeSelector(tk.Frame):
    """Pill-group for selecting the destination path type."""
    def __init__(self, parent, types, on_change, **kwargs):
        super().__init__(parent, bg=SURFACE, **kwargs)
        self._var = tk.StringVar(value=types[0][1])
        self._on_change = on_change
        self._btns = {}
        for label, value in types:
            btn = tk.Button(
                self, text=label, font=("Segoe UI", 9, "bold"),
                relief="flat", cursor="hand2", padx=14, pady=7,
                command=lambda v=value: self._select(v))
            btn.pack(side="left", padx=(0, 2))
            self._btns[value] = btn
        self._refresh()

    def _select(self, value):
        self._var.set(value)
        self._refresh()
        self._on_change(value)

    def set(self, value):
        """Public: select a value (same effect as clicking the pill)."""
        if value in self._btns:
            self._select(value)

    def _refresh(self):
        active = self._var.get()
        for value, btn in self._btns.items():
            if value == active:
                btn.config(bg=ACCENT, fg=WHITE,
                           activebackground=ACCENT2, activeforeground=WHITE)
            else:
                btn.config(bg=SURFACE2, fg=TEXT2,
                           activebackground=BORDER, activeforeground=TEXT)

    def get(self):
        return self._var.get()


class Dropdown(tk.Frame):
    """Themed dropdown (Menubutton + Menu) whose options are set at runtime.

    Used for the cascading source picker. Full color control on the dark
    theme — same rationale as the custom Canvas progress bar.
    """
    PLACEHOLDER = "—"

    def __init__(self, parent, label, on_change, width=10, **kwargs):
        super().__init__(parent, bg=SURFACE, **kwargs)
        self._on_change = on_change
        self._var = tk.StringVar(value=self.PLACEHOLDER)

        tk.Label(self, text=label, font=("Segoe UI", 8), bg=SURFACE,
                 fg=TEXT2).pack(anchor="w")
        self._mb = tk.Menubutton(
            self, textvariable=self._var, font=("Segoe UI", 9, "bold"),
            bg=SURFACE2, fg=TEXT, activebackground=ACCENT, activeforeground=WHITE,
            relief="flat", cursor="hand2", width=width, anchor="w",
            padx=10, pady=6, highlightbackground=BORDER, highlightthickness=1,
            takefocus=0)
        self._mb.pack(fill="x")
        self._menu = tk.Menu(
            self._mb, tearoff=0, bg=SURFACE2, fg=TEXT,
            activebackground=ACCENT, activeforeground=WHITE,
            relief="flat", bd=0)
        self._mb.config(menu=self._menu)
        self.set_options([])

    def set_options(self, values):
        """Replace the menu items. Empty list → disabled placeholder."""
        self._menu.delete(0, "end")
        for v in values:
            self._menu.add_command(
                label=v, command=lambda x=v: self._select(x))
        if values:
            self._mb.config(state="normal", fg=TEXT)
        else:
            self._mb.config(state="disabled")
        self._var.set(self.PLACEHOLDER)

    def _select(self, value):
        self._var.set(value)
        self._mb.config(fg=ACCENT2)
        self._on_change(value)

    def set(self, value):
        """Programmatically select a value and fire on_change."""
        self._select(value)

    def get(self):
        v = self._var.get()
        return None if v == self.PLACEHOLDER else v

    def clear(self):
        self._menu.delete(0, "end")
        self._mb.config(state="disabled")
        self._var.set(self.PLACEHOLDER)


class ToggleButton(tk.Frame):
    def __init__(self, parent, left_text, right_text, default="left", **kwargs):
        super().__init__(parent, bg=SURFACE2,
                         highlightbackground=BORDER, highlightthickness=1, **kwargs)
        self._value = tk.StringVar(value=default)
        self._left  = left_text
        self._right = right_text
        self._build()

    def _build(self):
        self.btn_l = tk.Button(
            self, text=self._left, font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=18, pady=6,
            command=lambda: self._select("left"))
        self.btn_l.pack(side="left")
        self.btn_r = tk.Button(
            self, text=self._right, font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=18, pady=6,
            command=lambda: self._select("right"))
        self.btn_r.pack(side="left")
        self._refresh()

    def _select(self, side):
        self._value.set(side)
        self._refresh()

    def _refresh(self):
        if self._value.get() == "left":
            self.btn_l.config(bg=ACCENT,   fg=WHITE, activebackground=ACCENT2, activeforeground=WHITE)
            self.btn_r.config(bg=SURFACE2, fg=TEXT2, activebackground=SURFACE, activeforeground=TEXT)
        else:
            self.btn_l.config(bg=SURFACE2, fg=TEXT2, activebackground=SURFACE, activeforeground=TEXT)
            self.btn_r.config(bg=WARNING,  fg=BG,   activebackground=WARNING,  activeforeground=BG)

    def get(self):
        return self._value.get()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Folder Mover — VHA Pipeline  v{VERSION}")
        self._set_window_icon()
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(720, 820)
        self.update_idletasks()
        w, h = 880, 960
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self._ep = self._shot = self._cut = None
        self._type_folder = PATH_TYPES[0][1]   # default: chara
        self._do_backup = True
        self._cfg = load_config()
        self._username = self._cfg.get("last_username")
        self._restoring = False
        self._build_ui()
        self._populate_ep(restore=True)

    def _set_window_icon(self):
        """Set the window/taskbar icon from the embedded PNGs (Tk 8.6 PNG support)."""
        try:
            self._icons = [tk.PhotoImage(data=_ICON_256_B64),
                           tk.PhotoImage(data=_ICON_64_B64)]
            self.iconphoto(True, *self._icons)
        except tk.TclError:
            pass   # older Tk without PNG support — keep default icon

    # ─────────────────────────────────────────────────────────────
    def _build_ui(self):

        # ── Header ───────────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=30, pady=(28, 0))
        tk.Label(header, text="FOLDER MOVER", font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=ACCENT2).pack(side="left")
        tk.Label(header, text="VHA Pipeline Tool", font=("Segoe UI", 9),
                 bg=BG, fg=TEXT2).pack(side="left", padx=(12, 0), pady=(6, 0))
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=30, pady=14)

        # ── SOURCE ───────────────────────────────────────────────
        src_outer = tk.Frame(self, bg=SURFACE,
                             highlightbackground=BORDER, highlightthickness=1)
        src_outer.pack(fill="x", padx=30)

        src_top = tk.Frame(src_outer, bg=SURFACE)
        src_top.pack(fill="x", padx=16, pady=(16, 8))
        tk.Label(src_top, text="SOURCE", font=("Segoe UI", 10, "bold"),
                 bg=SURFACE, fg=ACCENT2).pack(side="left")
        tk.Label(src_top, text="pick shot", font=("Segoe UI", 9),
                 bg=SURFACE, fg=TEXT2).pack(side="left", padx=8)
        tk.Button(src_top, text="Browse…", font=("Segoe UI", 9),
                  bg=SURFACE2, fg=TEXT2, activebackground=BORDER, activeforeground=TEXT,
                  relief="flat", cursor="hand2", padx=12, pady=4,
                  command=self.browse_src).pack(side="right")
        tk.Button(src_top, text="↻ Refresh", font=("Segoe UI", 9),
                  bg=ACCENT, fg=WHITE, activebackground=ACCENT2, activeforeground=WHITE,
                  relief="flat", cursor="hand2", padx=12, pady=4,
                  command=self._populate_ep).pack(side="right", padx=(0, 8))
        self.src_open_btn = tk.Button(
            src_top, text="📂 Open", font=("Segoe UI", 9),
            bg=SURFACE2, fg=TEXT2, activebackground=BORDER, activeforeground=TEXT,
            relief="flat", cursor="hand2", padx=12, pady=4,
            state="disabled", command=self.open_src)
        self.src_open_btn.pack(side="right", padx=(0, 8))

        # ── Cascading source dropdowns (ep → shot → cut → type → user) ──
        dd_row = tk.Frame(src_outer, bg=SURFACE)
        dd_row.pack(fill="x", padx=16, pady=(0, 8))
        self.ep_dd   = Dropdown(dd_row, "ep",   self._on_ep_change,       width=8)
        self.shot_dd = Dropdown(dd_row, "shot", self._on_shot_change,     width=8)
        self.cut_dd  = Dropdown(dd_row, "cut",  self._on_cut_change,      width=8)
        self.type_dd = Dropdown(dd_row, "type", self._on_src_type_change, width=10)
        self.user_dd = Dropdown(dd_row, "user", self._on_user_change,     width=10)
        self.ver_dd  = Dropdown(dd_row, "v",    self._on_version_change,  width=8)
        for dd in (self.ep_dd, self.shot_dd, self.cut_dd,
                   self.type_dd, self.user_dd, self.ver_dd):
            dd.pack(side="left", padx=(0, 8))

        src_path_f = tk.Frame(src_outer, bg=SURFACE2,
                              highlightbackground=BORDER, highlightthickness=1)
        src_path_f.pack(fill="x", padx=16, pady=(0, 16))
        self.src_var = tk.StringVar(value="")
        self.src_lbl = tk.Label(src_path_f, textvariable=self.src_var,
                                font=("Consolas", 9), bg=SURFACE2, fg=TEXT2,
                                wraplength=800, justify="left", anchor="w",
                                pady=9, padx=12)
        self.src_lbl.pack(fill="x")

        # ── Arrow ────────────────────────────────────────────────
        tk.Label(self, text="↓", font=("Segoe UI", 20), bg=BG, fg=TEXT2).pack(pady=4)

        # ── DESTINATION ──────────────────────────────────────────
        dst_outer = tk.Frame(self, bg=SURFACE,
                             highlightbackground=BORDER, highlightthickness=1)
        dst_outer.pack(fill="x", padx=30)

        dst_top = tk.Frame(dst_outer, bg=SURFACE)
        dst_top.pack(fill="x", padx=16, pady=(16, 8))
        tk.Label(dst_top, text="DESTINATION", font=("Segoe UI", 10, "bold"),
                 bg=SURFACE, fg=SUCCESS).pack(side="left")
        self.dst_tag = tk.Label(dst_top, text="waiting for source…",
                                font=("Segoe UI", 9), bg=SURFACE, fg=TEXT2)
        self.dst_tag.pack(side="left", padx=8)

        # ── Path type selector ───────────────────────────────────
        type_row = tk.Frame(dst_outer, bg=SURFACE)
        type_row.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(type_row, text="Type:", font=("Segoe UI", 9),
                 bg=SURFACE, fg=TEXT2).pack(side="left", padx=(0, 10))
        self.type_sel = TypeSelector(type_row, PATH_TYPES, self._on_type_change)
        self.type_sel.pack(side="left")

        # base path display
        base_f = tk.Frame(dst_outer, bg=SURFACE2,
                          highlightbackground=BORDER, highlightthickness=1)
        base_f.pack(fill="x", padx=16, pady=(0, 4))
        tk.Label(base_f, text=f"Base:  {PIPELINE_BASE}",
                 font=("Consolas", 8), bg=SURFACE2, fg=TEXT2,
                 anchor="w", pady=6, padx=12).pack(fill="x")

        # full destination path
        dst_path_f = tk.Frame(dst_outer, bg=SURFACE2,
                              highlightbackground=BORDER, highlightthickness=1)
        dst_path_f.pack(fill="x", padx=16, pady=(0, 4))
        self.dst_var = tk.StringVar(value="")
        self.dst_lbl = tk.Label(dst_path_f, textvariable=self.dst_var,
                                font=("Consolas", 9), bg=SURFACE2, fg=TEXT2,
                                wraplength=800, justify="left", anchor="w",
                                pady=9, padx=12)
        self.dst_lbl.pack(fill="x")

        # backup preview
        bak_f = tk.Frame(dst_outer, bg=SURFACE2,
                         highlightbackground=BORDER, highlightthickness=1)
        bak_f.pack(fill="x", padx=16, pady=(0, 16))
        bak_row = tk.Frame(bak_f, bg=SURFACE2)
        bak_row.pack(fill="x", padx=12, pady=6)
        tk.Label(bak_row, text="Backup →", font=("Segoe UI", 8),
                 bg=SURFACE2, fg=TEXT2).pack(side="left", padx=(0, 6))
        self.bak_var = tk.StringVar(value="")
        self.bak_lbl = tk.Label(bak_row, textvariable=self.bak_var,
                                font=("Consolas", 8), bg=SURFACE2, fg=TEXT2, anchor="w")
        self.bak_lbl.pack(side="left", fill="x", expand=True)

        # ── Chips row ────────────────────────────────────────────
        self.chips_frame = tk.Frame(self, bg=BG)
        self.chips_frame.pack(fill="x", padx=30, pady=(10, 0))

        # ── ACTION PANEL (hidden until source selected) ───────────
        self.action_panel = tk.Frame(self, bg=SURFACE,
                                     highlightbackground=ACCENT, highlightthickness=2)

        ap_inner = tk.Frame(self.action_panel, bg=SURFACE)
        ap_inner.pack(fill="both", expand=True, padx=16, pady=14)

        ap_left = tk.Frame(ap_inner, bg=SURFACE)
        ap_left.pack(side="left", fill="y")

        tk.Label(ap_left, text="Ready to run",
                 font=("Segoe UI", 11, "bold"), bg=SURFACE, fg=TEXT).pack(anchor="w")
        tk.Label(ap_left, text="Choose mode, then press Run.",
                 font=("Segoe UI", 9), bg=SURFACE, fg=TEXT2).pack(anchor="w", pady=(2, 10))

        mode_row = tk.Frame(ap_left, bg=SURFACE)
        mode_row.pack(anchor="w")
        tk.Label(mode_row, text="Mode:", font=("Segoe UI", 9),
                 bg=SURFACE, fg=TEXT2).pack(side="left", padx=(0, 8))
        self.mode_toggle = ToggleButton(mode_row, "MOVE", "COPY", default="left")
        self.mode_toggle.pack(side="left")

        bak_row = tk.Frame(ap_left, bg=SURFACE)
        bak_row.pack(anchor="w", pady=(10, 0))
        tk.Label(bak_row, text="Backup:", font=("Segoe UI", 9),
                 bg=SURFACE, fg=TEXT2).pack(side="left", padx=(0, 8))
        self.backup_toggle = ToggleButton(bak_row, "ON", "OFF", default="left")
        self.backup_toggle.pack(side="left")

        ap_right = tk.Frame(ap_inner, bg=SURFACE)
        ap_right.pack(side="right")

        self.clear_btn = tk.Button(
            ap_right, text="✕  Clear",
            font=("Segoe UI", 10),
            bg=SURFACE2, fg=TEXT2,
            activebackground=BORDER, activeforeground=TEXT,
            relief="flat", cursor="hand2", padx=18, pady=12,
            command=self.reset_all)
        self.clear_btn.pack(side="left", padx=(0, 10))

        self.run_btn = tk.Button(
            ap_right, text="  ▶  Run  ",
            font=("Segoe UI", 13, "bold"),
            bg=ACCENT, fg=WHITE,
            activebackground=ACCENT2, activeforeground=WHITE,
            relief="flat", cursor="hand2", padx=32, pady=12,
            command=self.start_action)
        self.run_btn.pack(side="left")

        # ── Info bar ─────────────────────────────────────────────
        info_bar = tk.Frame(self, bg=SURFACE2,
                            highlightbackground=BORDER, highlightthickness=1)
        info_bar.pack(fill="x", padx=30, pady=(10, 0))
        tk.Label(info_bar,
                 text="ℹ  Destination auto-generated from ep/shot/cut + type.    "
                      "⊘  asset_tracking skipped.    "
                      "📦  Existing files backed up to versioned folder.",
                 font=("Segoe UI", 9), bg=SURFACE2, fg=TEXT2,
                 pady=7, padx=14).pack(side="left")

        # ── Bottom status (packed before log so it's always visible) ──
        bot_wrap = tk.Frame(self, bg=SURFACE2,
                            highlightbackground=ACCENT, highlightthickness=1)
        bot_wrap.pack(side="bottom", fill="x", padx=30, pady=(8, 12))

        # ── Log ──────────────────────────────────────────────────
        tk.Label(self, text="LOG", font=("Segoe UI", 9, "bold"),
                 bg=BG, fg=TEXT2).pack(anchor="w", padx=30, pady=(12, 4))

        log_frame = tk.Frame(self, bg=SURFACE,
                             highlightbackground=BORDER, highlightthickness=1)
        log_frame.pack(fill="both", expand=True, padx=30)

        self.log_text = tk.Text(log_frame, bg=SURFACE, fg=TEXT2,
                                font=("Consolas", 9), relief="flat",
                                state="disabled", wrap="word", padx=12, pady=10)
        sb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True)

        self.log_text.tag_config("ok",   foreground=SUCCESS)
        self.log_text.tag_config("err",  foreground=ERROR)
        self.log_text.tag_config("info", foreground=ACCENT2)
        self.log_text.tag_config("warn", foreground=WARNING)

        bot = tk.Frame(bot_wrap, bg=SURFACE2)
        bot.pack(fill="x", padx=14, pady=12)

        # canvas progress bar
        bar_track = tk.Frame(bot, bg=BORDER,
                             highlightbackground=ACCENT2, highlightthickness=1)
        bar_track.pack(side="left", fill="x", expand=True)

        self._bar_canvas = tk.Canvas(bar_track, height=18, bg=BORDER,
                                     highlightthickness=0)
        self._bar_canvas.pack(fill="x")
        self._bar_fill = self._bar_canvas.create_rectangle(
            0, 0, 0, 18, fill=ACCENT, width=0)

        self.pct_lbl = tk.Label(bot, text="0%", font=("Segoe UI", 10, "bold"),
                                bg=SURFACE2, fg=ACCENT2, width=5, anchor="e")
        self.pct_lbl.pack(side="left", padx=(12, 0))

        self.status_lbl = tk.Label(bot, text="", font=("Segoe UI", 9),
                                   bg=SURFACE2, fg=TEXT, width=9, anchor="w")
        self.status_lbl.pack(side="left", padx=(6, 0))

        tk.Button(bot, text="Clear Log", font=("Segoe UI", 9, "bold"),
                  bg=BORDER, fg=TEXT, activebackground=SURFACE,
                  activeforeground=WHITE, relief="flat", cursor="hand2",
                  padx=14, pady=6, command=self.clear_log).pack(side="right")

        self.log("Ready — select a source folder to begin.", "info")

    # ── helpers ──────────────────────────────────────────────────
    def log(self, msg, tag=""):
        # Tk is not thread-safe — marshal calls from worker threads to the
        # main loop (see CLAUDE.md: all UI updates go through self.after).
        if threading.current_thread() is not threading.main_thread():
            self.after(0, lambda: self.log(msg, tag))
            return
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def _make_chip(self, label, value):
        f = tk.Frame(self.chips_frame, bg=SURFACE2,
                     highlightbackground=BORDER, highlightthickness=1)
        f.pack(side="left", padx=(0, 8))
        tk.Label(f, text=label, font=("Segoe UI", 8), bg=SURFACE2,
                 fg=TEXT2, padx=6, pady=3).pack(side="left")
        tk.Label(f, text=value, font=("Segoe UI", 8, "bold"), bg=SURFACE2,
                 fg=ACCENT2, padx=4, pady=3).pack(side="left")

    def _show_action_panel(self):
        self.action_panel.pack(fill="x", padx=30, pady=(10, 0),
                               after=self.chips_frame)

    def _hide_action_panel(self):
        self.action_panel.pack_forget()

    def _update_dst_display(self):
        """Recalculate dst + backup preview from current ep/shot/cut + type."""
        if not (self._ep and self._shot and self._cut):
            return
        dst = build_dst(self._ep, self._shot, self._cut, self._type_folder)
        self.dst_var.set(dst)
        self.dst_lbl.config(fg=SUCCESS)
        self._refresh_backup_preview()

    def _on_type_change(self, value):
        self._type_folder = value
        self._update_dst_display()
        if self._ep:
            self.log(f"Type changed → {value}  |  destination updated.", "info")

    def _refresh_backup_preview(self):
        if not (self._ep and self._shot and self._cut):
            return
        dst = build_dst(self._ep, self._shot, self._cut, self._type_folder)
        bak_root = build_backup_root(self._ep, self._shot, self._cut, self._type_folder)
        bak_path, ver = next_backup_version(bak_root)
        has_content = os.path.isdir(dst) and bool(os.listdir(dst))
        if has_content:
            self.bak_var.set(f"{bak_path}  (next: {ver})")
            self.bak_lbl.config(fg=WARNING)
        else:
            self.bak_var.set("No existing files — backup not needed.")
            self.bak_lbl.config(fg=TEXT2)

    def _refresh_src_open(self):
        """Enable the SOURCE 'Open' button only when the source folder exists."""
        src = self.src_var.get()
        if src and not src.startswith("⚠") and os.path.isdir(src):
            self.src_open_btn.config(state="normal", fg=ACCENT2)
        else:
            self.src_open_btn.config(state="disabled", fg=TEXT2)

    def open_src(self):
        src = self.src_var.get()
        if src and os.path.isdir(src):
            os.startfile(src)
        else:
            messagebox.showwarning("Open Folder", f"Source folder not found:\n{src}")

    # ── reset ────────────────────────────────────────────────────
    def reset_all(self):
        self.src_var.set("")
        self.src_lbl.config(fg=TEXT2)
        self._refresh_src_open()
        self.dst_var.set("")
        self.dst_lbl.config(fg=TEXT2)
        self.dst_tag.config(text="waiting for source…", fg=TEXT2)
        self.bak_var.set("")
        self._ep = self._shot = self._cut = None
        for w in self.chips_frame.winfo_children():
            w.destroy()
        self._hide_action_panel()
        self.status_lbl.config(text="")
        self.shot_dd.clear()
        self.cut_dd.clear()
        self.type_dd.clear()
        self.user_dd.clear()
        self.ver_dd.clear()
        self._populate_ep()
        self.log("─── Cleared — select a new source folder. ───", "info")

    # ── cascading source picker ──────────────────────────────────
    def _populate_ep(self, restore=False):
        self.shot_dd.clear()
        self.cut_dd.clear()
        self.type_dd.clear()
        self.user_dd.clear()
        self.ver_dd.clear()
        eps = list_subdirs(WORK_BASE)
        self.ep_dd.set_options(eps)
        if not eps:
            self.log(f"⚠  No episodes found under {WORK_BASE} "
                     f"(drive not mapped?).", "warn")
            return
        # restore the last-used selection on startup (chained via on_change)
        if restore and self._cfg.get("last_ep") in eps:
            self._restoring = True
            self.ep_dd.set(self._cfg["last_ep"])
        else:
            self._restoring = False

    def _on_ep_change(self, ep):
        self.cut_dd.clear()
        self.type_dd.clear()
        self.user_dd.clear()
        self.ver_dd.clear()
        shots = list_subdirs(os.path.join(WORK_BASE, ep))
        self.shot_dd.set_options(shots)
        if self._restoring and self._cfg.get("last_shot") in shots:
            self.shot_dd.set(self._cfg["last_shot"])
        else:
            self._restoring = False

    def _on_shot_change(self, shot):
        ep = self.ep_dd.get()
        self.type_dd.clear()
        self.user_dd.clear()
        self.ver_dd.clear()
        cuts = list_subdirs(os.path.join(WORK_BASE, ep, shot))
        self.cut_dd.set_options(cuts)
        if self._restoring and self._cfg.get("last_cut") in cuts:
            self.cut_dd.set(self._cfg["last_cut"])
        else:
            self._restoring = False

    def _on_cut_change(self, cut):
        ep, shot = self.ep_dd.get(), self.shot_dd.get()
        self.user_dd.clear()
        self.ver_dd.clear()
        lighting = os.path.join(WORK_BASE, ep, shot, cut, "lighting")
        allowed = {v for _, v in PATH_TYPES} | {"default"}
        types = [t for t in list_subdirs(lighting) if t in allowed]
        self.type_dd.set_options(types)
        if not types:
            self.log(f"⚠  No known render types under {lighting}", "warn")
        # type is the last gated level — the rest (user, version) auto-completes
        if self._restoring and self._cfg.get("last_type") in types:
            self.type_dd.set(self._cfg["last_type"])
        self._restoring = False

    def _on_src_type_change(self, type_folder):
        ep, shot, cut = self.ep_dd.get(), self.shot_dd.get(), self.cut_dd.get()
        self.ver_dd.clear()
        type_root = os.path.join(WORK_BASE, ep, shot, cut, "lighting", type_folder)
        users = list_subdirs(type_root)
        self.user_dd.set_options(users)
        # default to the last-used username if it exists here
        if self._username and self._username in users:
            self.user_dd.set(self._username)

    def _on_user_change(self, username):
        ep, shot = self.ep_dd.get(), self.shot_dd.get()
        cut, type_folder = self.cut_dd.get(), self.type_dd.get()
        if not all((ep, shot, cut, type_folder, username)):
            return
        # remember the username as soon as it's chosen
        self._username = username
        self._cfg["last_username"] = username
        save_config(self._cfg)
        # populate the version level and default to the latest version
        images = build_src_images(ep, shot, cut, type_folder, username)
        versions = list_subdirs(images)
        self.ver_dd.set_options(versions)
        if versions:
            self.ver_dd.set(versions[-1])       # newest (zero-padded → last)
        else:
            self.log(f"⚠  No version folders under {images}", "warn")

    def _on_version_change(self, version):
        ep, shot = self.ep_dd.get(), self.shot_dd.get()
        cut, type_folder = self.cut_dd.get(), self.type_dd.get()
        username = self.user_dd.get()
        if not all((ep, shot, cut, type_folder, username, version)):
            return
        src = build_src(ep, shot, cut, type_folder, username, version)
        self.src_var.set(src)
        self.src_lbl.config(fg=SUCCESS if os.path.isdir(src) else WARNING)
        self._refresh_src_open()

        self._ep, self._shot, self._cut = ep, shot, cut
        dst_type = dst_type_for_source(type_folder)
        self.type_sel.set(dst_type)             # syncs destination + _type_folder
        self._update_dst_display()
        self.dst_tag.config(text="auto-generated  ✓", fg=SUCCESS)

        for w in self.chips_frame.winfo_children():
            w.destroy()
        self._make_chip("ep", ep)
        self._make_chip("shot", shot)
        self._make_chip("cut", cut)
        self._make_chip("type", type_folder)
        self._make_chip("user", username)
        self._make_chip("v", version)

        # remember the full selection so it restores on next launch
        self._cfg.update({"last_ep": ep, "last_shot": shot, "last_cut": cut,
                          "last_type": type_folder, "last_username": username})
        save_config(self._cfg)

        if dst_type != type_folder:
            self.log(f"Source type '{type_folder}' → destination type '{dst_type}'.",
                     "info")
        self.log(f"Source ready:  {ep} / {shot} / {cut}  [{type_folder}]  "
                 f"({username} / {version})", "info")
        if not os.path.isdir(src):
            self.log(f"⚠  Source folder does not exist yet:  {src}", "warn")
        self._show_action_panel()

    # ── browse ───────────────────────────────────────────────────
    def browse_src(self):
        path = filedialog.askdirectory(title="Select Source Folder")
        if not path:
            return
        path = path.replace("/", "\\")
        self.src_var.set(path)
        self.src_lbl.config(fg=SUCCESS)
        self._refresh_src_open()

        ep, shot, cut = parse_shot_info(path)
        detected_type  = detect_type_from_path(path)
        for w in self.chips_frame.winfo_children():
            w.destroy()

        if ep and shot and cut:
            self._ep, self._shot, self._cut = ep, shot, cut
            if detected_type:
                self.type_sel.set(detected_type)
                self.log(f"Auto-detected type: {detected_type}", "info")
            self._update_dst_display()
            self.dst_tag.config(text="auto-generated  ✓", fg=SUCCESS)
            self._make_chip("ep", ep)
            self._make_chip("shot", shot)
            self._make_chip("cut", cut)
            self._make_chip("type", self._type_folder)
            self.log(f"Detected:  {ep} / {shot} / {cut}  —  destination ready.", "info")
            self._show_action_panel()
        else:
            self._ep = self._shot = self._cut = None
            self.dst_var.set("⚠  Could not find ep / shot / cut in path")
            self.dst_lbl.config(fg=WARNING)
            self.dst_tag.config(text="(parse failed)", fg=WARNING)
            self.bak_var.set("")
            self.log("⚠  No ep / shot / cut pattern found in the selected path.", "warn")

    # ── run ──────────────────────────────────────────────────────
    def start_action(self):
        src = self.src_var.get()
        dst = self.dst_var.get()

        if not src or src.startswith("⚠"):
            messagebox.showwarning("Error", "Please select a valid source folder.")
            return
        if not dst or dst.startswith("⚠"):
            messagebox.showwarning("Error", "Destination path could not be generated.")
            return
        if not os.path.isdir(src):
            messagebox.showerror("Error", f"Source folder not found:\n{src}")
            return

        if not os.path.isdir(dst):
            if messagebox.askyesno("Create Folder?",
                                   f"Destination does not exist:\n{dst}\n\nCreate it automatically?"):
                try:
                    os.makedirs(dst, exist_ok=True)
                    self.log(f"Created folder: {dst}", "warn")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create folder:\n{e}")
                    return
            else:
                return

        is_copy = self.mode_toggle.get() == "right"
        action  = "Copy" if is_copy else "Move"
        if not messagebox.askyesno("Confirm",
                                   f"{action} all contents from:\n{src}\n\n"
                                   f"To ({self._type_folder}):\n{dst}\n\nProceed?"):
            return

        do_backup = self.backup_toggle.get() == "left"
        self.run_btn.config(state="disabled", bg=SURFACE2, fg=TEXT2)
        self.clear_btn.config(state="disabled")
        self._draw_bar(0)
        self.pct_lbl.config(text="0%", fg=ACCENT2)
        self.status_lbl.config(text="Running…", fg=TEXT)
        threading.Thread(
            target=self._do_action,
            args=(src, dst, is_copy, self._ep, self._shot, self._cut, self._type_folder, do_backup),
            daemon=True
        ).start()

    def _do_action(self, src, dst, copy_mode, ep, shot, cut, type_folder, do_backup=True):
        action = "COPY" if copy_mode else "MOVE"
        total = errors = skipped = backed = 0

        self.log(f"\n{'─'*60}", "info")
        self.log(f"{action}  [{type_folder}]  {src}", "info")
        self.log(f"  →   {dst}", "info")
        self.log(f"{'─'*60}", "info")

        try:
            # ── Backup existing destination contents ──────────────
            dst_items = [i for i in os.listdir(dst)
                         if i.lower() not in SKIP_FOLDERS] if os.path.isdir(dst) else []
            src_items = {i for i in os.listdir(src) if i.lower() not in SKIP_FOLDERS}
            duplicates = [i for i in dst_items if i in src_items]
            src_work   = [i for i in os.listdir(src) if i.lower() not in SKIP_FOLDERS]

            # pre-calculate total steps for progress bar
            bak_steps  = len(duplicates) if do_backup else 0
            work_steps = len(src_work)
            prog_total = bak_steps + work_steps
            prog_done  = 0

            def tick():
                nonlocal prog_done
                prog_done += 1
                self.after(0, lambda d=prog_done, t=prog_total: self._set_progress(d, t))

            if do_backup and duplicates:
                bak_root = build_backup_root(ep, shot, cut, type_folder)
                bak_path, ver = next_backup_version(bak_root)
                os.makedirs(bak_path, exist_ok=True)
                self.log(f"📦  Backing up {len(duplicates)} duplicate(s) → version {ver}", "warn")
                for item in duplicates:
                    try:
                        shutil.move(os.path.join(dst, item), os.path.join(bak_path, item))
                        backed += 1
                        self.log(f"   📦  {item}", "warn")
                    except Exception as e:
                        self.log(f"   ✗  backup failed: {item}  —  {e}", "err")
                    tick()
                self.log(f"   Backed up {backed} item(s) → {bak_path}", "warn")
                self.log("", "")
            elif do_backup and dst_items and not duplicates:
                self.log("ℹ  No duplicate files — backup not needed.", "info")
            elif not do_backup and duplicates:
                self.log(f"🗑  Backup OFF — deleting {len(duplicates)} duplicate(s)...", "warn")
                deleted = 0
                for item in duplicates:
                    item_path = os.path.join(dst, item)
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                        deleted += 1
                        self.log(f"   🗑  {item}", "warn")
                    except Exception as e:
                        self.log(f"   ✗  delete failed: {item}  —  {e}", "err")
                self.log(f"   Deleted {deleted} duplicate(s) from destination.", "warn")
                self.log("", "")

            # ── Move / Copy source → destination ──────────────────
            items = os.listdir(src)
            if not items:
                self.log("⚠  Source folder is empty.", "warn")
            else:
                for item in items:
                    if item.lower() in SKIP_FOLDERS:
                        skipped += 1
                        self.log(f"⊘  skipped:  {item}", "warn")
                        continue
                    src_item = os.path.join(src, item)
                    dst_item = os.path.join(dst, item)
                    try:
                        if copy_mode:
                            if os.path.isdir(src_item):
                                shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
                            else:
                                shutil.copy2(src_item, dst_item)
                        else:
                            shutil.move(src_item, dst_item)
                        total += 1
                        self.log(f"✓  {item}", "ok")
                    except Exception as e:
                        errors += 1
                        self.log(f"✗  {item}  —  {e}", "err")
                    tick()

            self.log(f"{'─'*60}", "info")
            self.log(
                f"Done — {total} succeeded  |  {errors} failed  |  "
                f"{skipped} skipped  |  {backed} backed up",
                "ok" if errors == 0 else "warn"
            )
            if errors == 0 and os.path.isdir(dst):
                self.after(0, lambda d=dst: os.startfile(d))

        except Exception as e:
            self.log(f"Fatal error: {e}", "err")

        self.after(0, self._finish)

    def _draw_bar(self, pct):
        self._bar_canvas.update_idletasks()
        w = self._bar_canvas.winfo_width()
        fill_w = int(w * pct / 100)
        self._bar_canvas.coords(self._bar_fill, 0, 0, fill_w, 18)
        color = SUCCESS if pct == 100 else ACCENT
        self._bar_canvas.itemconfig(self._bar_fill, fill=color)

    def _set_progress(self, done, total):
        pct = int(done / total * 100) if total else 100
        self._draw_bar(pct)
        self.pct_lbl.config(text=f"{pct}%")
        self.status_lbl.config(text=f"{done}/{total}")

    def _finish(self):
        self._draw_bar(100)
        self.pct_lbl.config(text="100%", fg=SUCCESS)
        self.status_lbl.config(text="Done", fg=SUCCESS)
        self.run_btn.config(state="normal", bg=ACCENT, fg=WHITE)
        self.clear_btn.config(state="normal")
        self._refresh_backup_preview()


if __name__ == "__main__":
    app = App()
    app.mainloop()