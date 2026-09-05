cmake_minimum_required(VERSION 3.20)
project(burnout3_recomp C)

# Burnout 3: Takedown - Static Recompilation
# Builds all compatibility layers and the recompiled game executable

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Common definitions
add_compile_definitions(
    WIN32_LEAN_AND_MEAN
    NOMINMAX
)

# MinGW's CRT wrappers for the *_s "secure" string functions (swprintf_s,
# etc.) are gated behind a CRT-version feature test that isn't satisfied by
# default. Bump it so code written against the MSVC secure CRT API compiles
# unchanged under MinGW too.
# 0xE00 (14.00) is the lowest value that also keeps mingw's own _UCRT
# auto-detection happy (see _mingw.h: _UCRT is auto-defined when
# __MSVCRT_VERSION__ >= 0xE00 && < 0x1000, or >= 0x1400) - a lower value
# like 0x0700 disables _UCRT and breaks <cstdlib>'s quick_exit/at_quick_exit.
if(MINGW)
    add_compile_definitions(__MSVCRT_VERSION__=0xE00)
endif()

# ── Compatibility layers (static libraries) ──────────────────

# Xbox kernel replacement (147 imports → Win32)
add_subdirectory(src/kernel)

# D3D8 → D3D11 graphics abstraction
add_subdirectory(src/d3d)

# DirectSound → XAudio2 audio abstraction
add_subdirectory(src/audio)

# Xbox input → XInput controller abstraction
add_subdirectory(src/input)

# NV2A GPU emulation (extracted from xemu)
# Note: nv2a is compiled as part of src/game, no separate CMakeLists

# MCPX APU audio emulation (extracted from xemu)
add_subdirectory(src/apu)

# ── Recompiled game executable ─────────────────────────────────
add_subdirectory(src/game)
