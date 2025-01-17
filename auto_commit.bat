@echo off
chcp 65001 > nul

:: 获取当前时间
set YYYY=%date:~0,4%
set MM=%date:~5,2%
set DD=%date:~8,2%
set HH=%time:~0,2%
set MI=%time:~3,2%
set SS=%time:~6,2%

:: 处理时间格式
if "%HH:~0,1%" == " " set HH=0%HH:~1,1%

:: 设置时间戳
set timestamp=%YYYY%-%MM%-%DD%_%HH%-%MI%

:: 添加所有修改并提交
git add .
git commit -m "Auto commit at %timestamp%"

:: 创建标签
git tag -a "v_%timestamp%" -m "Version at %timestamp%"

:: 推送到远程
git push origin master
git push origin --tags

:: 显示结果
echo.
echo Recent commits:
git log --oneline -n 5
echo.
echo Recent tags:
git tag -n1 | sort /R | findstr /B "v_"

pause
