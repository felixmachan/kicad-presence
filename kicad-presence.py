import re
import time
import psutil
from pypresence import Presence

import win32gui
import win32process

DISCORD_CLIENT_ID = "1473099831051423887"
POLL_SECONDS = 3
LARGE_IMAGE = "kicad"

TARGET_PROCS = {
    "kicad.exe": "Project Manager",
    "pcbnew.exe": "PCB Editor",
    "eeschema.exe": "Schematic Editor",
    "kicad-pcbnew.exe": "PCB Editor",
    "kicad-eeschema.exe": "Schematic Editor",
}

FILE_REGEX = re.compile(r"([A-Za-z0-9_\- .()]+)\.(kicad_pcb|kicad_sch|sch)\b", re.IGNORECASE)

def find_kicad_like_process():
    procs = []
    for p in psutil.process_iter(["name", "pid"]):
        try:
            name = (p.info["name"] or "").lower()
            if name in TARGET_PROCS:
                procs.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not procs:
        return None, None

    priority = {"pcbnew.exe": 3, "kicad-pcbnew.exe": 3, "eeschema.exe": 2, "kicad-eeschema.exe": 2, "kicad.exe": 1}
    procs.sort(key=lambda p: priority.get((p.name() or "").lower(), 0), reverse=True)
    chosen = procs[0]
    kind = TARGET_PROCS.get((chosen.name() or "").lower(), "KiCad")
    return chosen, kind

def get_window_titles_for_pid(pid: int):
    titles = []

    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        try:
            _, wpid = win32process.GetWindowThreadProcessId(hwnd)
            if wpid != pid:
                return
            title = win32gui.GetWindowText(hwnd)
            if title and title.strip():
                titles.append(title.strip())
        except Exception:
            return

    win32gui.EnumWindows(enum_handler, None)
    return titles

def pick_best_title(titles):
    if not titles:
        return None
    for t in titles:
        tl = t.lower()
        if ".kicad_pcb" in tl or ".kicad_sch" in tl or re.search(r"\.sch\b", tl):
            return t
    return max(titles, key=len)

def parse_file_and_mode(title: str, fallback_kind: str):
    mode = fallback_kind
    file_or_project = None

    if title:
        tl = title.lower()
        if "pcb" in tl or ".kicad_pcb" in tl:
            mode = "PCB Editor"
        elif "schematic" in tl or "eeschema" in tl or ".kicad_sch" in tl or re.search(r"\.sch\b", tl):
            mode = "Schematic Editor"

        m = FILE_REGEX.search(title)
        if m:
            file_or_project = f"{m.group(1)}.{m.group(2)}"
        else:
            chunks = re.split(r"\s+-\s+", title)
            if chunks and chunks[0].strip():
                file_or_project = chunks[0].strip()

    return mode, file_or_project

def main():
    print("[INFO] Connecting to Discord RPC...")
    rpc = Presence(DISCORD_CLIENT_ID)
    rpc.connect()
    print("[OK] Connected.")

    session_start = None
    last_payload_key = None

    while True:
        proc, kind = find_kicad_like_process()

        if not proc:
            if last_payload_key is not None:
                print("[INFO] KiCad not found -> clearing presence")
                rpc.clear()
                last_payload_key = None
            else:
                print("[WAIT] KiCad not found...")
            session_start = None
            time.sleep(POLL_SECONDS)
            continue

        if session_start is None:
            session_start = int(time.time())
            print(f"[INFO] Found KiCad process: {proc.name()} (pid={proc.pid})")

        titles = get_window_titles_for_pid(proc.pid)
        title = pick_best_title(titles)
        print(f"[DEBUG] Window title: {title}")

        mode, file_or_project = parse_file_and_mode(title, kind)

        details = f"KiCad — {mode}"
        state = f"Editing: {file_or_project}" if file_or_project else "Editing…"

        payload_key = (details, state)
        if payload_key != last_payload_key:
            print(f"[UPDATE] {details} | {state}")
            rpc.update(
                details=details,
                state=state,
                large_image=LARGE_IMAGE,
                large_text="KiCad",
                start=session_start,
            )
            last_payload_key = payload_key

        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()
