"""Capture the real Tk Helix-Lock main screen in a virtual X display."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import ImageGrab

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from helix_lock_app import HelixLockApp


def main():
    output = Path(sys.argv[1])
    app = HelixLockApp()
    app.geometry("960x750+100+60")
    app.update_idletasks()
    app.update()
    assert app.tabs.select() == str(app.file_tab), "File & key must be first"
    app.after(800, app.quit)
    app.mainloop()
    app.update_idletasks()
    x, y = app.winfo_rootx(), app.winfo_rooty()
    width, height = app.winfo_width(), app.winfo_height()
    image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    print(f"Captured real Helix-Lock window: {output} ({width}x{height})")
    app.destroy()


if __name__ == "__main__":
    main()
