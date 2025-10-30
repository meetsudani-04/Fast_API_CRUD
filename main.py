from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from api import admin
from api.router import router
from api.auth import auth_router
from api.product import product_router
from api.admin import admin

app = FastAPI(title="Trade Opportunities API", version="1.0.0")

origins = [
    "http://127.0.0.1:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(admin,prefix="/api/admin")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(product_router, prefix="/api/product_router")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)