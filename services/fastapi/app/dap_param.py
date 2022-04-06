'''
PROJECTO DAP
=========================
:title: DAP Parameters
:docs:
:authors: @MarcoMicotti
:creation: 09.12.2021
:notes:
'''
import os
import sys
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy as db
from calendar import month_abbr

from pathlib import Path
import pdb

# local modules
sys.path.insert(0, '/wrk/progetti/tipico/')
# import utils as ut
# import modelclasslibrary as mcl

##PATHS
# ROOTDIR = Path( '/mnt/data/progetti/prjo_dap/' );
# ROOTDIR.mkdir( parents=True, exist_ok=True )
# DATADIR = Path( ROOTDIR, 'data' );
# DATADIR.mkdir( parents=True, exist_ok=True )
# RAWDIR = Path( DATADIR, 'raw' );
# RAWDIR.mkdir( parents=True, exist_ok=True )
# OUTDIR = Path( ROOTDIR, 'output' );
# OUTDIR.mkdir( parents=True, exist_ok=True )
# IMGDIR = Path( ROOTDIR, 'fig' );
# IMGDIR.mkdir( parents=True, exist_ok=True )
# LOGDIR = Path( ROOTDIR, 'log' );
# LOGDIR.mkdir( parents=True, exist_ok=True )

##TIME
HORIZON = pd.date_range(start=dt.datetime(2025, 1, 1), end=dt.datetime(2075, 1, 1))

##DATABASE
#                         dialect+driver://username:password@host:port/database
# pg_engine = db.create_engine('postgresql://prjo:prjo_2112@localhost/prjo_dap')
pg_engine = db.create_engine('postgresql://prjo:prjo@localhost/prjo_dap_v2')

RAWSCHEMA = 'raw'
INDSCHEMA = 'ind'
INPUTSCHEMA = 'input'
OUTPUTSCHEMA = 'output'
# columns standard names:
time_C = 'time'
loc_C = 'loc_id'
exp_C = 'exp'
scen_C = 'scen'
value_C = 'value'
COLNAMES = [time_C, loc_C, exp_C, scen_C, value_C]

# ind description standard names
I_CAT_TABLENAME = 'ind_catalogue'
I_LABEL_C = 'label'
I_DESCR_C = 'descr'
I_UNIT_C = 'unit'

##VARIABLES
variablesDict = {
    'a': {'descr': {'it': 'afflusso', 'en': 'inflow'}, 'unit': '[m3/sec]', 'dbtable': 'inflow'},
    's': {'descr': {'it': 'invaso', 'en': 'storage'}, 'unit': '[Mm3]', 'dbtable': 'storage'},
    'h': {'descr': {'it': 'livello', 'en': 'water level'}, 'unit': '[m]', 'dbtable': 'waterlevel'},
    'r': {'descr': {'it': 'rilascio', 'en': 'release'}, 'unit': '[m3/sec]'},
    'q': {'descr': {'it': 'portata', 'en': 'streamflow'}, 'unit': '[m3/sec]', 'dbtable': 'streamflow'},
    'tmean': {'descr': {'it': 'temperatura media', 'en': 'mean temperature'}, 'unit': '[°C]',
              'dbtable': 'temperature_mean'},
    'p': {'descr': {'it': 'precipitazione', 'en': 'precipitation'}, 'unit': '[mm]', 'dbtable': 'precipitation'},
    'dwa': {'descr': {'it': 'prelievo idropotabile', 'en': 'drinking water abstraction'}, 'unit': '[l/sec]',
            'dbtable': 'dw_abstraction'},
}

##SCENARIOS
BL_SCEN = 'baseline'
BAU_EXP = 'bau'
##IND param
# drinking water supply demand
dwdDict = {'Locone': 100, 'Pertusillo': 10, 'Occhito': 500, 'MonteCotugno': 250, 'Conza': 300}

# PLOT Labels
monthsA = np.array([m for m in month_abbr])
