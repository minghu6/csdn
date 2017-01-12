@echo off
set /a StartMS=%time:~3,1%*60000 + %time:~4,1%*6000 + %time:~6,1%*1000 + %time:~7,1%*100 + %time:~9,1%*10 + %time:~10,1%*1
%1 %2 %3 %4 %5 %6
set /a EndMS  =%time:~3,1%*60000 + %time:~4,1%*6000 + %time:~6,1%*1000 + %time:~7,1%*100 + %time:~9,1%*10 + %time:~10,1%*1
set /a realtime = (%EndMS%-%StartMS%) / 100
echo %realtime%s