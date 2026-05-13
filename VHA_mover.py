import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import threading
import re


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

VERSION = "1.05"

PIPELINE_BASE = r"S:\ANIMA\projects\VHA\pipeline\shots2d"
SKIP_FOLDERS  = {"asset_tracking"}

# path types: display label → subfolder name under lighting\
PATH_TYPES = [
    ("chara",        "chara"),
    ("bg",           "bg"),
    ("bgChaShw",     "bgChaShw"),
    ("interact",     "interact"),
    ("motionVector", "motionVector"),
]


def parse_shot_info(path):
    pattern = re.compile(r'(ep[^/\\]+)[/\\](s[^/\\]+)[/\\](c[^/\\]+)', re.IGNORECASE)
    m = pattern.search(path)
    if m:
        return m.group(1), m.group(2), m.group(3)
    return None, None, None


def detect_type_from_path(path):
    """Return type folder name if path contains \lighting\{TYPE}\, else None."""
    known = {v for _, v in PATH_TYPES}
    m = re.search(r'[/\\]lighting[/\\]([^/\\]+)', path, re.IGNORECASE)
    if m and m.group(1) in known:
        return m.group(1)
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
        self._build_ui()

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
        tk.Label(src_top, text="input folder", font=("Segoe UI", 9),
                 bg=SURFACE, fg=TEXT2).pack(side="left", padx=8)
        tk.Button(src_top, text="Browse…", font=("Segoe UI", 9),
                  bg=ACCENT, fg=WHITE, activebackground=ACCENT2, activeforeground=WHITE,
                  relief="flat", cursor="hand2", padx=12, pady=4,
                  command=self.browse_src).pack(side="right")

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

    # ── reset ────────────────────────────────────────────────────
    def reset_all(self):
        self.src_var.set("")
        self.src_lbl.config(fg=TEXT2)
        self.dst_var.set("")
        self.dst_lbl.config(fg=TEXT2)
        self.dst_tag.config(text="waiting for source…", fg=TEXT2)
        self.bak_var.set("")
        self._ep = self._shot = self._cut = None
        for w in self.chips_frame.winfo_children():
            w.destroy()
        self._hide_action_panel()
        self.status_lbl.config(text="")
        self.log("─── Cleared — select a new source folder. ───", "info")

    # ── browse ───────────────────────────────────────────────────
    def browse_src(self):
        path = filedialog.askdirectory(title="Select Source Folder")
        if not path:
            return
        path = path.replace("/", "\\")
        self.src_var.set(path)
        self.src_lbl.config(fg=SUCCESS)

        ep, shot, cut = parse_shot_info(path)
        detected_type  = detect_type_from_path(path)
        for w in self.chips_frame.winfo_children():
            w.destroy()

        if ep and shot and cut:
            self._ep, self._shot, self._cut = ep, shot, cut
            if detected_type:
                self.type_sel._select(detected_type)
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