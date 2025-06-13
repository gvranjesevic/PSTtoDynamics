; NSIS Installer Script for PSTtoDynamics

!define APPNAME "PSTtoDynamics"
!define EXENAME "main_window.exe"
!define COMPANY "Dynamique Solutions"
!define DESCRIPTION "PST to Dynamics 365 - Professional Email Import and Sync"
!define VERSION "1.0.0"

; Installer output
OutFile "${APPNAME}_Setup.exe"
InstallDir "$PROGRAMFILES64\${APPNAME}"
ShowInstDetails show
ShowUnInstDetails show

; Default icon (replace with real icon later)
Icon "gui/resources/app_icon.ico"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File "dist\${EXENAME}"
    ; Bundle resources
    File /r "dist\gui\themes"
    File /r "dist\gui\resources"
    ; Create shortcuts
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${EXENAME}"
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${EXENAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\${EXENAME}"
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
    RMDir /r "$INSTDIR\gui"
    RMDir "$SMPROGRAMS\${APPNAME}"
    RMDir "$INSTDIR"
SectionEnd

; Uninstaller
WriteUninstaller "$INSTDIR\Uninstall.exe" 