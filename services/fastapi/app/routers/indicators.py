from typing import List
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
from typing import Optional

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .. import dap_param as param
from ..sql import database
from ..tipico_fast_api import utils

router = APIRouter()

# UTILITY FUNCTIONS
def load_indicator(i_table, scenF=None, expF=None, locF=None):

    print('load_indicator')
    print(expF)

    pg_engine = database.engine
    iD = pd.read_sql(
        "SELECT * from {}.{} WHERE {} = '{}'".format(param.INDSCHEMA, param.I_CAT_TABLENAME, param.I_LABEL_C,
                                                     i_table), con=pg_engine).squeeze()
    figTitle = '{} cyclostationary monthly mean'.format(iD[param.I_DESCR_C])
    i_query = "SELECT * from {}.{} ".format(param.INDSCHEMA, i_table)
    whereFlag = False
    # scenarios filter
    if scenF:
        figTitle = '{} - Scenario:{} '.format(figTitle, ' '.join(scenF))
        scenL = "','".join(scenF)
        if whereFlag:
            i_query = "{} AND {} in ('{}','{}')".format(i_query, param.scen_C, param.BL_SCEN, scenL)
        else:
            i_query = "{} WHERE {} in ('{}','{}')".format(i_query, param.scen_C, param.BL_SCEN, scenL)
            whereFlag = True
    # experiment filter
    if expF:
        print('if expF')
        figTitle = '{} - Experiment:{} '.format(figTitle, ' '.join(expF))
        expL = "','".join(expF)
        print(expL)
        if whereFlag:
            i_query = "{} AND {} in ('{}','{}')".format(i_query, param.exp_C, param.BAU_EXP, expL)
        else:
            i_query = "{} WHERE {} in ('{}','{}')".format(i_query, param.exp_C, param.BAU_EXP, expL)
            whereFlag = True
    # location filter
    if locF:
        figTitle = '{} - Location:{} '.format(figTitle, ' '.join(locF))
        locL = "','".join(locF)
        if whereFlag:
            i_query = "{} AND {} in ('{}','{}')".format(i_query, param.exp_C, param.BAU_EXP, locL)
        else:
            i_query = "{} WHERE {} in ('{}','{}')".format(i_query, param.exp_C, param.BAU_EXP, locL)
            whereFlag = True

    dfI = pd.read_sql(i_query, con=pg_engine)
    print('END load_indicator')
    return dfI, figTitle, iD


def create_fake_indicator(time_freq, scenF=None, expF=None, locF=None):
    dfL = []
    print('create_fake_indicator')
    print(scenF)
    print(expF)
    for sc in scenF:
        for exp in expF:
            for l in locF:
                if time_freq == 'monthly':
                    df = pd.DataFrame(np.random.rand(12), columns=[param.value_C])
                    df[param.time_C] = np.arange(1, 13)
                df[param.loc_C] = l
                df[param.exp_C] = exp
                df[param.scen_C] = sc
                dfL.append(df.set_index(param.time_C))
    return pd.concat(dfL, axis=0)


def sort_key(key_list, sep, position):
    '''return sorted list of str keys composite'''
    key_n = [float(k.split(sep)[position]) for k in key_list]
    key_n = [float(k.split('_')[1]) for k in key_list]
    ksorted_idx = np.argsort(key_n)
    return key_list[ksorted_idx]

# END UTILITY FUNCTIONS

# FASTAPI ROUTES
@router.get("/indicators/", tags=["indicators"])
async def read_indicators():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/indicators/test", tags=["indicators"])
async def test_indicators():
    pg_engine = database.engine
    i_label = 'mean_y'
    i_name = 'yearly mean'
    var = 's'
    Scen = 'rcp8.5'
    Ind = 'i_{}_{}'.format(i_label, var)
    Loc = 'Locone'
    # figTitle = '{} {} {} - Scenario:{} '.format( Loc, i_name, param.variable sDict[var]['descr']['en'], Scen)
    dfI = pd.read_sql(
        "SELECT * from {}.{} WHERE scen in ('{}','{}') and loc_id = '{}'".format('ind', Ind, 'baseline',
                                                                                 Scen, Loc), con=pg_engine,
        index_col=['time'])
    dfPlot = dfI.groupby(['time', 'exp']).mean().unstack()
    dfPlot.columns = dfPlot.columns.droplevel(0)
    # print( "Content-Type: text/plain;charset=utf-8\n\n" )
    # print( dfPlot.to_json() )

    # return {"username": "fakecurrentuser"}
    return dfPlot.to_json()


@router.get("/indicators/graph", response_class=HTMLResponse)
async def graph_indicators():
    return """
        <html>
            <head>
                <title>Some HTML in here</title>
            </head>
            <body>
                <h1>Look ma! HTML!</h1>
            </body>
        </html>
        """


