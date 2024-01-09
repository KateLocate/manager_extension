import uvicorn


def main():
    uvicorn.run("manager_extension.mock_service.main:app", host='0.0.0.0', port=8000, log_level="info")
