from typing import List
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
from typing import Optional

import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .. import dap_param as param
from ..sql import database
# from ..tipico import utils
from ..tipico_fast_api import utils

router = APIRouter()


def load_timeseries(item_place_df, ts_type, scenF=None, expF=None):
    pg_engine = database.engine
    '''load timeseries from db'''
    itemF = item_place_df['id'].astype(str).to_list()
    itemL = "','".join(itemF)

    if ts_type.startswith('i_'):
        tabName = param.IND_T
    elif ts_type.startswith('wd_'):  ## TODO: generalizzare nome parametri
        tabName = param.PRM_T
    else:
        tabName = param.VARS_T
    # scenarios filter
    i_query = f"SELECT * from {tabName} WHERE {param.ITEM_C} in ('{itemL}')"
    if (scenF is not None) & ~(ts_type.startswith('wd_')):
        # figTitle    = '{} - Scenario:{} '.format(figTitle,' '.join(scenF))
        scenL = "','".join([str(x) for x in scenF])
        i_query = f"{i_query} AND {param.SCEN_C} in ('{scenL}')"

    # experiment filter
    if expF is not None:
        # figTitle    = '{} - Experiment:{} '.format(figTitle,' '.join(expF))
        expL = "','".join([str(x) for x in expF])
        i_query = f"{i_query} AND {param.EXP_C} in ('{expL}')"

    # #location filter not implemented
    dfTs = pd.read_sql(i_query, con=pg_engine, params={'item_id_list': item_place_df['id'].to_list()})
    dfTs = dfTs.merge(item_place_df, left_on=param.ITEM_C, right_on=param.ID_C)
    return dfTs


def load_indicator(item_place_df, scenF=None, expF=None):
    """ load indicator timeseries from db
    :param item_place_df: pandas.core.frame.DataFrame [ n rows x 2 cols (id, place_id) ]
    :param scenF: int or string of scenarios ID's
    :param expF: int or string of experiments ID's
    :return: pandas.core.frame.DataFrame [ n rows x 9 cols (item_id, time_start, time_end, exp_id, scen_id, label, value, id, place_id) ]
    """
    pg_engine = database.engine
    itemF = item_place_df['id'].astype(str).to_list()
    itemL = "','".join(itemF)
    print(itemL)
    i_query = f"SELECT * from {param.IND_T} WHERE {param.ITEM_C} in ('{itemL}')"
    # scenarios filter
    if scenF is not None:
        # figTitle    = '{} - Scenario:{} '.format(figTitle,' '.join(scenF))
        scenL = "','".join([str(x) for x in scenF])
        i_query = f"{i_query} AND {param.SCEN_C} in ('{scenL}')"

    # experiment filter
    if expF is not None:
        # figTitle    = '{} - Experiment:{} '.format(figTitle,' '.join(expF))
        expL = "','".join([str(x) for x in expF])
        i_query = f"{i_query} AND {param.EXP_C} in ('{expL}')"

    # #location filter not implemented
    dfI = pd.read_sql(i_query, con=pg_engine, params={'item_id_list': item_place_df['id'].to_list()})
    dfI = dfI.merge(item_place_df, left_on=param.ITEM_C, right_on=param.ID_C)
    return dfI


def load_variable(item_place_df, scenF=None, expF=None):
    """load variable timeseries from db
    :param item_place_df: pandas.core.frame.DataFrame [ n rows x 2 cols (id, place_id) ]
    :param scenF:
    :param expF:
    :return:
    """
    pg_engine = database.engine
    itemF = item_place_df['id'].astype(str).to_list()
    itemL = "','".join(itemF)
    i_query = f"SELECT * from {param.VARS_T} WHERE {param.ITEM_C} in ('{itemL}')"
    # scenarios filter
    if scenF is not None:
        # figTitle    = '{} - Scenario:{} '.format(figTitle,' '.join(scenF))
        scenL = "','".join([str(x) for x in scenF])
        i_query = f"{i_query} AND {param.SCEN_C} in ('{scenL}')"

    # experiment filter
    if expF is not None:
        # figTitle    = '{} - Experiment:{} '.format(figTitle,' '.join(expF))
        expL = "','".join([str(x) for x in expF])
        i_query = f"{i_query} AND {param.EXP_C} in ('{expL}')"

    # #location filter not implemented
    dfV = pd.read_sql(i_query, con=pg_engine, params={'item_id_list': item_place_df['id'].to_list()})
    dfV = dfV.merge(item_place_df, left_on=param.ITEM_C, right_on=param.ID_C)
    return dfV


