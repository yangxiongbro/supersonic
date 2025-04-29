@echo off
 
:Main
set num=0
set str=%1
@REM 输入的是空值，set "str=%str:"=%" 执行之后，str的值将为"=，而不是空值，结果将出错
if not defined str goto end
@REM 去掉字符串中所有可能存在的双引号
@REM 原型为：set str=%str1:str2=str3%，含义为：把 str1 中的字符串str2替换为str3，并把替换后的结果赋予str
set "str=%str:"=%"
if defined str (
  :count
  set /a num+=1
  set "str=%str:~1%"
  if defined str goto count
)
 
:end
@REM echo %num%
exit /b %num%