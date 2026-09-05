' ==============================================================================
' Universal Clipboard - Robust 1-Click Desktop Launcher for Windows
' ==============================================================================
Option Explicit

Dim WshShell, FSO, scriptDir, http, serverRunning, i, maxWait
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

' 1. Check if server is already active on port 7890
serverRunning = False
On Error Resume Next
Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
If http Is Nothing Then Set http = CreateObject("MSXML2.ServerXMLHTTP")
If Not http Is Nothing Then
    http.Open "GET", "http://127.0.0.1:7890/api/status", False
    http.setTimeouts 500, 500, 500, 500
    http.Send
    If http.Status = 200 Then serverRunning = True
End If
On Error GoTo 0

' 2. If not running, start Python from local venv (completely silent)
If Not serverRunning Then
    Dim pythonExe
    If FSO.FileExists(scriptDir & "\venv\Scripts\pythonw.exe") Then
        pythonExe = scriptDir & "\venv\Scripts\pythonw.exe"
    ElseIf FSO.FileExists(scriptDir & "\venv\Scripts\python.exe") Then
        pythonExe = scriptDir & "\venv\Scripts\python.exe"
    Else
        pythonExe = "python"
    End If

    Dim runCmd
    runCmd = """" & pythonExe & """ """ & scriptDir & "\server.py"" 7890"
    WshShell.Run runCmd, 0, False

    ' Wait up to 6 seconds for server to be responsive
    maxWait = 30
    For i = 1 To maxWait
        WScript.Sleep 200
        On Error Resume Next
        Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
        If http Is Nothing Then Set http = CreateObject("MSXML2.ServerXMLHTTP")
        http.Open "GET", "http://127.0.0.1:7890/api/status", False
        http.setTimeouts 300, 300, 300, 300
        http.Send
        If http.Status = 200 Then
            serverRunning = True
            Exit For
        End If
        On Error GoTo 0
    Next
End If

' 3. Open standalone app window via Edge / Chrome
Dim appUrl, browserExe, browserArgs
appUrl = "http://localhost:7890"
browserArgs = " --app=" & appUrl & " --window-size=1320,880"

Dim candidates(5)
candidates(0) = WshShell.ExpandEnvironmentStrings("%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe")
candidates(1) = WshShell.ExpandEnvironmentStrings("%ProgramFiles%\Microsoft\Edge\Application\msedge.exe")
candidates(2) = WshShell.ExpandEnvironmentStrings("%ProgramFiles%\Google\Chrome\Application\chrome.exe")
candidates(3) = WshShell.ExpandEnvironmentStrings("%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe")
candidates(4) = WshShell.ExpandEnvironmentStrings("%LocalAppData%\Google\Chrome\Application\chrome.exe")
candidates(5) = WshShell.ExpandEnvironmentStrings("%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe")

browserExe = ""
For i = 0 To UBound(candidates)
    If candidates(i) <> "" Then
        If FSO.FileExists(candidates(i)) Then
            browserExe = candidates(i)
            Exit For
        End If
    End If
Next

If browserExe <> "" Then
    WshShell.Run """" & browserExe & """" & browserArgs, 1, False
Else
    WshShell.Run "cmd /c start " & appUrl, 0, False
End If