def create_fake_indicator(time_freq, scenF=None, expF=None, locF=None):
    dfL = []
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


# plot_id == ts_type
@router.get("/indicators/cyclost_lineplot")
async def cyclost_lineplot(plot_id: str,
                           fullPage: Optional[bool] = True,
                           scenF: Optional[str] = None,
                           expF: List[str] = Query(default=[])):
    """

    :param plot_id: passed from
    :param fullPage:
    :param scenF:
    :param expF:
    :return:
    """
    print(plot_id);
    pg_engine = database.engine

    """ Get the item_place_df parameter to get data for graph given th plot_id"""
    item_place_df = pd.read_sql(
        f"SELECT {param.ID_C},{param.PLACE_C} FROM {param.CATALOG_T} WHERE {param.TYPE_C} = '{plot_id}'",
        con=pg_engine)

    # print(item_place_df)

    # sort places
    item_place_df.sort_values(by=param.PLACE_C, inplace=True)
    print('item_place_df  - cyclost_lineplot')
    print(item_place_df)
    # print(type(item_place_df))

    # get data

    #dfI = load_indicator(item_place_df, scenF, expF)
    ## print(dfI)
    ## print(type(dfI))

    ## places              = dfI[param.PLACE_C].unique()
    #experiments = np.sort(dfI[param.EXP_C].unique())
    #scenarios = np.sort(dfI[param.SCEN_C].unique())

    dfTs = load_timeseries(item_place_df, plot_id, scenF, expF)
    # places              = dfTs[prm.PLACE_C].unique()
    experiments = np.sort(dfTs[param.EXP_C].unique())
    scenarios = np.sort(dfTs[param.SCEN_C].unique())

    nSub = item_place_df.shape[0]
    # arrange subplots
    if nSub <= 3:
        nRows = 1
        nCols = nSub
    elif nSub <= 8:
        nRows = 2
        nCols = int(np.ceil(nSub / nRows))
    else:
        breakpoint()
        ## TODO: to generalize
    # prepare plot title and labels
    placesT = pd.read_sql(param.PLACES_T, con=pg_engine).set_index(param.ID_C)
    catalogT = pd.read_sql(param.CATALOG_T, con=pg_engine).set_index(param.ID_C)
    scenariosT = pd.read_sql(param.SCEN_T, con=pg_engine).set_index(param.ID_C)
    experimentsT = pd.read_sql(param.EXP_T, con=pg_engine).set_index(param.ID_C)

    places_labels = placesT.loc[item_place_df[param.PLACE_C], param.DESCR_C]
    unit_labels = catalogT.loc[item_place_df[param.ID_C], param.UOM_C]
    figTitle = catalogT.loc[item_place_df[param.ID_C], param.DESCR_C].iloc[0].title()
    figLabel = catalogT.loc[item_place_df[param.ID_C], param.TYPE_C].iloc[0]
    # init figure
    fig = make_subplots(rows=nRows, cols=nCols, shared_xaxes=False, subplot_titles=places_labels.to_list())
    rN = 1
    cN = 1
    # END TODO

    # loop over places
    for id, itplR in item_place_df.iterrows():
        # loop over scenarios
        for sc in scenarios:
            scLabel = scenariosT.loc[sc, param.LAB_C]
            #dfPlot = dfI.loc[
            #    (dfI[param.SCEN_C] == sc) & (dfI[param.PLACE_C] == itplR[param.PLACE_C]), [param.TIME_START_C,
            #                                                                               param.VALUE_C]].set_index(
            #    param.TIME_START_C).sort_index()
            dfPlot = dfTs.loc[(dfTs[param.SCEN_C] == sc) & (dfTs[param.PLACE_C] == itplR[param.PLACE_C]), [param.TIME_START_C,
                                                                                                     param.VALUE_C]].set_index(
                param.TIME_START_C).sort_index()

            fig.add_trace(
                go.Scatter(x=dfPlot.index, y=dfPlot[param.VALUE_C], name=scLabel, legendgroup=scLabel, showlegend=False,
                           line_color=param.CLR_SCALE[sc]), row=rN, col=cN)
        uom = catalogT.loc[itplR[param.ID_C], param.UOM_C]
        fig.update_yaxes(title_text=uom, row=rN, col=cN)
        #fig.update_xaxes(title_text="months", tickformat='%d-%b', tickmode='array', row=rN, col=cN)
        fig.update_xaxes(tickformat = '%d-%b', tickmode = 'array', row=rN, col=cN)

        # update row and col number
        if cN < nCols:
            cN += 1
        else:
            rN += 1
            cN = 1
    # show last legend
    fig.update_traces(selector=-1, showlegend=True)
    fig.update_traces(selector=-2, showlegend=True)

    if fullPage:
        fig.update_layout(title_text=figTitle)
        # return fig.to_html(include_plotlyjs=True, full_html=True)
        return HTMLResponse(content=fig.to_html(include_plotlyjs=True, full_html=True), status_code=200)
    else:
        # return fig.to_html(include_plotlyjs=False, full_html=False)
        return {"title": figTitle, "graph": fig.to_html(include_plotlyjs=False, full_html=False)}


