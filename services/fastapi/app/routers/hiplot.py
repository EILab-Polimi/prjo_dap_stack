from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

import json
import pandas as pd
import numpy as np
import hiplot as hip

from .. import dap_param as prm
from ..sql import database

from .indicators import load_timeseries

router = APIRouter()


@router.get("/hiplot/comparison")
async def comparison_plot():
    pg_engine = database.engine

    scenariosT = pd.read_sql(prm.SCEN_T, con=pg_engine).set_index(prm.ID_C)
    experimentsT = pd.read_sql(prm.EXP_T, con=pg_engine).set_index(prm.ID_C)

    '''Parallel plot for comparison page: to be generalised by passing a different dictionary as input'''
    pcIndDict = {115: 'Irrigation def.', 121: 'Drinking Water def.', 122: 'Distribution Costs', 123: 'Industrial def.'}
    # pcIndList = (115,121,122,123) #i_irr_def_mean_H,i_dw_def_mean_H,i_wdistr_cost_mean_H,i_ind_def_mean_H
    sql_q = f"SELECT * from {prm.IND_T} where {prm.ITEM_C} in {tuple(pcIndDict.keys())}"
    dfPlot = pd.read_sql(sql_q, con=pg_engine)
    pcDf = dfPlot.drop(columns=[prm.TIME_START_C, prm.TIME_END_C, prm.LAB_C]).set_index([prm.EXP_C, prm.SCEN_C]).pivot(
        columns=prm.ITEM_C).droplevel(0, axis=1).reset_index()

   # print(pcDf)

    wpplinks = []
    for index, item in enumerate((experimentsT.loc[pcDf[prm.EXP_C], prm.LAB_C])):
        wpplinks.append('<a href="/dap/dap_out_infograph?wpp=' + str(pcDf['exp_id'][index]) + '">' + item + '</a>')
        #print(item)
    pcDf['wpp'] = wpplinks

    scenlinks = []
    for index, item in enumerate((scenariosT.loc[pcDf[prm.SCEN_C], prm.LAB_C])):
        scenlinks.append('<a href="/dap/dap_scenarios?scen=' + str(pcDf['scen_id'][index]) + '">' + item + '</a>')
        #print(item)
    pcDf['scenario'] = scenlinks


    pcDf['WPP'] = (experimentsT.loc[pcDf[prm.EXP_C], prm.LAB_C]).values
    pcDf['Scenario'] = (scenariosT.loc[pcDf[prm.SCEN_C], prm.LAB_C]).values

    pcDf.rename(
        columns={115: 'Irrigation def.', 121: 'Drinking Water def.', 122: 'Distribution Costs', 123: 'Industrial def.'},
        inplace=True)

    print(pcDf)

    pcDf.drop(columns=[prm.EXP_C, prm.SCEN_C], inplace=True)

    pcHTML = hip.Experiment.from_dataframe(pcDf)

    # https://facebookresearch.github.io/hiplot/experiment_settings.html#frontendrenderingsettings
    # Provide configuration for the table with all the rows
    pcHTML.display_data(hip.Displays.TABLE).update({
        # Don't display `uid` and `from_uid` columns to the user
        'hide': ['uid', 'from_uid', 'WPP', 'Scenario'],
        # In the table, order rows by default
        # 'order_by': [['pct_success', 'desc']],
        # Specify the order for columns
        # 'order': ['time'],  # Put column time first on the left
    })
    # Provide configuration for the parallel plot
    pcHTML.display_data(hip.Displays.PARALLEL_PLOT).update({
        # Hide some columns in the parallel plot
        'hide': ['wpp', 'scenario'],
        # Specify the order for others
        #'order': ['time'],  # Put column time first on the left
    })
    # Provide configuration for the XY graph
    #exp.display_data(hip.Displays.XY).update({
    #    # Default X axis for the XY plot
    #    'axis_x': 'time',
    #    # Default Y axis
    #    'axis_y': 'lr',
    #    # Configure lines
    #    'lines_thickness': 1.0,
    #    'lines_opacity': 0.1,
    #    # Configure dots
    #    'dots_thickness': 2.0,
    #    'dots_opacity': 0.3,
    #})

    # return pcHTML
    return HTMLResponse(pcHTML.to_html(), status_code=200)


@router.get("/hiplot/test")
async def hyplot_test():
    # data = [{'dropout':0.1, 'lr': 0.001, 'loss': 10.0, 'optimizer': 'SGD'},
    #     {'dropout':0.15, 'lr': 0.01, 'loss': 3.5, 'optimizer': 'Adam'},
    #     {'dropout':0.3, 'lr': 0.1, 'loss': 4.5, 'optimizer': 'Adam'}]
    # return HTMLResponse(hip.Experiment.from_iterable(data).to_html(), status_code=200)

    exp = hip.Experiment()

    # https://facebookresearch.github.io/hiplot/experiment_settings.html#

    """ Provide configuration for the table with all the rows """
    exp.display_data(hip.Displays.TABLE).update({
        # Don't display `uid` and `from_uid` columns to the user
        # 'hide': ['uid', 'from_uid'],
        'hide': ['uid'],
        # In the table, order rows by default
        # 'order_by': [['pct_success', 'desc']],
        # Specify the order for columns
        # 'order': ['time'],  # Put column time first on the left
    })

    """ Provide configuration for the XY graph """
    exp.display_data(hip.Displays.XY).update({
        'axis_x': 'generation',
        'axis_y': 'loss',
    })
    for i in range(200):
        dp = hip.Datapoint(
            uid=str(i),
            # uidanchor='<a href="/test/'+str(i)+'">' + str(i) + '</a>',
            values={
                'uidanchor': '<a href="/test/' + str(i) + '">' + str(i) + '</a>',
                'generation': i,
                'prm': 10 ** np.random.uniform(-1, 1),
                'loss': np.random.uniform(-5, 5),
            })
        if i > 10:
            from_parent = np.random.choice(exp.datapoints[-10:])
            dp.from_uid = from_parent.uid  # <-- Connect the parent to the child
            dp.values['loss'] += from_parent.values['loss']  # type: ignore
            dp.values['prm'] *= from_parent.values['prm']  # type: ignore
        exp.datapoints.append(dp)

    return HTMLResponse(exp.to_html(), status_code=200)


@router.get("/hiplot/ind")
async def hyplot_indicators():
    pg_engine = database.engine

    """ Get the item_place_df prmeter to get data for graph given th plot_id"""
    item_place_df = pd.read_sql(
        # f"SELECT {prm.ID_C},{prm.PLACE_C} FROM {prm.CATALOG_T} WHERE {prm.TYPE_C} = '{plot_id}'",
        f"SELECT {prm.ID_C},{prm.PLACE_C} FROM {prm.CATALOG_T} WHERE {prm.TYPE_C} = 'a'",
        con=pg_engine)

    dfTs = load_timeseries(item_place_df, '', [1], [1])

    print(dfTs)
    print(type(dfTs))  # <class 'pandas.core.frame.DataFrame'>

    # Extract first column of pandas dataframe
    # item_id = dfTs.iloc[:, 0] # this is item_id
    # print(item_id)

    result = dfTs.to_json(orient="records")
    parsed = json.loads(result)
    # print(json.dumps(parsed, indent=4))

    # exp = hip.Experiment(dfTs)
    exp = hip.Experiment.from_iterable(parsed)

    # return item_place_df.to_json()
    return HTMLResponse(exp.to_html(), status_code=200)
