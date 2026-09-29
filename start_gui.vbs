Set shell = CreateObject("WScript.Shell")
Set fileSystem = CreateObject("Scripting.FileSystemObject")

projectFolder = fileSystem.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = projectFolder

command = Chr(34) & projectFolder & "\start_gui.bat" & Chr(34)
exitCode = shell.Run(command, 0, True)

If exitCode <> 0 Then
    MsgBox "The quiz could not start. Check that Python is installed and try again.", _
        vbExclamation, "Computer Knowledge Quiz"
End If
