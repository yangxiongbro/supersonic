@echo off
 
:Main
set num=0
set str=%1
@REM ������ǿ�ֵ��set "str=%str:"=%" ִ��֮��str��ֵ��Ϊ"=�������ǿ�ֵ�����������
if not defined str goto end
@REM ȥ���ַ��������п��ܴ��ڵ�˫����
@REM ԭ��Ϊ��set str=%str1:str2=str3%������Ϊ���� str1 �е��ַ���str2�滻Ϊstr3�������滻��Ľ������str
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