@router.get("/indicators/graph_test", response_class=HTMLResponse)
async def graph_indicators_test(fullPage: Optional[bool] = True):
    pg_engine = database.engine
    i_label = 'mean_y'
    i_name = 'yearly mean'
    var = 's'
    Scen = 'rcp8.5'
    Ind = 'i_{}_{}'.format(i_label, var)
    Loc = 'Locone'
    # figTitle = '{} {} {} - Scenario:{} '.format( Loc, i_name, param.variable sDict[var]['descr']['en'], Scen)
    dfI = pd.read_sql(
        "SELECT * from {}.{} WHERE scen in ('{}','{}') and loc_id = '{}'".format('ind', Ind, 'baseline',
                                                                                 Scen, Loc), con=pg_engine,
        index_col=['time'])
    dfPlot = dfI.groupby(['time', 'exp']).mean().unstack()
    dfPlot.columns = dfPlot.columns.droplevel(0)

    #
    figure = utils.ts_lineplot(dfPlot, 'test', 'My title', 'uom')

    # print(figure.show())

    # fig = plotly.io.to_html( figure, include_plotlyjs=True, full_html=False )
    # return fig

    if fullPage:
        return figure.to_html(include_plotlyjs=True, full_html=True)  # funziona
    else:
        # https://plotly.com/python-api-reference/generated/plotly.io.to_html.html
        return figure.to_html(include_plotlyjs=False, full_html=False)  # funziona


@router.get("/indicators/graph_params", response_class=HTMLResponse)
async def graph_indicators_params(i_label: Optional[str] = None,
                                  i_name: Optional[str] = None,
                                  var: Optional[str] = None,
                                  scen: Optional[str] = None,
                                  loc: Optional[str] = None):
    pg_engine = database.engine
    Ind = 'i_{}_{}'.format(i_label, var)
    figTitle = '{} {} {} - Scenario:{} '.format(loc, i_name, 'storage ', scen)
    dfI = pd.read_sql(
        "SELECT * from {}.{} WHERE scen in ('{}','{}') and loc_id = '{}'".format('ind', Ind, 'baseline',
                                                                                 scen, loc), con=pg_engine,
        index_col=['time'])
    dfPlot = dfI.groupby(['time', 'exp']).mean().unstack()
    dfPlot.columns = dfPlot.columns.droplevel(0)
    figure = utils.ts_lineplot(dfPlot, 'test', figTitle, '[Mm3]')

    """ To be run in Drupal that already have Plotly && has it's html """
    return figure.to_html(include_plotlyjs=False, full_html=False)  # funziona


# New version
@router.get("/indicators/graph_params_new", response_class=HTMLResponse)
async def graph_indicators_params_new(fullPage: Optional[bool] = True,
                                      i_table: Optional[str] = None,
                                      scenF: Optional[str] = None,
                                      # expF: Optional[str] = None, # WPP
                                      expF: Optional[List[str]] = Query(None), # WPP
                                      loc: Optional[str] = None):
    print('CALL graph_params_new')
    # i_table = 'i_sqwdef_irrd_m'
    # expF, scenF && loc must be arrays in url you pass them like &expF=WPP1&expF=WPP2
    print(expF)

    dfI, figTitle, iD = load_indicator(i_table, scenF, expF, loc)
    # print(dfI)
    # print(figTitle)
    # print(iD)
    locations = dfI[param.loc_C].unique()
    experiments = dfI[param.exp_C].unique()
    scenarios = dfI[param.scen_C].unique()
    nSub = len(locations)
    # TODO: arrange subplot for +1 locations
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True,
                        subplot_titles=['{} Reservoir'.format(l) for l in locations])
    for l in locations:
        rN = 1
        cN = 1
        # dfLoc               = dfI.xs(l,level=param.loc_C)
        dfLoc = dfI.loc[dfI[param.loc_C] == l].drop(columns=param.loc_C)
        dfLocGr = dfLoc.groupby([dfLoc[param.time_C].apply(lambda x: x.month), param.scen_C, param.exp_C]).mean()
        dfPlot = dfLocGr.unstack([1, 2])
        dfPlot.columns = dfPlot.columns.droplevel()
        for col in dfPlot.columns:
            colName = '_'.join(col)
            fig.add_trace(go.Scatter(x=dfPlot.index, y=dfPlot[col], name=colName), row=rN, col=cN)
        fig.update_yaxes(title_text=iD['unit'], row=rN, col=cN)
        fig.update_xaxes(title_text="months", row=rN, col=cN)
    fig.update_layout(title_text=figTitle)
    # fig.write_html( os.path.join( param.IMGDIR, '{}.html'.format( figTitle.replace( ' ', '_' ) ) ) )

    if fullPage:
        return fig.to_html(include_plotlyjs=True, full_html=True)  # funziona
    else:
        # https://plotly.com/python-api-reference/generated/plotly.io.to_html.html
        return fig.to_html(include_plotlyjs=False, full_html=False)  # funziona


