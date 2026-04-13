import sys
from pathlib import Path

_here = str(Path(__file__).parent)
sys.path.insert(0, _here)
sys.modules.pop("exercises", None)
