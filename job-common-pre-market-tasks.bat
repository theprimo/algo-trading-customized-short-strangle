:: perform pre market tasks, common tasks shared job

::start cmd.exe /c "%FLINK_HOME%\bin\start-cluster.bat"
::timeout 60

:: update python libraries - schedule

start cmd.exe /c "D:\MyWork\task\automate\python\schedule\venv\Scripts\pip.exe install future -U"
timeout 10
start cmd.exe /c "D:\MyWork\task\automate\python\schedule\venv\Scripts\pip.exe install requests -U"
timeout 10
start cmd.exe /c "D:\MyWork\task\automate\python\schedule\venv\Scripts\pip.exe install websocket -U"
timeout 10
start cmd.exe /c "D:\MyWork\task\automate\python\schedule\venv\Scripts\pip.exe install websocket_client -U"
timeout 10
start cmd.exe /c "D:\MyWork\task\automate\python\schedule\venv\Scripts\pip.exe install stocknotebridge -U"
timeout 10

start cmd.exe /c "D:\MyWork\task\automate\python\schedule\venv\Scripts\pip.exe install fyers_api -U"
timeout 10
start cmd.exe /c "D:\MyWork\task\automate\python\schedule\venv\Scripts\pip.exe install truedata_ws -U"
timeout 10

start cmd.exe /c "D:\MyWork\task\automate\python\schedule\venv\Scripts\pip.exe install schedule -U"
timeout 10

:: generate fyers access token - schedule\overnight
:: "D:\MyWork\task\automate\python\schedule\venv\Scripts\python.exe" "D:\MyWork\task\automate\python\schedule\overnight_generate_access_token.py"

:: generate fyers access token - schedule\scalping  - customized short strangle - overnight
"D:\MyWork\task\automate\python\schedule\venv\Scripts\python.exe" "D:\MyWork\task\automate\python\schedule\scalping\scalping_generate_token.py"
timeout 10

