"""Capture the real Tk Helix-Lock main screen and compact API queue window."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import ImageGrab

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from helix_lock_app import HelixLockApp


def capture(window, output: Path, label: str):
    window.update_idletasks()
    window.update()
    x, y = window.winfo_rootx(), window.winfo_rooty()
    width, height = window.winfo_width(), window.winfo_height()
    image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(f"Captured {label}: {output} ({width}x{height})")


def main():
    output = Path(sys.argv[1])
    app = HelixLockApp()
    app.geometry("960x750+100+60")
    app.update_idletasks()
    app.update()
    assert app.tabs.select() == str(app.file_tab), "File & key must be first"
    app.after(800, app.quit)
    app.mainloop()
    capture(app, output, "Helix-Lock main window")

    if len(sys.argv) > 2:
        api_output = Path(sys.argv[2])
        app._open_api_window()
        capture(app.api_window, api_output, "Helix-Lock compact API queue")

    app.destroy()


if __name__ == "__main__":
    main()
