# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd

from .routers import indicators
from .sql import database


app = FastAPI()

# Avoid CORS error when calling the api from outside domains
# Set the origins to the domains allowed to access this APIs
# Only domains without ports
origins = [
    # "http://local.d8mapping.it",
    # "https://localhost.tiangolo.com",
    # "http://localhost",
    # "http://localhost",
    # 'http://local.wp4dap_dev.it',
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

@app.get("/scenarios")
async def scenarios():
    """
        Get a list of scenarios
    """
    pg_engine = database.engine
    scen = pd.read_sql(
        "select distinct scen from ind.i_mean_y_s order by scen", con=pg_engine
    )
    return scen.to_json()

@app.get("/indicators")
async def indicators():
    """
        Get a list of indicators
    """
    pg_engine = database.engine
    inds = pd.read_sql(
        "select * from ind.ind_catalogue", con=pg_engine
    )
    return inds.to_json()
