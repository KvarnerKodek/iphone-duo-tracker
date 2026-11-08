import sys
from datetime import datetime, timezone
from pathlib import Path

from .render import render_page
from .stock import load_retailers

out = Path(sys.argv[2] if len(sys.argv) > 2 else "site")
out.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
(out / "index.html").write_text(render_page(load_retailers(sys.argv[1]), now))