# Project routes
@router.get("/indicators/plot_def_cycloM", response_class=HTMLResponse)
async def plot_def_cycloM(fullPage: Optional[bool] = True,
                                      i_table: Optional[str] = None,
                                      scenF: Optional[List[str]] = Query(None),
                                      expF: Optional[List[str]] = Query(None), # WPP
                                      loc: Optional[List[str]] = Query(None)):
    print('CALL graph_params_new')
    # i_table = 'i_sqwdef_irrd_m'
    # expF, scenF && loc must be arrays in url you pass them like &expF=WPP1&expF=WPP2
    print(expF)

    dfI, figTitle, iD = load_indicator(i_table, scenF, expF, loc)
    # print(dfI)
    # print(figTitle)
    # print(iD)
    locations = dfI[param.loc_C].unique()
    experiments = dfI[param.exp_C].unique()
    scenarios = dfI[param.scen_C].unique()
    nSub = len(locations)
    # TODO: arrange subplot for +1 locations
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True,
                        subplot_titles=['{} Reservoir'.format(l) for l in locations])
    for l in locations:
        rN = 1
        cN = 1
        # dfLoc               = dfI.xs(l,level=param.loc_C)
        dfLoc = dfI.loc[dfI[param.loc_C] == l].drop(columns=param.loc_C)
        dfLocGr = dfLoc.groupby([dfLoc[param.time_C].apply(lambda x: x.month), param.scen_C, param.exp_C]).mean()
        dfPlot = dfLocGr.unstack([1, 2])
        dfPlot.columns = dfPlot.columns.droplevel()
        for col in dfPlot.columns:
            colName = '_'.join(col)
            fig.add_trace(go.Scatter(x=dfPlot.index, y=dfPlot[col], name=colName), row=rN, col=cN)
        fig.update_yaxes(title_text=iD['unit'], row=rN, col=cN)
        fig.update_xaxes(title_text="months", row=rN, col=cN)
    fig.update_layout(title_text=figTitle)
    # fig.write_html( os.path.join( param.IMGDIR, '{}.html'.format( figTitle.replace( ' ', '_' ) ) ) )

    if fullPage:
        return fig.to_html(include_plotlyjs=True, full_html=True)  # funziona
    else:
        # https://plotly.com/python-api-reference/generated/plotly.io.to_html.html
        return fig.to_html(include_plotlyjs=False, full_html=False)  # funziona


@router.get("/indicators/plot_def_drw_cycloM", response_class=HTMLResponse)
async def plot_def_drw_cycloM(fullPage: Optional[bool] = True,
                              i_table: Optional[str] = None,
                              scenF: Optional[List[str]] = Query(None),
                              expF: Optional[List[str]] = Query(None),
                              loc: Optional[List[str]] = Query(None)):
    """Water deficit ciclostazionario a passo mensile (heatmap?), per idropotabile (subplot uno per schema aqp (19))"""
    i_table = 'i_sqwdef_irrd_m'
    # dfI, figTitle, iD   = load_indicator(i_table,scenF,expF,loc)
    # TMP:
    dfI = create_fake_indicator('monthly', scenF, expF, ['wdcenter_{}'.format(l) for l in np.arange(1, 20)])
    iD = pd.Series({'unit': 'm3'})
    figTitle = 'Monthly cyclostationary drinkig water deficit aggregated for water demand center [{}]'.format(
        iD['unit'])
    ##
    locations = dfI[param.loc_C].unique()
    scenarios = dfI[param.scen_C].unique() # TODO deve passare una lista
    experiments = dfI[param.exp_C].unique()
    #
    nSub = len(locations)
    nScen = len(scenarios)
    nExp = len(experiments)
    e_s = dfI.pivot(index=[param.exp_C, param.scen_C], columns=param.value_C).index.values
    fig = make_subplots(rows=nExp, cols=nScen, shared_xaxes=False,
                        subplot_titles=['Water Portfolio: {} - Scenario: {} '.format(e, s) for e, s in e_s])
    rN = 0
    for e in experiments:
        rN += 1
        cN = 0
        for s in scenarios:
            cN += 1
            if (cN == nScen) & (rN == 1):
                showScale = True
            else:
                showScale = False
            df_s_e = dfI.loc[(dfI[param.scen_C] == s) & (dfI[param.exp_C] == e)].drop(
                columns=[param.scen_C, param.exp_C])
            dfPlot = df_s_e.pivot(columns=param.loc_C, values=param.value_C)
            dfPlot = dfPlot[sort_key(dfPlot.columns, '_', 1)]
            fig.add_trace(
                go.Heatmap(z=dfPlot.T, x=dfPlot.index, y=dfPlot.columns, colorscale='Blackbody', showscale=showScale),
                row=rN, col=cN)
            fig.update_xaxes(title_text="months", tickvals=dfPlot.index, ticktext=param.monthsA[dfPlot.index], row=rN,
                             col=cN)
            fig.update_yaxes(title_text="locations", row=rN, col=cN)
    fig.update_layout(title_text=figTitle)
    # fig.write_html(os.path.join(param.IMGDIR,'{}.html'.format(figTitle.replace(' ','_'))))
    # print('{} plot done'.format(figTitle))
    # return fig.to_html(include_plotlyjs=False, full_html=False)
    if fullPage:
        return fig.to_html(include_plotlyjs=True, full_html=True)  # funziona
    else:
        # https://plotly.com/python-api-reference/generated/plotly.io.to_html.html
        return fig.to_html(include_plotlyjs=False, full_html=False)  # funziona
