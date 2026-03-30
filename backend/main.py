from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.events import router as event_router
from api.document import router as document_router
from api.analytics import router as analytics_router
from database.db import engine, Base

print("[Main] Iniciando aplicação...")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(event_router)
app.include_router(document_router)
app.include_router(analytics_router)
