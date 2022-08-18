"""Submission for BGGP3 test script"""
from pathlib import Path
from re import search as rsearch
from subprocess import run
from tempfile import NamedTemporaryFile

name = NamedTemporaryFile(suffix="bggp3.crash.c").name
Path(name).write_text("int main(){}", "utf-8")

version = run(["clang", "--version"], check=True, capture_output=True).stdout

assert (
    rsearch(rb"15.0.0", version) is not None
), "This crash only works on clang 15.0.0! Visit https://apt.llvm.org/ to get it."

CMD = [
    "clang",
    "-target",
    "i386-apple-windows-eabi",
    # Uncomment this flag to be able to remove `int ` from the source code
    # "-Wno-implicit-int",
    name,
]

run(CMD, check=True, shell=False)
