"""
Utilities to check for valid triples for clang
"""

from asyncio import (
    FIRST_COMPLETED,
    StreamReader,
    create_subprocess_exec,
    create_task,
    gather,
    get_event_loop,
    wait,
)
from asyncio.subprocess import PIPE
from enum import Enum
from itertools import product
from os import unlink
from pathlib import Path
from typing import AsyncGenerator, Tuple
from uuid import uuid1


class ClangArch(str, Enum):
    """
    Architecture options for clang as of LLVM 15.0.0

    The "original list" of these options is
    [here](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Support/Triple.cpp),
    """

    i386 = "i386"
    i486 = "i486"
    i586 = "i586"
    i686 = "i686"
    i786 = "i786"
    i886 = "i886"
    i986 = "i986"
    amd64 = "amd64"
    x86_64 = "x86_64"
    x86_64h = "x86_64h"
    powerpc = "powerpc"
    powerpcspe = "powerpcspe"
    ppc = "ppc"
    ppc32 = "ppc32"
    powerpcle = "powerpcle"
    ppcle = "ppcle"
    ppc32le = "ppc32le"
    powerpc64 = "powerpc64"
    ppu = "ppu"
    ppc64 = "ppc64"
    powerpc64le = "powerpc64le"
    ppc64le = "ppc64le"
    xscale = "xscale"
    xscaleeb = "xscaleeb"
    aarch64 = "aarch64"
    aarch64_be = "aarch64_be"
    aarch64_32 = "aarch64_32"
    arc = "arc"
    arm64 = "arm64"
    arm64_32 = "arm64_32"
    arm64e = "arm64e"
    arm = "arm"
    armeb = "armeb"
    thumb = "thumb"
    thumbeb = "thumbeb"
    avr = "avr"
    m68k = "m68k"
    msp430 = "msp430"
    mips = "mips"
    mipseb = "mipseb"
    mipsallegrex = "mipsallegrex"
    mipsisa32r6 = "mipsisa32r6"
    mipsr6 = "mipsr6"
    mipsel = "mipsel"
    mipsallegrexel = "mipsallegrexel"
    mipsisa32r6el = "mipsisa32r6el"
    mipsr6el = "mipsr6el,"
    mips64 = "mips64"
    mips64eb = "mips64eb"
    mipsn32 = "mipsn32"
    mipsisa64r6 = "mipsisa64r6,"
    mips64r6 = "mips64r6"
    mipsn32r6 = "mipsn32r6"
    mips64el = "mips64el"
    mipsn32el = "mipsn32el"
    mipsisa64r6el = "mipsisa64r6el"
    mips64r6el = "mips64r6el,"
    mipsn32r6el = "mipsn32r6el"
    r600 = "r600"
    amdgcn = "amdgcn"
    riscv32 = "riscv32"
    riscv64 = "riscv64"
    hexagon = "hexagon"
    s390x = "s390x"
    systemz = "systemz"
    sparc = "sparc"
    sparcel = "sparcel"
    sparcv9 = "sparcv9"
    sparc64 = "sparc64"
    tce = "tce"
    tcele = "tcele"
    xcore = "xcore"
    nvptx = "nvptx"
    nvptx64 = "nvptx64"
    le32 = "le32"
    le64 = "le64"
    amdil = "amdil"
    amdil64 = "amdil64"
    hsail = "hsail"
    hsail64 = "hsail64"
    spir = "spir"
    spir64 = "spir64"
    spirv32 = "spirv32"
    spirv32v1_0 = "spirv32v1.0"
    spirv32v1_1 = "spirv32v1.1"
    spirv32v1_2 = "spirv32v1.2,"
    spirv32v1_3 = "spirv32v1.3"
    spirv32v1_4 = "spirv32v1.4"
    spirv32v1_5 = "spirv32v1.5"
    spirv64 = "spirv64"
    spirv64v1_0 = "spirv64v1.0"
    spirv64v1_1 = "spirv64v1.1"
    spirv64v1_2 = "spirv64v1.2,"
    spirv64v1_3 = "spirv64v1.3"
    spirv64v1_4 = "spirv64v1.4"
    spirv64v1_5 = "spirv64v1.5"
    lanai = "lanai"
    renderscript32 = "renderscript32"
    renderscript64 = "renderscript64"
    shave = "shave"
    ve = "ve"
    wasm32 = "wasm32"
    wasm64 = "wasm64"
    csky = "csky"
    loongarch32 = "loongarch32"
    loongarch64 = "loongarch64"
    dxil = "dxil"
    NONE = ""


class ClangVendor(str, Enum):
    """
    Vendor options for clang as of LLVM 15.0.0

    The "original list" of these options is
    [here](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Support/Triple.cpp),
    """

    apple = "apple"
    pc = "pc"
    scei = "scei"
    sie = "sie"
    fsl = "fsl"
    ibm = "ibm"
    img = "img"
    mti = "mti"
    nvidia = "nvidia"
    csr = "csr"
    myriad = "myriad"
    amd = "amd"
    mesa = "mesa"
    suse = "suse"
    oe = "oe"
    NONE = ""


