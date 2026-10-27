"""
YT-DLP GUI by AkiPana
A minimalist front-end for yt-dlp.

Keep this next to yt-dlp.exe, ffmpeg.exe, ffprobe.exe (same folder).
Run build.bat once to turn it into a double-clickable .exe.
"""
import base64
import hashlib
import io
import json
import math
import os
import queue
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
import zipfile
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

APP_NAME = "YT-DLP GUI"
APP_VERSION = "1.0.0"
# Your GitHub repo as "username/repository". Used for the "new version" check and the
# Report a problem / Request a feature links. Leave the placeholder to switch them off.
GITHUB_REPO = "YOUR-USERNAME/yt-dlp-gui"

APP_DIR = os.path.dirname(
    os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__)
)
DATA_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share"),
    APP_NAME,
)
TOOLS_DIR = os.path.join(DATA_DIR, "tools")
CONFIG_FILE = os.path.join(DATA_DIR, "settings.json")
STATE_FILE = os.path.join(DATA_DIR, "tools-state.json")
OLD_CONFIG_FILE = os.path.join(APP_DIR, "yt-dlp-gui-settings.json")  # from earlier versions
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
HAS_REPO = "YOUR-USERNAME" not in GITHUB_REPO

# Official download sources (nothing is redistributed by this app)
YTDLP_REPO = "yt-dlp/yt-dlp"
YTDLP_URL = f"https://github.com/{YTDLP_REPO}/releases/latest/download/yt-dlp.exe"
YTDLP_SUMS = f"https://github.com/{YTDLP_REPO}/releases/latest/download/SHA2-256SUMS"
FFMPEG_BASE = "https://github.com/yt-dlp/FFmpeg-Builds/releases/latest/download/"
FFMPEG_ZIP = "ffmpeg-master-latest-win64-gpl.zip"
FFMPEG_SUMS = FFMPEG_BASE + "checksums.sha256"
DENO_BASE = "https://github.com/denoland/deno/releases/latest/download/"
DENO_ZIP = "deno-x86_64-pc-windows-msvc.zip"

LOGO_LIGHT = "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"
LOGO_DARK = "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"

# ---- colours: (light, dark) ------------------------------------------------
BG = ("#F5F5F7", "#151517")
CARD = ("#FFFFFF", "#202023")
BORDER = ("#E3E3E8", "#2D2D32")
FIELD = ("#F0F0F3", "#2A2A2E")
TEXT = ("#1C1C1E", "#F2F2F5")
MUTED = ("#6E6E78", "#9A9AA6")
ACCENT = "#E5231B"
ACCENT_HOVER = "#C41D16"
GREY_BTN = ("#D9D9DE", "#3A3A40")
GREY_BTN_HOVER = ("#C8C8CE", "#4A4A52")
OK = ("#1E8E3E", "#4CD27A")
ERR = ("#C5221F", "#FF6B63")

# ---- choices ---------------------------------------------------------------
VIDEO_QUALITIES = ["Best available", "4K (2160p)", "1440p", "1080p", "720p", "480p", "360p"]
CONTAINERS = ["MP4", "MKV", "WEBM"]
AUDIO_FORMATS = ["MP3", "M4A", "OPUS", "FLAC", "WAV"]
AUDIO_QUALITIES = ["Best", "High (320 kbps)", "Medium (192 kbps)", "Low (128 kbps)"]
BROWSERS = ["None", "Chrome", "Edge", "Firefox", "Brave", "Opera", "Vivaldi"]

HOME = os.path.expanduser("~")
FOLDERS = {
    "Downloads": os.path.join(HOME, "Downloads"),
    "Desktop": os.path.join(HOME, "Desktop"),
    "Videos": os.path.join(HOME, "Videos"),
    "Music": os.path.join(HOME, "Music"),
}

DEFAULTS = {
    "theme": "system",
    "mode": "video",
    "quality": "1080p",
    "container": "MP4",
    "audio_format": "MP3",
    "audio_quality": "Best",
    "compat": True,
    "playlist": False,
    "thumbnail": False,
    "metadata": True,
    "subs": False,
    "sub_langs": "en",
    "cookies": "None",
    "extra": "",
    "save_dir": FOLDERS["Downloads"],
}

PCT_RE = re.compile(r"\[download\]\s+(\d+(?:\.\d+)?)%")
SPEED_RE = re.compile(r"at\s+(\S+/s)")
ETA_RE = re.compile(r"ETA\s+(\S+)")
FORMATS_RE = re.compile(r"Downloading \d+ format\(s\):\s*(\S+)")


def resource_path(name):
    base = getattr(sys, "_MEIPASS", APP_DIR)
    p = os.path.join(base, name)
    return p if os.path.exists(p) else os.path.join(APP_DIR, name)


def load_logo(b64):
    return Image.open(io.BytesIO(base64.b64decode(b64)))


def friendly_error(line):
    low = line.lower()
    if "sign in" in low or "age" in low and "restrict" in low or "cookies" in low or "login" in low:
        return "This video needs a login. Open Advanced options and pick your browser under \"Use my browser login\"."
    if "unsupported url" in low:
        return "That link isn't supported. Check that you copied the full video link."
    if "private video" in low or "video unavailable" in low or "not available" in low:
        return "This video is private or unavailable."
    if "ffmpeg" in low and ("not found" in low or "not installed" in low):
        return "ffmpeg wasn't found. Keep ffmpeg.exe in the same folder as this app."
    if "unable to download" in low or "getaddrinfo" in low or "timed out" in low:
        return "Couldn't reach the website. Check your internet connection."
    return line.replace("ERROR:", "").strip()[:160]


# ============================================================================
#  Tool management: find / download / verify / update yt-dlp, ffmpeg and deno
# ============================================================================
class ToolError(Exception):
    pass


class Cancelled(Exception):
    pass


STATE = {}


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            STATE.update(json.load(f))
    except Exception:
        pass


def save_state():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(STATE, f, indent=2)
    except Exception:
        pass


