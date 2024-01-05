import uvicorn


def main():
    uvicorn.run("manager_extension.mock_service.main:app", port=8000, log_level="info")