class ClangOS(str, Enum):
    """
    OS options for clang as of LLVM 15.0.0

    The "original list" of these options is
    [here](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Support/Triple.cpp),
    """

    ananas = "ananas"
    cloudabi = "cloudabi"
    darwin = "darwin"
    dragonfly = "dragonfly"
    freebsd = "freebsd"
    fuchsia = "fuchsia"
    ios = "ios"
    kfreebsd = "kfreebsd"
    linux = "linux"
    lv2 = "lv2"
    macos = "macos"
    netbsd = "netbsd"
    openbsd = "openbsd"
    solaris = "solaris"
    win32 = "win32"
    windows = "windows"
    zos = "zos"
    haiku = "haiku"
    minix = "minix"
    rtems = "rtems"
    nacl = "nacl"
    aix = "aix"
    cuda = "cuda"
    nvcl = "nvcl"
    amdhsa = "amdhsa"
    ps4 = "ps4"
    ps5 = "ps5"
    elfiamcu = "elfiamcu"
    tvos = "tvos"
    watchos = "watchos"
    driverkit = "driverkit"
    mesa3d = "mesa3d"
    contiki = "contiki"
    amdpal = "amdpal"
    hermit = "hermit"
    hurd = "hurd"
    wasi = "wasi"
    emscripten = "emscripten"
    shadermodel = "shadermodel"
    NONE = ""


class ClangEnvironment(str, Enum):
    """
    Environment options for clang as of LLVM 15.0.0

    The "original list" of these options is
    [here](https://github.com/llvm/llvm-project/blob/main/llvm/lib/Support/Triple.cpp),
    """

    eabihf = "eabihf"
    eabi = "eabi"
    gnuabin32 = "gnuabin32"
    gnuabi64 = "gnuabi64"
    gnueabihf = "gnueabihf"
    gnueabi = "gnueabi"
    gnux32 = "gnux32"
    gnu_ilp32 = "gnu_ilp32"
    code16 = "code16"
    gnu = "gnu"
    android = "android"
    musleabihf = "musleabihf"
    musleabi = "musleabi"
    muslx32 = "muslx32"
    musl = "musl"
    msvc = "msvc"
    itanium = "itanium"
    cygnus = "cygnus"
    coreclr = "coreclr"
    simulator = "simulator"
    macabi = "macabi"
    pixel = "pixel"
    vertex = "vertex"
    geometry = "geometry"
    hull = "hull"
    domain = "domain"
    compute = "compute"
    library = "library"
    raygeneration = "raygeneration"
    intersection = "intersection"
    anyhit = "anyhit"
    closesthit = "closesthit"
    miss = "miss"
    callable = "callable"
    mesh = "mesh"
    amplification = "amplification"
    NONE = ""


async def check_valid_triple(triple: str, input_file: str) -> Tuple[bool, str]:
    """
    Check if a triple is valid
    """

    cmd = [
        "/home/novafacing/hub/llvm-project/llvm/build/bin/clang",
        "-target",
        triple,
        "-x",
        "c",
        "-o",
        "/dev/null",
        input_file,
    ]

    res = await create_subprocess_exec(
        *cmd,
        stdout=PIPE,
        stderr=PIPE,
    )

    async def read_stream(stream: StreamReader) -> bytes:
        out = b""
        while True:
            data = await stream.read(1024)
            if not data:
                break
            out += data
        return out

    out, err = await gather(
        read_stream(res.stdout),
        read_stream(res.stderr),
    )

    if b"PLEASE" in out or b"PLEASE" in err:
        return False, out + err

    return res.returncode == 0, ""


async def generate_triples() -> AsyncGenerator[str, None]:
    """
    Generate target triples, some of which may not be valid
    """
    oses = list(map(lambda x: x.value, ClangOS))
    archs = list(map(lambda x: x.value, ClangArch))
    vendors = list(map(lambda x: x.value, ClangVendor))
    envs = list(map(lambda x: x.value, ClangEnvironment))

    for arch, vendor, op_s, environ in product(archs, vendors, oses, envs):
        triple = ""
        if arch:
            triple += arch

        if vendor:
            triple += ("-" if triple else "") + vendor

        if op_s:
            triple += ("-" if triple else "") + op_s

        if environ:
            triple += ("-" if triple else "") + environ

        yield triple


async def main() -> None:
    """
    Run the script!
    """
    tempfile = Path(f"/dev/shm/test/{uuid1()}.c")
    tempfile.write_text("int main(){return 1;}")

    async def check_triple(triple: str, i: int) -> None:
        """
        Check a triple and dump out its stack trace if it has one
        """
        _valid, err = await check_valid_triple(triple, str(tempfile))

        if err:
            print(f"Error checking triple (#{i}) `{triple}`:")
            print(err)

    tasks = set()
    i = 0
    l = 1
    TASK_COUNT = 32

    async for triple in generate_triples():

        while len(tasks) >= TASK_COUNT:
            done, tasks = await wait(tasks, return_when=FIRST_COMPLETED)

            for task in done:
                await task
                i += 1
                if i / l > 1.1:
                    print(f"Done: {i}")
                    l = i

        task = create_task(check_triple(triple, i))
        task.add_done_callback(tasks.discard)
        tasks.add(task)

    await wait(tasks)

    unlink(tempfile.name)


if __name__ == "__main__":
    get_event_loop().run_until_complete(main())
