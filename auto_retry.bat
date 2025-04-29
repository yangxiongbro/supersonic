@REM auto_retry.bat "git pull"
@REM 不显示本行命令行
@echo off
setlocal enabledelayedexpansion
echo hello world

@REM set work_dir=%1
@REM if not defined work_dir goto end
@REM set "work_dir=%work_dir:"=%"
@REM if not defined work_dir goto end
@REM 防止有切换驱动器的情况，比如当前工作路径在c盘，需要切换到d盘，直接使用cd是不行的，需要加上 /d
@REM cd /d !work_dir!

set cmd_str=%1
if not defined cmd_str goto end
set "cmd_str=%cmd_str:"=%"
if not defined cmd_str goto end

:loop
@REM git fetch --all
@REM git reset --hard origin/develop
@REM git pull
!cmd_str! >auto_retry.output.txt 2>&1
timeout /t 2
for /f "delims=" %%i in (auto_retry.output.txt) do ( 
  set "content=%%i"
  call str_length.bat !content!
  set "output_len=!ERRORLEVEL!"
  echo !output_len!：!content!
  if !output_len! gtr 4 (
    set content_start=!content:~0,5!
    if !content_start!==fatal (
      echo 重试
      goto loop
    )
  )
)

:end
echo 结束重试
del auto_retry.output.txt