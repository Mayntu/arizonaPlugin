Start-Process powershell -WorkingDirectory $PWD -ArgumentList "-NoExit", "-Command", "& .\RunFastapi.ps1"
Start-Process "http://localhost:5000"