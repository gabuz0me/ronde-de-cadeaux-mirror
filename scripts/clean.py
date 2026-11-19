"""Python pour la portabilité Gnunux/Windows."""

import shutil
from pathlib import Path

if __name__ == "__main__":
    working_dir = Path(__file__).parent.parent
    shutil.rmtree(working_dir / "dist/", ignore_errors=True)
    for compiled in (working_dir / "ronde_de_cadeaux").glob("**/*.mo"):
        compiled.unlink()
    print("Cleaned!")