# @router.get("/indicators/cyclost_heatmap", response_class=HTMLResponse)
@router.get("/indicators/cyclost_heatmap")
async def cyclost_heatmap(plot_id: str,
                          fullPage: Optional[bool] = True,
                          scenF: Optional[str] = None,
                          expF: List[str] = Query(default=[]),
                          loc: Optional[str] = None):
    '''plot cyclostationary monthly data on heatmap: # TODO: generalizzare per il caso con uno scenario e tanti exp e per plot giornalieri'''
    pg_engine = database.engine
    # plot_idL = ['i_cyclo_mean_dw_def_M']

    # TODO make unique function given plot_idL array

    item_place_df = pd.read_sql(
        f"SELECT {param.ID_C},{param.PLACE_C} FROM {param.CATALOG_T} WHERE {param.TYPE_C} = '{plot_id}'",
        con=pg_engine)

    # print(item_place_df)

    # sort places
    item_place_df.sort_values(by=param.PLACE_C, inplace=True)
    # get data
    dfI = load_indicator(item_place_df, scenF, expF)
    # places              = dfI[param.PLACE_C].unique()
    experiments = np.sort(dfI[param.EXP_C].unique())
    scenarios = np.sort(dfI[param.SCEN_C].unique())
    nSub = len(scenarios)
    # arrange subplots
    if nSub <= 3:
        nRows = 1
        nCols = nSub
    elif nSub <= 8:
        nRows = 2
        nCols = int(np.ceil(nSub / nRows))
    else:
        breakpoint()
        ## TODO: to generalize
    # prepare plot title and labels
    placesT = pd.read_sql(param.PLACES_T, con=pg_engine).set_index(param.ID_C)
    catalogT = pd.read_sql(param.CATALOG_T, con=pg_engine).set_index(param.ID_C)
    scenariosT = pd.read_sql(param.SCEN_T, con=pg_engine).set_index(param.ID_C)
    experimentsT = pd.read_sql(param.EXP_T, con=pg_engine).set_index(param.ID_C)

    places_labels = placesT.loc[item_place_df[param.PLACE_C], param.DESCR_C]
    unit_labels = catalogT.loc[item_place_df[param.ID_C], param.UOM_C]
    scen_labels = scenariosT.loc[scenarios, param.LAB_C]
    figTitle = catalogT.loc[item_place_df[param.ID_C], param.DESCR_C].iloc[0].title()
    figTitle += f' over different scenarios {unit_labels.iloc[0]}'
    figLabel = catalogT.loc[item_place_df[param.ID_C], param.TYPE_C].iloc[0]
    # init figure
    fig = make_subplots(rows=nRows, cols=nCols, shared_xaxes=False, subplot_titles=scen_labels.to_list())
    rN = 1
    cN = 1
    # END TODO

    # loop over scenarios
    for sc in scenarios:
        if (cN == 1) & (rN == 1):
            showScale = True
        else:
            showScale = False
        scLabel = scenariosT.loc[sc, param.LAB_C]
        dfPlot = dfI.loc[dfI[param.SCEN_C] == sc, [param.TIME_START_C, param.VALUE_C, param.PLACE_C]].set_index(
            param.TIME_START_C).sort_index()
        dfPlot = dfPlot.pivot(columns=param.PLACE_C)
        dfPlot = dfPlot.droplevel(None, axis=1)
        fig.add_trace(go.Heatmap(z=dfPlot.T, x=dfPlot.index.strftime('%b'), y=places_labels.loc[dfPlot.columns],
                                 colorscale='Blackbody', showscale=showScale), row=rN, col=cN)
        # update row and col number
        if cN < nCols:
            cN += 1
        else:
            rN += 1
            cN = 1

    if fullPage:
        fig.update_layout(title_text=figTitle)
        # return fig.to_html(include_plotlyjs=True, full_html=True)
        return HTMLResponse(content=fig.to_html(include_plotlyjs=True, full_html=True), status_code=200)
    else:
        # return fig.to_html(include_plotlyjs=False, full_html=False)
        return {"title": figTitle, "graph": fig.to_html(include_plotlyjs=False, full_html=False)}