def find_tool(name):
    """Look in our tools folder first, then next to the app, then on PATH."""
    for folder in (TOOLS_DIR, APP_DIR):
        p = os.path.join(folder, name + ".exe")
        if os.path.isfile(p):
            return p
    return shutil.which(name)


def http_open(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": f"YT-DLP-GUI/{APP_VERSION}"})
    return urllib.request.urlopen(req, timeout=timeout)


def http_text(url):
    with http_open(url, 30) as r:
        return r.read().decode("utf-8", "replace")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def latest_release_tag(repo):
    """Newest release tag of a GitHub repo, read from the /releases/latest redirect."""
    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(f"https://github.com/{repo}/releases/latest",
                                 headers={"User-Agent": f"YT-DLP-GUI/{APP_VERSION}"})
    try:
        opener.open(req, timeout=20)
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location", "")
        if "/tag/" in loc:
            return urllib.parse.unquote(loc.rsplit("/tag/", 1)[1])
        raise
    return None


def vtuple(v):
    nums = re.findall(r"\d+", v or "")[:3]
    return tuple(int(n) for n in nums) if len(nums) == 3 else None


def local_version(exe):
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=25,
                             creationflags=NO_WINDOW).stdout.strip()
        return out.splitlines()[0] if out else None
    except Exception:
        return None


def parse_sums(text, filename):
    m = re.search(r"^\s*Hash\s*:\s*([0-9A-Fa-f]{64})\s*$", text, re.M)  # PowerShell style
    if m:
        return m.group(1).lower()
    rows = [ln.split() for ln in text.splitlines() if ln.strip()]
    for parts in rows:
        if len(parts) >= 2 and parts[-1].lstrip("*").split("/")[-1] == filename:
            return parts[0].lower()
    if len(rows) == 1 and len(rows[0]) == 1:
        return rows[0][0].lower()
    return None


