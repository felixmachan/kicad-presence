import re
import time

import psutil
from pypresence import Presence
import win32gui
import win32process

# ------------------- CONFIG -------------------
DISCORD_CLIENT_ID = "1473099831051423887"
POLL_SECONDS = 2
DEBUG = True

# Discord Developer Portal -> Rich Presence -> Art Assets keys
SMALL_IMAGE = "kicad_small"
LARGE_PCB_IMAGE = "pcb_editor"
LARGE_SCH_IMAGE = "schematic_editor"
LARGE_PM_IMAGE = "pcb_editor"
# ---------------------------------------------

TARGET_PROCS = {
    "kicad.exe",
    "pcbnew.exe",
    "eeschema.exe",
    "kicad-pcbnew.exe",
    "kicad-eeschema.exe",
}

FILE_REGEX = re.compile(r"([A-Za-z0-9_\- .()]+)\.(kicad_pcb|kicad_sch|sch)\b", re.IGNORECASE)
DASH_SPLIT_REGEX = re.compile(r"\s+[\u2012-\u2015-]\s+")
EDITOR_SUFFIX_REGEX = re.compile(r"\s*[\u2012-\u2015-]\s*(PCB Editor|Schematic Editor)\s*$", re.IGNORECASE)


def connect_discord(client_id: str) -> Presence:
    last_err = None
    for pipe in range(0, 10):
        try:
            rpc = Presence(client_id, pipe=pipe)
            rpc.connect()
            return rpc
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Could not connect to Discord RPC (pipes 0-9). Is Discord running? ({last_err})")


def any_kicad_running() -> bool:
    for p in psutil.process_iter(["name"]):
        try:
            name = (p.info["name"] or "").lower()
            if name in TARGET_PROCS:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def get_foreground_kicad_window():
    """
    Return (title, proc_name_lower) if the currently focused window belongs to KiCad.
    Otherwise return (None, None).
    """
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None, None

    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        title = (win32gui.GetWindowText(hwnd) or "").strip()
    except Exception:
        return None, None

    try:
        proc_name = (psutil.Process(pid).name() or "").lower()
    except Exception:
        return None, None

    if proc_name not in TARGET_PROCS:
        return None, None

    return title, proc_name


def sanitize_file_label(value: str | None) -> str | None:
    if not value:
        return None

    cleaned = EDITOR_SUFFIX_REGEX.sub("", value).strip()
    return cleaned or None


def pick_editor_and_file_from_title(title: str, proc_name: str | None = None):
    tl = (title or "").lower()
    proc = (proc_name or "").lower()

    is_pcb = (".kicad_pcb" in tl) or ("pcb editor" in tl) or ("pcbnew" in tl) or (proc in {"pcbnew.exe", "kicad-pcbnew.exe"})
    is_sch = (
        (".kicad_sch" in tl)
        or (re.search(r"\.sch\b", tl) is not None)
        or ("schematic editor" in tl)
        or ("eeschema" in tl)
        or (proc in {"eeschema.exe", "kicad-eeschema.exe"})
    )

    if is_pcb and not is_sch:
        editor_label = "PCB Editor"
        large_image = LARGE_PCB_IMAGE
    elif is_sch and not is_pcb:
        editor_label = "Schematic Editor"
        large_image = LARGE_SCH_IMAGE
    else:
        editor_label = "KiCad"
        large_image = LARGE_PM_IMAGE

    file_or_project = None
    m = FILE_REGEX.search(title or "")
    if m:
        file_or_project = f"{m.group(1)}.{m.group(2)}"
    else:
        chunks = DASH_SPLIT_REGEX.split(title or "")
        if chunks and chunks[0].strip():
            candidate = chunks[0].strip()
            if len(candidate) <= 80:
                file_or_project = candidate

    file_or_project = sanitize_file_label(file_or_project)
    return editor_label, large_image, file_or_project


def main():
    rpc = connect_discord(DISCORD_CLIENT_ID)

    session_start = None
    last_payload = None
    last_update_ts = 0.0

    while True:
        if not any_kicad_running():
            session_start = None
            if last_payload is not None:
                try:
                    rpc.clear()
                except Exception:
                    pass
                last_payload = None
            time.sleep(POLL_SECONDS)
            continue

        if session_start is None:
            session_start = int(time.time())

        title, proc_name = get_foreground_kicad_window()

        if title is None:
            editor_label, large_image, file_or_project = "KiCad", LARGE_PM_IMAGE, None
        else:
            editor_label, large_image, file_or_project = pick_editor_and_file_from_title(title, proc_name)

        details = "Cooking..."
        if file_or_project:
            state = f"Editing: {file_or_project}"
            if editor_label.lower() not in state.lower():
                state += f" - {editor_label}"
        else:
            if editor_label == "KiCad":
                details = None
                state = "Idling..."
            else:
                state = f"Editing... - {editor_label}"

        payload = (details, state, large_image, editor_label)

        now = time.time()
        should_update = (payload != last_payload) or (now - last_update_ts > 20)

        if should_update:
            try:
                update_kwargs = {
                    "state": state,
                    "large_image": large_image,
                    "large_text": editor_label,
                    "small_image": SMALL_IMAGE,
                    "small_text": "KiCad Presence",
                    "start": session_start,
                }
                if details is not None:
                    update_kwargs["details"] = details
                rpc.update(**update_kwargs)
                last_payload = payload
                last_update_ts = now
            except Exception:
                try:
                    rpc = connect_discord(DISCORD_CLIENT_ID)
                except Exception:
                    pass

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
