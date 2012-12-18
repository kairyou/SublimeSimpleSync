:: echo "%1 pscp.exe %2"

:: open packageDir , run pscp(args)
cd %~1 && pscp.exe %~2

:: echo "cmd /c "%~1\pscp.exe %~2""
::%~1\pscp.exe %~2

pause