import time
from random import randint
from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def hellow():
    delta = randint(0, 10)
    time.sleep(delta)
    return {'message': 'heh',
            'delta': delta}
