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


# Main routes

@app.get("/portfolios")
async def portfolios():
    """
        Get a list of portfolios table experiments aka WPP
    """
    pg_engine = database.engine
    wpp = pd.read_sql(
        "select * from experiments", con=pg_engine
    )
    return wpp.to_json()


@app.get("/scenarios")
async def scenarios():
    """
        Get a list of scenarios table scenarios aka baseline, rcp
    """
    pg_engine = database.engine
    scen = pd.read_sql(
        "select * from scenarios", con=pg_engine
    )
    return scen.to_json()


@app.get("/graph_api_url")
async def graph_api_url(plot_id: str):
    """
        Get the api_url/function to call for generate the graph
    """
    pg_engine = database.engine
    api_url = pd.read_sql(
        f"SELECT * from charts "
        "WHERE id IN (SELECT DISTINCT chart_id FROM chart_catalog WHERE item_id IN "
        f"(SELECT id FROM catalog WHERE type LIKE '{plot_id}'))", con=pg_engine
    )
    return api_url.to_json()


@app.get("/indicators")
async def indicators():
    """
        Get a list of indicators to fill the selectbox
    """
    pg_engine = database.engine
    indicators = pd.read_sql(
        # f"SELECT DISTINCT ON (type) type, label, descr FROM catalog WHERE type LIKE '{params}'"
        f"SELECT DISTINCT ON (type) type, label, descr FROM catalog WHERE type LIKE %(this_name)s"
        # f"SELECT DISTINCT ON (type) type, label, descr FROM catalog"
        , con=pg_engine
        , params={'this_name': 'i\_%'}
    )
    # indicators = pd.read_sql(
    #     f"SELECT * from charts "
    #     "WHERE id IN (SELECT DISTINCT chart_id FROM chart_catalog WHERE item_id IN "
    #     f"(SELECT id FROM catalog WHERE type LIKE %(this_name)s))"
    #     , con=pg_engine
    #     , params={'this_name': 'i\_%'}
    # )

    # se vuoi passare un parametro in più
    # query = ("SELECT stuff FROM TABLE WHERE name LIKE %(this_name)s")
    # result = pd.read_sql(query,con=cnx, params={'this_name': '%'+ some_name +'%'})

    return indicators.to_json()