# @router.get("/indicators/wdistr_cost_barplot", response_class=HTMLResponse)
@router.get("/indicators/wdistr_cost_barplot")
async def wdistr_cost_barplot(plot_id: str,
                              fullPage: Optional[bool] = True,
                              scenF: Optional[str] = None,
                              expF: List[str] = Query(default=[]),
                              loc: Optional[str] = None):
    """stacked barplot with subplot for each scenario"""
    pg_engine = database.engine
    plot_idL = ['i_wdistr_cost_Y']

    item_place_df = pd.read_sql(
        f"SELECT {param.ID_C},{param.PLACE_C} FROM {param.CATALOG_T} WHERE {param.TYPE_C} like %(cost_ind_suffix)s",
        con=pg_engine, params={'cost_ind_suffix': '%_c'})

    # get data
    dfV = load_variable(item_place_df, scenF, expF)
    # places              = dfI[param.PLACE_C].unique()
    experiments = np.sort(dfV[param.EXP_C].unique())
    scenarios = np.sort(dfV[param.SCEN_C].unique())
    nSub = len(scenarios)
    # arrange subplots
    if nSub <= 3:
        nRows = 1
        nCols = nSub
    elif nSub <= 8:
        nRows = 2
        nCols = int(np.ceil(nSub / nRows))
    else:
        breakpoint()
        ## TODO: to generalize
    # prepare plot title and labels
    placesT = pd.read_sql(param.PLACES_T, con=pg_engine).set_index(param.ID_C)
    catalogT = pd.read_sql(param.CATALOG_T, con=pg_engine).set_index(param.ID_C)
    scenariosT = pd.read_sql(param.SCEN_T, con=pg_engine).set_index(param.ID_C)
    experimentsT = pd.read_sql(param.EXP_T, con=pg_engine).set_index(param.ID_C)

    places_labels = placesT.loc[item_place_df[param.PLACE_C], param.DESCR_C]
    unit_labels = catalogT.loc[item_place_df[param.ID_C], param.UOM_C]
    catalog_labels = catalogT.loc[item_place_df[param.ID_C], param.LAB_C]
    scen_labels = scenariosT.loc[scenarios, param.LAB_C]
    figTitle = 'Water distribution costs over time under different scenarios [eur/year]'
    figLabel = 'water_distribution_costs'
    # init figure
    fig = make_subplots(rows=nRows, cols=nCols, shared_xaxes=False, subplot_titles=scen_labels.to_list())
    rN = 1
    cN = 1
    # loop over scenarios
    for sc in scenarios:
        if (cN == 1) & (rN == 1):
            showScale = True
        else:
            showScale = False
        scLabel = scenariosT.loc[sc, param.LAB_C]
        dfPlot = dfV.loc[dfV[param.SCEN_C] == sc, [param.TIME_C, param.VALUE_C, param.ITEM_C]].set_index(
            param.TIME_C).sort_index()
        dfPlot = dfPlot.pivot(columns=param.ITEM_C)
        dfPlot = dfPlot.droplevel(None, axis=1)
        for i, c_id in enumerate(dfPlot.columns):
            fig.add_trace(go.Bar(name=catalog_labels.loc[c_id], x=dfPlot.index.year, y=dfPlot[c_id],
                                 marker_color=param.SCEN_CLRSCALE[sc][i]), row=rN, col=cN)

        # update row and col number
        if cN < nCols:
            cN += 1
        else:
            rN += 1
            cN = 1
    # fig.update_layout(title_text=figTitle, barmode='stack')
    fig.update_layout(barmode='stack')
    if fullPage:
        fig.update_layout(title_text=figTitle)
        #return fig.to_html(include_plotlyjs=True, full_html=True)
        return HTMLResponse(content=fig.to_html(include_plotlyjs=True, full_html=True), status_code=200)
    else:
        # return fig.to_html(include_plotlyjs=False, full_html=False)
        return {"title": figTitle, "graph": fig.to_html(include_plotlyjs=False, full_html=False)}


