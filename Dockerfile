FROM python:3.10
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
COPY main.py main.py

RUN pip install pipenv && pipenv install --system
EXPOSE 8000/tcp
ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8000
