Set WshShell = CreateObject("WScript.Shell")
Set oExec = WshShell.Exec("git pull")

Dim output
output = oExec.StdOut.ReadAll()
Dim errOutput
errOutput = oExec.StdErr.ReadAll()

If oExec.ExitCode = 0 Then
    MsgBox "Upgrade successful" & vbCrLf & vbCrLf & output, vbInformation, "Git Pull"
Else
    MsgBox "Upgrade failed" & vbCrLf & vbCrLf & errOutput, vbCritical, "Git Pull"
End If