@router.get("/indicators/prm_groupedbarplot")
async def prm_groupedbarplot(plot_id: str,
                             fullPage: Optional[bool] = True,
                             scenF: Optional[str] = None,
                             expF: List[str] = Query(default=[]),
                             loc: Optional[str] = None):
    '''plot cyclostationary monthly data: # TODO: generalizzare per il caso con uno scenario e tanti exp e per plot giornalieri'''
    pg_engine = database.engine
    item_place_df = pd.read_sql(
        f"SELECT {param.ID_C},{param.PLACE_C} FROM {param.CATALOG_T} WHERE {param.TYPE_C} = '{plot_id}'", con=pg_engine)
    # sort places
    item_place_df.sort_values(by=param.PLACE_C, inplace=True)
    # get data
    dfTs = load_timeseries(item_place_df, plot_id, None, expF)
    if dfTs.empty:
        return print(f'no data for {plot_id} and experiment {expF}')
    # places              = dfTs[param.PLACE_C].unique()
    # prepare plot title and labels
    placesT = pd.read_sql(param.PLACES_T, con=pg_engine).set_index(param.ID_C)
    catalogT = pd.read_sql(param.CATALOG_T, con=pg_engine).set_index(param.ID_C)
    scenariosT = pd.read_sql(param.SCEN_T, con=pg_engine).set_index(param.ID_C)
    experimentsT = pd.read_sql(param.EXP_T, con=pg_engine).set_index(param.ID_C)

    places_labels = placesT.loc[item_place_df[param.PLACE_C], param.DESCR_C]
    unit_labels = catalogT.loc[item_place_df[param.ID_C], param.UOM_C]
    figTitle = catalogT.loc[item_place_df[param.ID_C], param.DESCR_C].iloc[0].title()
    figLabel = plot_id
    # init figure
    fig = go.Figure()
    # loop over places
    for id, itplR in item_place_df.iterrows():
        dfPlot = dfTs.loc[(dfTs[param.PLACE_C] == itplR[param.PLACE_C]), [param.TIME_C, param.VALUE_C]].set_index(
            param.TIME_C).sort_index()
        fig.add_trace(
            go.Bar(x=dfPlot.index.strftime('%b'), y=dfPlot[param.VALUE_C], name=places_labels.loc[itplR[param.PLACE_C]]))
    # adjust title and uom
    fig.update_layout(barmode='group', yaxis=dict(title=unit_labels.iloc[0]))
    if fullPage:
        fig.update_layout(title_text=figTitle)
        #return fig.to_html(include_plotlyjs=True, full_html=True)
        return HTMLResponse(content=fig.to_html(include_plotlyjs=True, full_html=True), status_code=200)
    else:
        # return fig.to_html(include_plotlyjs=False, full_html=False)
        return {"title": figTitle, "graph": fig.to_html(include_plotlyjs=False, full_html=False)}