def download_file(url, dest, progress, cancel):
    """Stream url to dest, return its sha256. Removes the partial file on any failure."""
    sha = hashlib.sha256()
    try:
        with http_open(url, 60) as r, open(dest, "wb") as f:
            total = int(r.headers.get("Content-Length") or 0)
            done = 0
            while True:
                if cancel.is_set():
                    raise Cancelled()
                chunk = r.read(256 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                sha.update(chunk)
                done += len(chunk)
                if total:
                    progress(min(done / total, 1.0))
    except BaseException:
        try:
            os.remove(dest)
        except OSError:
            pass
        raise
    return sha.hexdigest()


def fetch_verified(url, sums_url, filename, dest, progress, cancel):
    expected = parse_sums(http_text(sums_url), filename)
    if not expected:
        raise ToolError("Couldn't read the official checksum for " + filename)
    got = download_file(url, dest, progress, cancel)
    if got != expected:
        try:
            os.remove(dest)
        except OSError:
            pass
        raise ToolError(f"The downloaded {filename} didn't match its official checksum, "
                        "so it was discarded. Please try again.")
    return expected


def extract_exes(zip_path, wanted):
    """Pull only the wanted .exe names out of a zip (from any folder inside it)."""
    found = set()
    with zipfile.ZipFile(zip_path) as z:
        for member in z.namelist():
            base = member.rsplit("/", 1)[-1].lower()
            if base in wanted and not member.endswith("/"):
                target = os.path.join(TOOLS_DIR, base)
                with z.open(member) as src, open(target + ".new", "wb") as dst:
                    shutil.copyfileobj(src, dst)
                os.replace(target + ".new", target)
                found.add(base)
    return found


def install_ytdlp(progress, cancel):
    os.makedirs(TOOLS_DIR, exist_ok=True)
    tmp = os.path.join(TOOLS_DIR, "yt-dlp.exe.new")
    fetch_verified(YTDLP_URL, YTDLP_SUMS, "yt-dlp.exe", tmp, progress, cancel)
    os.replace(tmp, os.path.join(TOOLS_DIR, "yt-dlp.exe"))


def install_ffmpeg(progress, cancel):
    os.makedirs(TOOLS_DIR, exist_ok=True)
    tmp = os.path.join(TOOLS_DIR, "ffmpeg.zip.part")
    digest = fetch_verified(FFMPEG_BASE + FFMPEG_ZIP, FFMPEG_SUMS, FFMPEG_ZIP, tmp,
                            progress, cancel)
    try:
        found = extract_exes(tmp, {"ffmpeg.exe", "ffprobe.exe"})
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    if "ffmpeg.exe" not in found:
        raise ToolError("ffmpeg.exe wasn't found inside the download.")
    STATE["ffmpeg_hash"] = digest
    STATE["ffmpeg_date"] = time.time()
    save_state()


def install_deno(progress, cancel):
    os.makedirs(TOOLS_DIR, exist_ok=True)
    tmp = os.path.join(TOOLS_DIR, "deno.zip.part")
    fetch_verified(DENO_BASE + DENO_ZIP, DENO_BASE + DENO_ZIP + ".sha256sum", DENO_ZIP, tmp,
                   progress, cancel)
    try:
        found = extract_exes(tmp, {"deno.exe"})
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    if "deno.exe" not in found:
        raise ToolError("deno.exe wasn't found inside the download.")


# name -> (size, what it's for, installer)
TOOL_INFO = {
    "yt-dlp": ("24 MB", "the downloader itself", install_ytdlp),
    "ffmpeg": ("200 MB", "joins video + audio and converts to MP3", install_ffmpeg),
    "deno": ("43 MB", "needed for YouTube to work properly", install_deno),
}


# ============================================================================
#  Pop-up dialog (message + buttons, optional download progress)
# ============================================================================
class ToolDialog(ctk.CTkToplevel):
    """buttons: list of dicts {text, key, run}. The first one is the main (red) button.
    If a button has run=True the dialog runs `jobs` [(label, fn(progress, cancel))] with a
    progress bar, then closes. on_done(key, ok) is called when the dialog closes."""

    def __init__(self, app, title, message, buttons, jobs=None, on_done=None):
        super().__init__(app)
        self.app, self.jobs, self.on_done = app, jobs or [], on_done
        self.buttons, self.message = buttons, message
        self.q = queue.Queue()
        self.cancel_evt = threading.Event()
        self.running = False
        self.closed = False
        self.run_key = None

        self.title(title)
        self.configure(fg_color=BG)
        self.resizable(False, False)
        self.transient(app)

        lines = sum(max(1, math.ceil(len(ln) / 60)) for ln in message.split("\n"))
        w, h = 540, 124 + lines * 20 + (56 if self.jobs else 0)
        x = app.winfo_rootx() + max(10, (app.winfo_width() - w) // 2)
        y = app.winfo_rooty() + 50
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.btn_row = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_row.pack(side="bottom", fill="x", padx=24, pady=(0, 20))
        ctk.CTkLabel(self, text=title, text_color=TEXT, anchor="w",
                     font=ctk.CTkFont(size=18, weight="bold")
                     ).pack(side="top", fill="x", padx=24, pady=(20, 6))
        self.msg = ctk.CTkLabel(self, text=message, text_color=MUTED, anchor="nw",
                                justify="left", wraplength=490, font=ctk.CTkFont(size=13))
        self.msg.pack(side="top", fill="x", padx=24)
        self.step = ctk.CTkLabel(self, text="", text_color=TEXT, anchor="w",
                                 font=ctk.CTkFont(size=12))
        self.bar = ctk.CTkProgressBar(self, height=8, corner_radius=4, fg_color=BORDER,
                                      progress_color=ACCENT)
        self.bar.set(0)
        self.show_buttons(buttons)

        self.protocol("WM_DELETE_WINDOW", self.on_x)
        self.after(120, self.grab)
        self.after(80, self.poll)

    def grab(self):
        try:
            self.lift()
            self.focus_force()
            self.grab_set()
        except tk.TclError:
            pass

    def show_buttons(self, buttons):
        for w in self.btn_row.winfo_children():
            w.destroy()
        for i, b in enumerate(buttons):
            primary = i == 0
            ctk.CTkButton(
                self.btn_row, text=b["text"], height=36, corner_radius=9,
                width=130 if primary else 100,
                fg_color=ACCENT if primary else GREY_BTN,
                hover_color=ACCENT_HOVER if primary else GREY_BTN_HOVER,
                text_color="#FFFFFF" if primary else TEXT,
                font=ctk.CTkFont(size=13, weight="bold" if primary else "normal"),
                command=lambda b=b: self.pressed(b)).pack(side="right", padx=(8, 0))

    def pressed(self, b):
        if b.get("run") and self.jobs:
            self.start(b["key"])
        else:
            self.close(b["key"], True)

    def start(self, key):
        self.run_key = key
        self.running = True
        self.cancel_evt.clear()
        self.msg.configure(text=self.message, text_color=MUTED)
        self.step.pack(side="top", fill="x", padx=24, pady=(14, 4))
        self.bar.pack(side="top", fill="x", padx=24)
        self.bar.set(0)
        self.show_buttons([{"text": "Cancel", "key": "cancel"}])
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        n = len(self.jobs)
        try:
            for i, (label, fn) in enumerate(self.jobs, 1):
                self.q.put(("step", f"Step {i} of {n}: downloading {label}"))
                self.q.put(("progress", 0.0))
                fn(lambda f: self.q.put(("progress", f)), self.cancel_evt)
            self.q.put(("done", None))
        except Cancelled:
            self.q.put(("error", "Cancelled."))
        except urllib.error.URLError:
            self.q.put(("error", "Couldn't connect. Check your internet connection and try again."))
        except Exception as e:
            self.q.put(("error", f"Something went wrong: {e}"))

    def poll(self):
        if self.closed:
            return
        try:
            while True:
                kind, data = self.q.get_nowait()
                if kind == "progress":
                    self.bar.set(data)
                elif kind == "step":
                    self.step.configure(text=data)
                elif kind == "done":
                    self.running = False
                    self.close(self.run_key, True)
                    return
                elif kind == "error":
                    self.running = False
                    self.msg.configure(text=data, text_color=ERR)
                    self.show_buttons([{"text": "Try again", "key": self.run_key, "run": True},
                                       {"text": "Close", "key": "close"}])
        except queue.Empty:
            pass
        self.after(80, self.poll)

    def on_x(self):
        if self.running:
            self.cancel_evt.set()
            return
        later = self.buttons[1]["key"] if len(self.buttons) > 1 else self.buttons[0]["key"]
        self.close(later, False if self.run_key else True)

    def close(self, key, ok):
        if self.closed:
            return
        self.closed = True
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()
        if self.on_done:
            self.on_done(key, ok)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cfg = dict(DEFAULTS)
        for path in (OLD_CONFIG_FILE, CONFIG_FILE):  # old location first, new one wins
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.cfg.update(json.load(f))
            except Exception:
                pass
        load_state()

        for key, values in (("quality", VIDEO_QUALITIES), ("container", CONTAINERS),
                            ("audio_format", AUDIO_FORMATS), ("audio_quality", AUDIO_QUALITIES),
                            ("cookies", BROWSERS)):
            match = [v for v in values if v.lower() == str(self.cfg[key]).lower()]
            self.cfg[key] = match[0] if match else DEFAULTS[key]
        if self.cfg["theme"] not in ("system", "light", "dark"):
            self.cfg["theme"] = "system"

        ctk.set_appearance_mode(self.cfg["theme"])
        self.title(APP_NAME)
        self.configure(fg_color=BG)
        self.resizable(False, False)
        self.after(250, self.set_icon)

        self.exe = None
        self.ffmpeg_dir = None
        self.has_deno = False
        self.offers = []
        self.notes = []
        self.manual_check = False
        self.refresh_tools()
        self.q = queue.Queue()
        self.proc = None
        self.running = False
        self.cancelled = False
        self.save_dir = self.cfg["save_dir"]
        self.adv_open = False
        self.last_error = ""
        self.passes_done = 0
        self.passes_expected = 1

        self.build_ui()
        self.apply_mode()
        self.set_idle_status()
        self.fit_window()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(100, self.poll_queue)
        self.after(700, self.startup_checks)

    # ------------------------------------------------- tools: setup & updates
    def refresh_tools(self):
        self.exe = find_tool("yt-dlp")
        ff = find_tool("ffmpeg")
        self.ffmpeg_dir = os.path.dirname(ff) if ff else None
        self.has_deno = bool(find_tool("deno"))

    def missing_tools(self, include_optional=True):
        m = []
        if not self.exe:
            m.append("yt-dlp")
        if not self.ffmpeg_dir:
            m.append("ffmpeg")
        if include_optional and not self.has_deno and not STATE.get("skip_deno"):
            m.append("deno")
        return m

    def open_tools_folder(self):
        os.makedirs(TOOLS_DIR, exist_ok=True)
        try:
            os.startfile(TOOLS_DIR)
        except AttributeError:
            pass

    def dialog(self, title, message, buttons, jobs=None, on_done=None):
        ToolDialog(self, title, message, buttons, jobs, on_done)

    def offer_setup(self, then=None):
        """Offer to download whatever tools are missing."""
        missing = self.missing_tools()
        if not missing:
            if then:
                then()
            return
        required_missing = bool(self.missing_tools(include_optional=False))
        lines = [f"\u2022 {n} ({TOOL_INFO[n][0]}): {TOOL_INFO[n][1]}" for n in missing]
        if required_missing:
            title = "One-time setup"
            msg = ("To download videos, this app needs a few free tools:\n\n" + "\n".join(lines) +
                   "\n\nThey come straight from their official websites and are saved in your "
                   "user folder. You only do this once.")
        else:
            title = "Quick add-on for YouTube"
            msg = ("YouTube now needs a small helper to download reliably:\n\n" + "\n".join(lines) +
                   "\n\nIt comes from its official website. Skip it if you don't use YouTube.")
        buttons = [{"text": "Download", "key": "go", "run": True},
                   {"text": "Not now", "key": "later"}]
        if not required_missing:
            buttons.append({"text": "Don't ask again", "key": "never"})
        jobs = [(f"{n} ({TOOL_INFO[n][0]})", TOOL_INFO[n][2]) for n in missing]

        def done(key, ok):
            if key == "never":
                STATE["skip_deno"] = True
                save_state()
            self.refresh_tools()
            if key == "go" and ok:
                self.set_status("Setup complete. Paste a link to get started.", "ok")
            elif not self.exe or not self.ffmpeg_dir:
                self.set_status("Setup isn't finished yet. Click Download again, or open "
                                "Advanced options > Check for updates.", "err")
            if then:
                then()

        self.dialog(title, msg, buttons, jobs, done)

    def startup_checks(self):
        self.refresh_tools()
        if not self.exe or not self.ffmpeg_dir:
            self.set_status("Setup needed.", "err")
        self.offer_setup(then=lambda: self.start_update_checks(manual=False))

    def check_now(self):
        if self.running:
            self.set_status("Wait for the current download to finish first.", "err")
            return
        self.refresh_tools()
        self.set_status("Checking for updates...", "text")
        self.offer_setup(then=lambda: self.start_update_checks(manual=True))

    def start_update_checks(self, manual):
        threading.Thread(target=self.check_worker, args=(manual,), daemon=True).start()

    def check_worker(self, manual):
        offers, notes = [], []
        now = time.time()
        failed = False
        # yt-dlp (daily)
        try:
            if self.exe and (manual or now - STATE.get("last_ytdlp", 0) > 86400):
                latest = latest_release_tag(YTDLP_REPO)
                STATE["last_ytdlp"] = now
                local = local_version(self.exe)
                if latest and vtuple(latest) and vtuple(local) and vtuple(latest) > vtuple(local):
                    if manual or STATE.get("skip_ytdlp") != latest:
                        offers.append(("ytdlp", local, latest))
                elif manual and local:
                    notes.append(f"yt-dlp is up to date ({local}).")
        except Exception:
            failed = True
        # ffmpeg (weekly, only for the copy this app downloaded)
        try:
            managed = (os.path.isfile(os.path.join(TOOLS_DIR, "ffmpeg.exe"))
                       and STATE.get("ffmpeg_hash"))
            if managed and (manual or now - STATE.get("last_ffmpeg", 0) > 7 * 86400):
                remote = parse_sums(http_text(FFMPEG_SUMS), FFMPEG_ZIP)
                STATE["last_ffmpeg"] = now
                age_days = (now - STATE.get("ffmpeg_date", now)) / 86400
                if remote and remote != STATE["ffmpeg_hash"] and (manual or age_days > 45):
                    if manual or STATE.get("skip_ffmpeg") != remote:
                        offers.append(("ffmpeg", remote))
                elif manual:
                    notes.append("ffmpeg is up to date.")
            elif manual and self.ffmpeg_dir and not managed:
                notes.append("ffmpeg: you're using your own copy, so it isn't checked.")
        except Exception:
            failed = True
        # this app (daily)
        try:
            if HAS_REPO and (manual or now - STATE.get("last_app", 0) > 86400):
                latest = latest_release_tag(GITHUB_REPO)
                STATE["last_app"] = now
                if latest and vtuple(latest) and vtuple(latest) > vtuple(APP_VERSION):
                    if manual or STATE.get("skip_app") != latest:
                        offers.append(("app", latest))
                elif manual:
                    notes.append(f"YT-DLP GUI is up to date (v{APP_VERSION}).")
        except Exception:
            failed = True
        save_state()
        if manual and failed and not offers:
            notes = ["Couldn't check for updates. Are you online?"] + notes
        self.q.put(("call", lambda: self.show_offers(offers, notes, manual)))

    def show_offers(self, offers, notes, manual):
        self.offers, self.notes, self.manual_check = list(offers), notes, manual
        self.next_offer()

    def next_offer(self):
        if not self.offers:
            if not self.running and self.exe and self.ffmpeg_dir:
                self.set_idle_status()
            if self.manual_check:
                if self.notes:
                    self.dialog("Updates", "\n".join(self.notes),
                                [{"text": "OK", "key": "ok"}])
                self.manual_check = False
            return
        kind, *info = self.offers.pop(0)
        if kind == "ytdlp":
            local, latest = info
            title, key_skip = "yt-dlp update available", ("skip_ytdlp", latest)
            msg = (f"A new version of yt-dlp is available ({latest}). You have {local}.\n\n"
                   "Updating keeps downloads working when websites change things. "
                   "It's a quick 24 MB download.")
            jobs = [("yt-dlp (24 MB)", install_ytdlp)]
            go = "Update"
        elif kind == "ffmpeg":
            title, key_skip = "ffmpeg update available", ("skip_ffmpeg", info[0])
            msg = ("A new version of ffmpeg is available.\n\nThis is optional. Your current one "
                   "keeps working. The download is about 200 MB.")
            jobs = [("ffmpeg (200 MB)", install_ffmpeg)]
            go = "Update"
        else:
            latest = info[0]
            title, key_skip = "New version of YT-DLP GUI", ("skip_app", latest)
            msg = f"YT-DLP GUI {latest} is available. You have v{APP_VERSION}."
            jobs = None
            go = "Open download page"
        buttons = [{"text": go, "key": "go", "run": bool(jobs)},
                   {"text": "Not now", "key": "later"},
                   {"text": "Skip this version", "key": "skip"}]

        def done(key, ok):
            if key == "skip":
                STATE[key_skip[0]] = key_skip[1]
                save_state()
            elif key == "go":
                if kind == "app":
                    webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
                elif ok:
                    self.refresh_tools()
                    self.set_status(("yt-dlp" if kind == "ytdlp" else "ffmpeg") + " updated.", "ok")
            self.next_offer()

        self.dialog(title, msg, buttons, jobs, done)

    def set_icon(self):
        try:
            self.iconbitmap(resource_path("yt-dlp-gui.ico"))
        except Exception:
            pass

    # ------------------------------------------------------------------ UI
    def build_ui(self):
        c = self.cfg
        self.v_mode = tk.StringVar(value=c["mode"])
        self.v_quality = tk.StringVar(value=c["quality"])
        self.v_container = tk.StringVar(value=c["container"])
        self.v_aformat = tk.StringVar(value=c["audio_format"])
        self.v_aquality = tk.StringVar(value=c["audio_quality"])
        self.v_compat = tk.BooleanVar(value=c["compat"])
        self.v_playlist = tk.BooleanVar(value=c["playlist"])
        self.v_thumb = tk.BooleanVar(value=c["thumbnail"])
        self.v_meta = tk.BooleanVar(value=c["metadata"])
        self.v_subs = tk.BooleanVar(value=c["subs"])
        self.v_langs = tk.StringVar(value=c["sub_langs"])
        self.v_cookies = tk.StringVar(value=c["cookies"])
        self.v_extra = tk.StringVar(value=c["extra"])
        self.v_folder = tk.StringVar(value=self.save_dir)

        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=26, pady=(20, 22))
        root.grid_columnconfigure(0, weight=1)
        self.root_frame = root

        # --- header
        head = ctk.CTkFrame(root, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew")
        head.grid_columnconfigure(1, weight=1)
        logo = ctk.CTkImage(light_image=load_logo(LOGO_LIGHT), dark_image=load_logo(LOGO_DARK),
                            size=(87, 38))
        ctk.CTkLabel(head, image=logo, text="").grid(row=0, column=0, padx=(0, 12))
        title = ctk.CTkFrame(head, fg_color="transparent")
        title.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(title, text="YT-DLP GUI", text_color=TEXT,
                     font=ctk.CTkFont(size=26, weight="bold")).pack(side="left")
        ctk.CTkLabel(title, text="  by AkiPana", text_color=MUTED,
                     font=ctk.CTkFont(size=13)).pack(side="left", pady=(8, 0))
        self.theme_switch = ctk.CTkSwitch(
            head, text="Dark mode", text_color=MUTED, progress_color=ACCENT,
            button_color=("#FFFFFF", "#FFFFFF"), button_hover_color=("#F0F0F0", "#E0E0E0"),
            fg_color=GREY_BTN, command=self.toggle_theme)
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()
        self.theme_switch.grid(row=0, column=2, sticky="e")

        # --- link row
        row = ctk.CTkFrame(root, fg_color="transparent")
        row.grid(row=1, column=0, sticky="ew", pady=(22, 0))
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text="Link", text_color=TEXT,
                     font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, padx=(0, 12))
        self.url = ctk.CTkEntry(row, height=42, corner_radius=10, border_width=1,
                                border_color=BORDER, fg_color=CARD, text_color=TEXT,
                                placeholder_text="Paste a video link here...")
        self.url.grid(row=0, column=1, sticky="ew")
        self.url.bind("<Return>", lambda e: self.on_download_click())
        self.bind_paste_menu(self.url)
        self.btn_dl = ctk.CTkButton(row, text="Download", width=150, height=42, corner_radius=10,
                                    fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#FFFFFF",
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    command=self.on_download_click)
        self.btn_dl.grid(row=0, column=2, padx=(10, 0))

        # --- progress + status
        self.progress = ctk.CTkProgressBar(root, height=6, corner_radius=3, fg_color=BORDER,
                                           progress_color=ACCENT)
        self.progress.set(0)
        self.progress.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        srow = ctk.CTkFrame(root, fg_color="transparent")
        srow.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        srow.grid_columnconfigure(0, weight=1)
        self.status = ctk.CTkLabel(srow, text="", anchor="w", justify="left", text_color=MUTED,
                                   font=ctk.CTkFont(size=12), wraplength=560)
        self.status.grid(row=0, column=0, sticky="w")
        ctk.CTkButton(srow, text="Open folder", width=90, height=26, corner_radius=8,
                      fg_color="transparent", hover_color=FIELD, text_color=MUTED,
                      border_width=1, border_color=BORDER, font=ctk.CTkFont(size=12),
                      command=self.open_folder).grid(row=0, column=1, sticky="e")

        # --- format card
        ctk.CTkLabel(root, text="Format", text_color=TEXT, anchor="w",
                     font=ctk.CTkFont(size=15, weight="bold")).grid(row=4, column=0, sticky="w",
                                                                    pady=(18, 6))
        card = ctk.CTkFrame(root, fg_color=CARD, corner_radius=14, border_width=1,
                            border_color=BORDER)
        card.grid(row=5, column=0, sticky="ew")
        card.grid_columnconfigure(5, weight=1)
        self.video_menus, self.audio_menus = [], []

        def radio(r, text, val):
            ctk.CTkRadioButton(card, text=text, value=val, variable=self.v_mode,
                               command=self.apply_mode, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                               text_color=TEXT, border_color=MUTED, width=100,
                               font=ctk.CTkFont(size=13, weight="bold")
                               ).grid(row=r, column=0, padx=(18, 10), pady=14, sticky="w")

        def menu(r, col, label, var, values, store):
            lbl = ctk.CTkLabel(card, text=label, text_color=MUTED, font=ctk.CTkFont(size=12))
            lbl.grid(row=r, column=col, padx=(10, 6), sticky="e")
            m = ctk.CTkOptionMenu(card, values=values, variable=var, width=150, height=32,
                                  corner_radius=8, fg_color=FIELD, button_color=FIELD,
                                  button_hover_color=GREY_BTN, text_color=TEXT,
                                  dropdown_fg_color=CARD, dropdown_text_color=TEXT,
                                  dropdown_hover_color=FIELD, font=ctk.CTkFont(size=13))
            m.grid(row=r, column=col + 1, padx=(0, 10), pady=14, sticky="w")
            store.append((lbl, m))

        radio(0, "VIDEO", "video")
        menu(0, 1, "Quality", self.v_quality, VIDEO_QUALITIES, self.video_menus)
        menu(0, 3, "Format", self.v_container, CONTAINERS, self.video_menus)
        sep = ctk.CTkFrame(card, height=1, fg_color=BORDER)
        sep.grid(row=1, column=0, columnspan=6, sticky="ew", padx=18)
        radio(2, "AUDIO", "audio")
        menu(2, 1, "Format", self.v_aformat, AUDIO_FORMATS, self.audio_menus)
        menu(2, 3, "Quality", self.v_aquality, AUDIO_QUALITIES, self.audio_menus)

        # --- advanced toggle
        self.adv_btn = ctk.CTkButton(root, text="ADVANCED OPTIONS  \u25BE", anchor="w", width=190,
                                     height=30, fg_color="transparent", hover_color=FIELD,
                                     text_color=TEXT, corner_radius=8,
                                     font=ctk.CTkFont(size=13, weight="bold"),
                                     command=self.toggle_advanced)
        self.adv_btn.grid(row=6, column=0, sticky="w", pady=(14, 0))

        self.adv = ctk.CTkFrame(root, fg_color=CARD, corner_radius=14, border_width=1,
                                border_color=BORDER)
        self.adv.grid_columnconfigure(0, weight=1)
        a = ctk.CTkFrame(self.adv, fg_color="transparent")
        a.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 4))

        def check(parent, text, var, r, col):
            ctk.CTkCheckBox(parent, text=text, variable=var, fg_color=ACCENT,
                            hover_color=ACCENT_HOVER, text_color=TEXT, border_color=MUTED,
                            checkbox_width=20, checkbox_height=20, corner_radius=5,
                            font=ctk.CTkFont(size=13)
                            ).grid(row=r, column=col, sticky="w", padx=(0, 22), pady=5)

        check(a, "Download whole playlist", self.v_playlist, 0, 0)
        check(a, "Embed thumbnail", self.v_thumb, 0, 1)
        check(a, "Embed metadata", self.v_meta, 0, 2)
        check(a, "Plays everywhere (H.264)", self.v_compat, 1, 0)
        check(a, "Subtitles", self.v_subs, 1, 1)
        langs = ctk.CTkFrame(a, fg_color="transparent")
        langs.grid(row=1, column=2, sticky="w")
        ctk.CTkLabel(langs, text="Languages", text_color=MUTED,
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 6))
        ctk.CTkEntry(langs, textvariable=self.v_langs, width=60, height=28, fg_color=FIELD,
                     border_width=0, text_color=TEXT).pack(side="left")

        b = ctk.CTkFrame(self.adv, fg_color="transparent")
        b.grid(row=1, column=0, sticky="ew", padx=18, pady=4)
        b.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(b, text="Use my browser login", text_color=MUTED,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkOptionMenu(b, values=BROWSERS, variable=self.v_cookies, width=110, height=28,
                          corner_radius=8, fg_color=FIELD, button_color=FIELD,
                          button_hover_color=GREY_BTN, text_color=TEXT, dropdown_fg_color=CARD,
                          dropdown_text_color=TEXT, dropdown_hover_color=FIELD
                          ).grid(row=0, column=1, padx=(0, 18))
        ctk.CTkLabel(b, text="Extra arguments", text_color=MUTED,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=(0, 8))
        ctk.CTkEntry(b, textvariable=self.v_extra, height=28, fg_color=FIELD, border_width=0,
                     text_color=TEXT).grid(row=0, column=3, sticky="ew")

        f = ctk.CTkFrame(self.adv, fg_color="transparent")
        f.grid(row=2, column=0, sticky="ew", padx=18, pady=4)
        f.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(f, text="Save folder", text_color=MUTED,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkEntry(f, textvariable=self.v_folder, height=28, fg_color=FIELD, border_width=0,
                     text_color=MUTED, state="readonly").grid(row=0, column=1, sticky="ew")
        ctk.CTkButton(f, text="Change...", width=90, height=28, corner_radius=8,
                      fg_color=GREY_BTN, hover_color=GREY_BTN_HOVER, text_color=TEXT,
                      font=ctk.CTkFont(size=12), command=self.change_folder
                      ).grid(row=0, column=2, padx=(8, 0))

        c2 = ctk.CTkFrame(self.adv, fg_color="transparent")
        c2.grid(row=3, column=0, sticky="ew", padx=18, pady=(6, 4))
        c2.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(c2, text="Details", text_color=MUTED,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(c2, text="Open tools folder", width=120, height=26, corner_radius=8,
                      fg_color=GREY_BTN, hover_color=GREY_BTN_HOVER, text_color=TEXT,
                      font=ctk.CTkFont(size=12), command=self.open_tools_folder
                      ).grid(row=0, column=1, sticky="e", padx=(0, 8))
        self.btn_update = ctk.CTkButton(c2, text="Check for updates", width=130, height=26,
                                        corner_radius=8, fg_color=GREY_BTN,
                                        hover_color=GREY_BTN_HOVER, text_color=TEXT,
                                        font=ctk.CTkFont(size=12), command=self.check_now)
        self.btn_update.grid(row=0, column=2, sticky="e")
        self.log = ctk.CTkTextbox(self.adv, height=120, corner_radius=8, fg_color=FIELD,
                                  text_color=TEXT, font=ctk.CTkFont(family="Consolas", size=11),
                                  wrap="word")
        self.log.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 16))
        self.log.configure(state="disabled")

        # --- footer
        foot = ctk.CTkFrame(root, fg_color="transparent")
        foot.grid(row=8, column=0, sticky="ew", pady=(12, 0))
        foot.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(foot, text=f"v{APP_VERSION}", text_color=MUTED,
                     font=ctk.CTkFont(size=11)).grid(row=0, column=0, sticky="w")
        if HAS_REPO:
            for i, (text, tpl) in enumerate((("Request a feature", "feature_request.md"),
                                             ("Report a problem", "bug_report.md"))):
                ctk.CTkButton(foot, text=text, width=110, height=22, corner_radius=6,
                              fg_color="transparent", hover_color=FIELD, text_color=MUTED,
                              font=ctk.CTkFont(size=11),
                              command=lambda t=tpl: webbrowser.open(
                                  f"https://github.com/{GITHUB_REPO}/issues/new?template={t}")
                              ).grid(row=0, column=1 + i, sticky="e")

    def bind_paste_menu(self, entry):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Paste", command=lambda: self.paste_into(entry))
        menu.add_command(label="Clear", command=lambda: entry.delete(0, "end"))
        entry.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

    def paste_into(self, entry):
        try:
            text = self.clipboard_get().strip()
        except tk.TclError:
            return
        entry.delete(0, "end")
        entry.insert(0, " ".join(text.split()))

    def fit_window(self):
        w = 780
        h = 794 if self.adv_open else 474
        self.geometry(f"{w}x{h}")

    # --------------------------------------------------------- behaviours
    def apply_mode(self):
        video = self.v_mode.get() == "video"
        for lbl, m in self.video_menus:
            m.configure(state="normal" if video else "disabled")
            lbl.configure(text_color=MUTED if video else ("#B5B5BD", "#55555C"))
        for lbl, m in self.audio_menus:
            m.configure(state="disabled" if video else "normal")
            lbl.configure(text_color=("#B5B5BD", "#55555C") if video else MUTED)

    def toggle_advanced(self):
        self.adv_open = not self.adv_open
        if self.adv_open:
            self.adv.grid(row=7, column=0, sticky="ew", pady=(8, 0))
            self.adv_btn.configure(text="ADVANCED OPTIONS  \u25B4")
        else:
            self.adv.grid_remove()
            self.adv_btn.configure(text="ADVANCED OPTIONS  \u25BE")
        self.fit_window()

    def toggle_theme(self):
        mode = "dark" if self.theme_switch.get() else "light"
        self.cfg["theme"] = mode
        ctk.set_appearance_mode(mode)

    def change_folder(self):
        d = filedialog.askdirectory(initialdir=self.save_dir, title="Choose where to save")
        if not d:
            return
        self.save_dir = os.path.normpath(d)
        self.v_folder.set(self.save_dir)
        if not self.running:
            self.set_idle_status()

    def open_folder(self):
        os.makedirs(self.save_dir, exist_ok=True)
        try:
            os.startfile(self.save_dir)
        except AttributeError:
            pass

    def set_status(self, text, kind="muted"):
        color = {"muted": MUTED, "ok": OK, "err": ERR, "text": TEXT}[kind]
        self.status.configure(text=text, text_color=color)

    def set_idle_status(self):
        self.set_status(f"Ready. Files will be saved to {self.save_dir}")

    def write_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def save_settings(self):
        data = {
            "theme": self.cfg["theme"], "mode": self.v_mode.get(), "quality": self.v_quality.get(),
            "container": self.v_container.get(), "audio_format": self.v_aformat.get(),
            "audio_quality": self.v_aquality.get(), "compat": self.v_compat.get(),
            "playlist": self.v_playlist.get(), "thumbnail": self.v_thumb.get(),
            "metadata": self.v_meta.get(), "subs": self.v_subs.get(),
            "sub_langs": self.v_langs.get(), "cookies": self.v_cookies.get(),
            "extra": self.v_extra.get(), "save_dir": self.save_dir,
        }
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def on_close(self):
        self.save_settings()
        if self.running:
            self.cancel()
        self.destroy()

    # ---------------------------------------------------- build command
    def build_cmd(self, url):
        playlist = self.v_playlist.get()
        template = ("%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s" if playlist
                    else "%(title)s.%(ext)s")
        cmd = [self.exe, "--newline", "--no-colors", "--ignore-errors",
               "-o", os.path.join(self.save_dir, template),
               "--yes-playlist" if playlist else "--no-playlist"]
        if self.ffmpeg_dir:
            cmd += ["--ffmpeg-location", self.ffmpeg_dir]

        audio = self.v_mode.get() == "audio"
        if audio:
            q = self.v_aquality.get()
            m = re.search(r"(\d+) kbps", q)
            cmd += ["-f", "ba/b", "-x", "--audio-format", self.v_aformat.get().lower(),
                    "--audio-quality", f"{m.group(1)}K" if m else "0"]
        else:
            container = self.v_container.get().lower()
            sort = []
            m = re.match(r"(?:4K \()?(\d+)p", self.v_quality.get())
            if m:
                sort.append(f"res:{m.group(1)}")
            if self.v_compat.get():
                sort += ["vcodec:h264", "acodec:aac"]
            if container == "mp4":
                sort.append("ext:mp4:m4a")
            cmd += ["-f", "bv*+ba/b"]
            if sort:
                cmd += ["-S", ",".join(sort)]
            cmd += ["--merge-output-format", container]

        if self.v_thumb.get():
            cmd.append("--embed-thumbnail")
        if self.v_meta.get():
            cmd.append("--embed-metadata")
        if self.v_subs.get() and not audio:
            cmd += ["--write-subs", "--write-auto-subs", "--sub-langs",
                    self.v_langs.get().strip() or "en", "--embed-subs"]
        if self.v_cookies.get() != "None":
            cmd += ["--cookies-from-browser", self.v_cookies.get().lower()]
        extra = self.v_extra.get().strip()
        if extra:
            try:
                cmd += [x.strip('"') for x in shlex.split(extra, posix=False)]
            except ValueError:
                pass
        cmd.append(url)
        return cmd

    # ------------------------------------------------------- run / worker
    def on_download_click(self):
        if self.running:
            self.cancel()
            return
        if not self.exe or not self.ffmpeg_dir:
            self.refresh_tools()
            self.offer_setup(then=None)
            return
        urls = self.url.get().split()
        if not urls:
            self.set_status("Paste a video link first.", "err")
            self.url.focus()
            return
        try:
            os.makedirs(self.save_dir, exist_ok=True)
        except OSError:
            self.set_status("Can't use that folder. Pick another one with Save To.", "err")
            return
        self.save_settings()
        self.run_commands([(u, self.build_cmd(u)) for u in urls], is_download=True)

    def run_commands(self, cmds, is_download):
        self.running = True
        self.cancelled = False
        self.last_error = ""
        self.progress.set(0)
        self.set_status("Starting...", "text")
        self.btn_dl.configure(text="Cancel", fg_color=GREY_BTN, hover_color=GREY_BTN_HOVER,
                              text_color=TEXT)
        threading.Thread(target=self.worker, args=(cmds, is_download), daemon=True).start()

    def worker(self, cmds, is_download):
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        env["PATH"] = os.pathsep.join([TOOLS_DIR, APP_DIR, env.get("PATH", "")])
        failures = 0
        total = len(cmds)
        prefix = ""
        for i, (label, cmd) in enumerate(cmds, 1):
            if self.cancelled:
                break
            prefix = f"Video {i} of {total}: " if total > 1 else ""
            self.q.put(("log", f"\n=== {label} ==="))
            self.q.put(("log", "> " + subprocess.list2cmdline(cmd)))
            self.q.put(("reset", None))
            self.q.put(("status", prefix + "Getting video info..."))
            passes_done, passes_expected = 0, 1
            try:
                self.proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    encoding="utf-8", errors="replace", creationflags=NO_WINDOW, env=env,
                    cwd=APP_DIR)
                for line in self.proc.stdout:
                    line = line.rstrip()
                    if not line:
                        continue
                    fm = FORMATS_RE.search(line)
                    if fm:
                        passes_expected = fm.group(1).count("+") + 1
                    if line.startswith("[download] Destination:"):
                        passes_done = passes_done + 1 if passes_done < passes_expected else passes_done
                    m = PCT_RE.search(line)
                    if m:
                        pct = float(m.group(1))
                        frac = (max(passes_done, 1) - 1 + pct / 100) / passes_expected
                        extra = ""
                        sp, eta = SPEED_RE.search(line), ETA_RE.search(line)
                        if sp:
                            extra += f"  \u2022  {sp.group(1)}"
                        if eta:
                            extra += f"  \u2022  {eta.group(1)} left"
                        self.q.put(("progress", min(frac, 1.0)))
                        self.q.put(("status", f"{prefix}Downloading {int(frac * 100)}%{extra}"))
                        continue
                    if "[Merger]" in line:
                        self.q.put(("status", prefix + "Merging video and audio..."))
                    elif "[ExtractAudio]" in line:
                        self.q.put(("status", prefix + "Converting audio..."))
                    elif "[EmbedThumbnail]" in line or "[Metadata]" in line:
                        self.q.put(("status", prefix + "Finishing up..."))
                    if line.startswith("ERROR"):
                        self.q.put(("error", line))
                    self.q.put(("log", line))
                rc = self.proc.wait()
                if rc != 0 and not self.cancelled:
                    failures += 1
            except Exception as e:
                failures += 1
                self.q.put(("error", f"ERROR: {e}"))
        self.q.put(("done", (failures, is_download)))

    def cancel(self):
        self.cancelled = True
        if self.proc and self.proc.poll() is None:
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.proc.pid)],
                               creationflags=NO_WINDOW, capture_output=True)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass

    def poll_queue(self):
        try:
            while True:
                kind, data = self.q.get_nowait()
                if kind == "log":
                    self.write_log(data)
                elif kind == "reset":
                    self.progress.set(0)
                elif kind == "progress":
                    self.progress.set(data)
                elif kind == "status":
                    self.set_status(data, "text")
                elif kind == "call":
                    data()
                elif kind == "error":
                    self.last_error = data
                elif kind == "done":
                    failures, is_download = data
                    self.running = False
                    self.btn_dl.configure(text="Download", fg_color=ACCENT,
                                          hover_color=ACCENT_HOVER, text_color="#FFFFFF")
                    if self.cancelled:
                        self.set_status("Cancelled.")
                        self.progress.set(0)
                    elif failures:
                        msg = friendly_error(self.last_error) if self.last_error else \
                            "Something went wrong. Open Advanced options to see the details."
                        self.set_status(msg, "err")
                    else:
                        self.progress.set(1)
                        self.set_status("All done!" if is_download else "yt-dlp is up to date.",
                                        "ok")
        except queue.Empty:
            pass
        self.after(100, self.poll_queue)


if __name__ == "__main__":
    ctk.set_default_color_theme("blue")
    App().mainloop()
