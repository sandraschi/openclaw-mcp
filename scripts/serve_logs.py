"""Run the log server (python -m openclaw_mcp.serve_logs)."""
import sys
from pathlib import Path

# Add src so openclaw_mcp is importable when run as scripts/serve_logs.py
root = Path(__file__).resolve().parent.parent
if str(root / "src") not in sys.path:
    sys.path.insert(0, str(root / "src"))

from openclaw_mcp.serve_logs import main  # noqa: E402

if __name__ == "__main__":
    main()
