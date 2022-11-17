from fastapi import APIRouter, Query
import pandas as pd

import json
from .. import dap_param as param
from ..sql import database

router = APIRouter()

@router.get("/geocoder")
async def geocoder(search: str,):
    pg_engine = database.engine

    # mysql_statement = """SELECT id, label, descr FROM places WHERE LOWER(descr) LIKE LOWER(%s) ; """
    # mysql_statement = """SELECT id, label, descr, ST_AsText (ST_Transform (geom, 4326)), ST_AsGeoJSON(ST_Transform (geom, 4326)) FROM places JOIN points ON id = place_id WHERE LOWER(descr) LIKE LOWER(%s) ; """
    mysql_statement = """SELECT id, label, descr, ST_X (ST_Transform (geom, 4326)) AS lon, ST_Y (ST_Transform (geom, 4326)) AS lat, ST_AsGeoJSON(ST_Transform (geom, 4326)) FROM places JOIN points ON id = place_id WHERE LOWER(descr) LIKE LOWER(%s) ; """

    results = pd.read_sql(mysql_statement, con=pg_engine, params=('%' + search + '%',))

    return results.to_json()