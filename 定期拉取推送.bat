@echo off
:: 设置仓库目录
set REPO_DIR=E:\Data-Analysis

cd /d %REPO_DIR%
echo start to Synchronize the code...

:: 添加所有更改到暂存区
git add .

:: 设置时间戳
set TIMESTAMP=%date:~0,4%-%date:~5,2%-%date:~8,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

:: 提交更改
git commit -m "Auto commit at %TIMESTAMP%"
if %errorlevel% neq 0 (
    echo no new change to be committed
) else (
    echo Local changes have been committed
)

:: 拉取远程更改并与本地合并
git pull origin master
if %errorlevel% neq 0 (
    echo Error while pulling remote changes, please resolve the conflict manually
    exit /b 1
)

:: 推送本地提交到远程仓库
git push origin master
if %errorlevel% neq 0 (
    echo An error occurred while pushing to the remote repository. Check the network connection or remote repository status
    exit /b 1
) else (
    echo Synchronization succeeded
)