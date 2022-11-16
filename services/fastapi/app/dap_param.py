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

from pathlib import Path
import pdb

# local modules
sys.path.insert(0, '/wrk/progetti/tipico/')
# import utils as ut
# import modelclasslibrary as mcl
from calendar import month_abbr
import plotly.express as px

##PATHS
# ROOTDIR = Path('/mnt/data/progetti/prjo_dap/');
# ROOTDIR.mkdir(parents=True, exist_ok=True)
# DATADIR = Path(ROOTDIR, 'data');
# DATADIR.mkdir(parents=True, exist_ok=True)
# RAWDIR = Path(DATADIR, 'raw');
# RAWDIR.mkdir(parents=True, exist_ok=True)
# OUTDIR = Path(ROOTDIR, 'output');
# OUTDIR.mkdir(parents=True, exist_ok=True)
# IMGDIR = Path(ROOTDIR, 'fig');
# IMGDIR.mkdir(parents=True, exist_ok=True)
# LOGDIR = Path(ROOTDIR, 'log');
# LOGDIR.mkdir(parents=True, exist_ok=True)

##TIME
BASELINE = pd.date_range(start=dt.datetime(2010, 1, 1), end=dt.datetime(2019, 12, 31))
BASELINE_NL = pd.date_range(start=dt.datetime(2010, 1, 1), end=dt.datetime(2019, 12, 31));
BASELINE_NL = BASELINE_NL[~((BASELINE_NL.month == 2) & (BASELINE_NL.day == 29))]
HORIZON50 = pd.date_range(start=dt.datetime(2050, 1, 1), end=dt.datetime(2059, 12, 31));
HORIZON50 = HORIZON50[~((HORIZON50.month == 2) & (HORIZON50.day == 29))]
HORIZON90 = pd.date_range(start=dt.datetime(2090, 1, 1), end=dt.datetime(2099, 12, 31));
HORIZON90 = HORIZON90[~((HORIZON90.month == 2) & (HORIZON90.day == 29))]
HORIZON = pd.date_range(start=dt.datetime(2025, 1, 1), end=dt.datetime(2075, 1, 1))
SEC_DAY = 86400

timeScenD = {0: BASELINE_NL, 1: HORIZON50, 2: HORIZON50, 3: HORIZON90, 4: HORIZON90}

##time index for monthly parameters
monthsT = pd.Series(pd.date_range(start=dt.datetime(1900, 1, 1), periods=12, freq='MS'), index=range(1, 13))
monthsT_end = pd.Series(pd.date_range(start=dt.datetime(1900, 1, 1), periods=12, freq='M'), index=range(1, 13))
daysT = pd.Series(pd.date_range(start=dt.datetime(1900, 1, 1), end=dt.datetime(1900, 12, 31), freq='D'),
                  index=range(1, 366))
monthsT_end = pd.Series(pd.date_range(start=dt.datetime(1900, 1, 1), periods=12, freq='M'), index=range(1, 13))

##DATABASE
pg_engine = db.create_engine('postgresql://prjo:prjo_2112@localhost/prjo_dap')

# RAWSCHEMA   = 'raw'
# INDSCHEMA   = 'ind'
# INPUTSCHEMA   = 'input'
# OUTPUTSCHEMA   = 'output'

##COLOR SCALE
CLR_SCALE = px.colors.qualitative.Plotly
##scenarios color scale
SCEN_CLRSCALE = {0: px.colors.sequential.Blues_r, 1: px.colors.sequential.Reds_r, 2: px.colors.sequential.Greens_r}

# columns standard names:
ID_C = 'id'
TIME_C = 'time'
TIME_START_C = 'time_start'
TIME_END_C = 'time_end'
LAB_C = 'label'
PLACE_C = 'place_id'
EXP_C = 'exp_id'
SCEN_C = 'scen_id'
VALUE_C = 'value'
DESCR_C = 'descr'
DESCR_M_C = 'descr_mng'
DESCR_P_C = 'descr_plan'
QC_C = 'quality_check'
UOM_C = 'uom'
GEOM_C = 'geom'
ATTR_C = 'attributes'
TYPE_C = 'type'
ITEM_C = 'item_id'
API_C = 'api_root'
CHART_C = 'chart_id'
# COLNAMES    = [time_C, loc_C, exp_C, scen_C, value_C]

# table names

CATALOG_T = 'catalog'
CHART_CAT_T = 'chart_catalog'
CHARTS_T = 'charts'
EXP_T = 'experiments'
IND_T = 'indicators'
LINES_T = 'lines'
PRM_T = 'parameters'
PLACES_T = 'places'
POINTS_T = 'points'
POLYGONS_T = 'polygons'
SCEN_T = 'scenarios'
VARS_T = 'variables'

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

##PLOT Labels
monthsA = np.array([m for m in month_abbr])
