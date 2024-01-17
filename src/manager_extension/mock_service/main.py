import asyncio
import logging
import sys
from random import randint
from fastapi import FastAPI

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.info('API is starting up')


@app.get('/')
async def hellow():
    delta = randint(0, 10)
    logger.info('start %s', delta)
    await asyncio.sleep(delta)
    logger.info('stop %s', delta)
    return {'message': 'heh',
            'delta': delta}
