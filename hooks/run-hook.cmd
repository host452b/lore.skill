: << 'CMDBLOCK'
@echo off
REM Cross-platform polyglot wrapper for hook scripts.
REM On Windows: cmd.exe runs the batch portion, which finds and calls bash.
REM On Unix: the shell interprets this as a script.
REM Hook scripts use extensionless filenames so Claude Code's Windows
REM auto-detection doesn't interfere.
REM Usage: run-hook.cmd <script-name> [args...]

if "%~1"=="" (
    echo run-hook.cmd: missing script name >&2
    exit /b 1
)

set "HOOK_DIR=%~dp0"

if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)
if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    "C:\Program Files (x86)\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

where bash >nul 2>nul
if %ERRORLEVEL% equ 0 (
    bash "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

REM No bash found on Windows - cannot run hook.
REM The plugin still "works" but SessionStart context injection is skipped.
echo run-hook.cmd: no bash available on PATH or in standard Git install locations >&2
echo run-hook.cmd: SessionStart hook cannot run; install Git for Windows to enable >&2
exit /b 1
CMDBLOCK

# Unix bash path
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "run-hook.cmd: missing script name" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_NAME="$1"
shift

exec bash "${SCRIPT_DIR}/${HOOK_NAME}" "$@"
