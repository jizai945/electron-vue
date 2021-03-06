@REM conda activate pudu-can-tool-32  切换打包的python环境
@REM 版本从命令行中获取
@REM jsonextractor.bat package.json version
@REM set /p version=input your version(v0.0.0):

@REM 版本从package.json 中获取
for /F %%i in ('jsonextractor.bat package.json version') ^
do (
set version=%%i
)
set version=v%version:~1,-1%
echo %version%
echo name:pudu-can-tool-%version%-%date:~0,4%-%date:~5,2%-%date:~8,2%
@REM 删除同名文件夹
CMD.EXE /C call del /s /Q dist_electron\pudu-can-tool-%version%-%date:~0,4%-%date:~5,2%-%date:~8,2%
CMD.EXE /C call rd /s /q dist_electron\pudu-can-tool-%version%-%date:~0,4%-%date:~5,2%-%date:~8,2%

@REM python脚本生成exe----------------------------------
cd .\backend\
CMD.EXE /C call pyinstaller -Fw backend_up.py
CMD.EXE /C call python installer.py
cd ..
@REM ----------------------------------------------------

CMD.EXE /C call yarn run electron:build
CMD.EXE /C call md dist_electron\win-ia32-unpacked\backend\dist

@REM ------------------------------------------拷贝文件放在vue cli中
@REM CMD.EXE /C call xcopy backend\dist\ dist_electron\win-ia32-unpacked\backend\dist\ /s
@REM CMD.EXE /C call copy .\update.json dist_electron\win-ia32-unpacked\
@REM ----------------------------------------------------
CMD.EXE /C call ren dist_electron\win-ia32-unpacked pudu-can-tool-%version%-%date:~0,4%-%date:~5,2%-%date:~8,2%
