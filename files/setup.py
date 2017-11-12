import sys
from cx_Freeze import setup, Executable



setup(
    name="shroud",
    version="0.1",
    description="test",
    executables=[Executable("Shroud.py")])
