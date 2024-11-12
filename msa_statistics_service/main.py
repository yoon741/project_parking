import logging
import os

import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from routes import statistics
from service.database import SessionLocal, create_tables

app = FastAPI()

# Instrumentator 설정
Instrumentator().instrument(app).expose(app)

# CORS 설정
origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(",")
print('CORS -> ', origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# 라우터 등록
app.include_router(statistics.router)

@app.get('/mariadb')
def mariadb():
    try:
        with SessionLocal() as conn:
            result = conn.execute(text('SELECT SYSDATE();')).scalar()
            return {'msg': 'Database Connection Successful!!', 'result': f'{result}'}
    except Exception as ex:
        logging.error(f"Database Connection Failed: {ex}")
        return {'msg': 'Database Connection Failed!!', 'error': str(ex)}

if __name__ == '__main__':
    create_tables()
    uvicorn.run('main:app', port=8003, reload=True)
