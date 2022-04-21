# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd

from .routers import indicators
from .sql import database


app = FastAPI()

# Avoid CORS error when calling the api from outside domains
# Set the origins to the domains allowed to access this APIs
origins = [
    # "http://local.d8mapping.it",
    # "https://localhost.tiangolo.com",
    # "http://localhost",
    # "http://localhost:8080",
    # "http://drupal:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes from external file
app.include_router(indicators.router)

# Add routes directly
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/portfolios")
async def portfolios():
    """
        Get a list of portfolios
    """
    pg_engine = database.engine
    wpp = pd.read_sql(
        "select distinct exp from ind.i_mean_y_s order by exp", con=pg_engine
    )
    return wpp.to_json()
