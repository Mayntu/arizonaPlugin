function Run-Fastapi {
    Write-Host "Запуск FastAPI проекта..."
    .\venv\Scripts\activate
    code .
    py fastapi/run.py
}



Run-Fastapi