' ==============================================================================
' Universal Clipboard - 1-Click Desktop Launcher for Windows 10/11
' Starts Python server in completely hidden background and opens standalone app window
' ==============================================================================
Option Explicit

Dim WshShell, FSO, scriptDir, http, serverRunning
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' 1. Set working directory to the script's home folder
scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

' 2. Check if the server is already active on port 7890
serverRunning = False
On Error Resume Next
Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
If http Is Nothing Then Set http = CreateObject("MSXML2.ServerXMLHTTP")
If Not http Is Nothing Then
    http.Open "GET", "http://127.0.0.1:7890/api/status", False
    http.setTimeouts 500, 500, 500, 500
    http.Send
    If http.Status = 200 Then
        serverRunning = True
    End If
End If
On Error GoTo 0

' 3. Start Python background daemon if not already running (WindowStyle 0 = Hidden)
If Not serverRunning Then
    Dim pythonCmd
    pythonCmd = "cmd /c ""cd /d """ & scriptDir & """ && (start """" /b pythonw server.py 7890 || start """" /b python server.py 7890)"""
    WshShell.Run pythonCmd, 0, False
    WScript.Sleep 1500
End If

' 4. Find browser supporting standalone --app mode
Dim appUrl, browserExe, browserArgs
appUrl = "http://localhost:7890"
browserArgs = " --app=" & appUrl & " --window-size=1280,850"

Dim candidates(5)
candidates(0) = WshShell.ExpandEnvironmentStrings("%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe")
candidates(1) = WshShell.ExpandEnvironmentStrings("%ProgramFiles%\Microsoft\Edge\Application\msedge.exe")
candidates(2) = WshShell.ExpandEnvironmentStrings("%ProgramFiles%\Google\Chrome\Application\chrome.exe")
candidates(3) = WshShell.ExpandEnvironmentStrings("%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe")
candidates(4) = WshShell.ExpandEnvironmentStrings("%LocalAppData%\Google\Chrome\Application\chrome.exe")
candidates(5) = WshShell.ExpandEnvironmentStrings("%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe")

browserExe = ""
Dim i
For i = 0 To UBound(candidates)
    If candidates(i) <> "" Then
        If FSO.FileExists(candidates(i)) Then
            browserExe = candidates(i)
            Exit For
        End If
    End If
Next

' 5. Launch the standalone native app window
If browserExe <> "" Then
    WshShell.Run """" & browserExe & """" & browserArgs, 1, False
Else
    ' Fallback to Windows default handler
    WshShell.Run "cmd /c start " & appUrl, 0, False
End If
