@echo off
chcp 65001 >nul
echo ==========================================
echo      Git 一键快速上传工具
echo ==========================================
echo.

:: 检查是否在git仓库中
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo [错误] 当前目录不是Git仓库！
    pause
    exit /b 1
)

:: 显示当前状态
echo [1/5] 检查仓库状态...
git status --short
echo.

:: 询问提交信息
set /p commit_msg="请输入提交信息 (直接回车使用默认'更新代码'): "
if "%commit_msg%"=="" set commit_msg=更新代码

:: 添加所有更改
echo.
echo [2/5] 添加文件到暂存区...
git add -A
echo 完成

:: 提交
echo.
echo [3/5] 提交更改...
git commit -m "%commit_msg%"
if errorlevel 1 (
    echo [提示] 没有需要提交的更改，或提交失败
    pause
    exit /b 0
)

:: 推送到远程
echo.
echo [4/5] 推送到远程仓库...
git push origin HEAD
if errorlevel 1 (
    echo.
    echo [错误] 推送失败，尝试设置上游分支...
    git push -u origin HEAD
)

:: 完成
echo.
echo [5/5] 完成！
git log -1 --oneline
echo.
echo ==========================================
pause
