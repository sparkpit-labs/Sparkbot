!include "LogicLib.nsh"
!include "FileFunc.nsh"

; Check the exact installed executables, not unrelated processes with the same
; name. Opening for write without writing detects running image/file locks.
!macro SPARKBOT_REQUIRE_UNLOCKED NAME
  ${If} ${FileExists} "$INSTDIR\${NAME}"
    System::Call 'kernel32::CreateFileW(w "$INSTDIR\${NAME}", i 0x40000000, i 0, p 0, i 3, i 0, p 0) p .r0'
    ${If} $0 == -1
      IfSilent +2
      MessageBox MB_OK|MB_ICONEXCLAMATION "Cannot change ${NAME}. Close Sparkbot and all connector login/runner terminals, then try again. No files will be changed by this step."
      SetErrorLevel 2
      Abort
    ${EndIf}
    System::Call 'kernel32::CloseHandle(p r0)'
  ${EndIf}
!macroend

!macro SPARKBOT_REQUIRE_STOPPED
  !insertmacro SPARKBOT_REQUIRE_UNLOCKED "sparkbot-roundtable.exe"
  !insertmacro SPARKBOT_REQUIRE_UNLOCKED "sparkbot-server.exe"
  !insertmacro SPARKBOT_REQUIRE_UNLOCKED "sparkbot-roundtable-desktop.exe"
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro SPARKBOT_REQUIRE_STOPPED
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro SPARKBOT_REQUIRE_STOPPED
!macroend
