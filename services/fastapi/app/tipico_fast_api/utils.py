#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIPICO utils
--------------------------------------------------------------------------------

Collezione di funzioni utilizzate in modo trasversale nei vari script di progetto

"""
import os
import sys
import pandas as pd
import numpy as np
import subprocess
# from osgeo import gdal, ogr, gdalconst, osr
import pickle
import logging
import plotly.graph_objects as go
import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
# from pangres import upsert

import pdb


# local import
# import modelclasslibrary as mcl

######################################
# functions
######################################
def getFileList(rootPath, fileExt=None):
    '''return a list of files, eventually filtered by extension, with their abs path present in the input folder and subfolders'''
    fileList = []
    for root, subdirs, files in os.walk(rootPath):
        if files and fileExt:
            df = pd.DataFrame(files, columns=['file'])
            idxExt = df['file'].str.endswith('.' + fileExt)
            if idxExt.sum() > 0:
                # import pdb; pdb.set_trace()
                extFiles = root + os.path.sep + df.loc[idxExt, 'file']
                # extFiles= root + "/" + df[idxExt]
                fileList.append(extFiles.tolist())
        elif files:
            df = pd.DataFrame(files, columns=['file'])
            allFiles = root + os.path.sep + df.loc[:, 'file']
            fileList.append(allFiles.tolist())
        # break
    #
    fileList = [f for sl in fileList for f in sl]
    return fileList


#
# def rasterRprj(refRast,tbrRast, rprjFile,resampleMet=gdalconst.GRA_NearestNeighbour):
#     '''take the fullpath of a reference raster and another raster (tbrRast) which has to be reprojected and cropped on the basis of the first one'''
#     tbrRastProj     = tbrRast.GetProjection()
#     # tbrRastTrans    = tbrRast.GetGeoTransform()
#     refProj         = refRast.GetProjection()
#     refTrans        = refRast.GetGeoTransform()
#     rprjRast        = driverGtif.Create(rprjFile,refRast.RasterXSize,refRast.RasterYSize,1,refRast.GetRasterBand(1).DataType,['COMPRESS=LZW'])
#     rprjRast.SetGeoTransform(refTrans)
#     rprjRast.SetProjection(refProj)
#     gdal.ReprojectImage(tbrRast,rprjRast,tbrRastProj,refProj,resampleMet)
#     rprjRast.FlushCache()
#     return rprjRast

def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output)


def raw_to_dailymean(ts, hour):
    '''given a timeseries, i.e. dataframe with time index, with subdaily frequency, it translates in daily average from hour to hour-1'''
    return ts.values.resample('24H', base=hour, closed='left', label='right').mean()


def raw_to_dailysum(ts, hour):
    '''given a timeseries, i.e. dataframe with time index, with subdaily frequency, it translates in daily sum from hour to hour-1'''
    return ts.values.resample('24H', base=hour, closed='left', label='right').sum()


def raw_to_dailyhour(ts, hour, minute):
    '''given a timeseries, i.e. dataframe with time index, with subdaily frequency, it samples at hour:minute'''
    idx = (ts.index.hour == hour) & (ts.index.minute == minute)
    return ts.loc[idx, :]


# def convert_unit(unit_source,unit_dest)
# #unit conversion
#     if varLabel in ['pr','tp']:
#         #convert from [kg m-2 s-1] ->  mm/day
#         dfAll[varLabel]         = dfAll[varLabel] * param.SEC_DAY
#     elif varLabel in ['tas']:
#         #convert from K -> °C
#         dfAll[varLabel]         = dfAll[varLabel] - param.K_TO_C
#     else:
#         raise Exception('{} variable not managed'.format(varLabel))

def detect_spikes(ts, threshold):
    idx = []
    return idx


def correct_spikes(ts, idx, mode='linear_interpolation'):
    ts.loc[idx, :] = np.nan
    if mode == 'linear_interpolation':
        tsOut = pd.DataFrame(data=ts.interpolate())
    else:
        print('unknown mode: {}'.format(mode))
    return tsOut


def headerCheck(df, varDict):
    '''check DataFrame headers againts variables dictionary keys. Returns a boolean list wiht True for matching labels'''
    hCheck = []
    for c in df.columns:
        if c in varDict.keys():
            hCheck.append(True)
        else:
            hCheck.append(False)
    return hCheck


def keysCheck(keysList, kDict):
    'check the content of a list with respect to the keys of a Dictionary. Returns a boolean list with True for matching list items'
    kCheck = []
    for k in keysList:
        if k in kDict.keys():
            kCheck.append(True)
        else:
            kCheck.append(False)
    return kCheck


def logSetup(logPath, appName):
    '''logging.. in a better way'''
    logger = logging.getLogger(appName)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(os.path.join(logPath, '{}.log'.format(appName)))
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


# def export_todb(df,engine,schemaname,db_concat,suffix=None):
#     '''Esporta le colonne del db nelle tabelle cercando il match con le etichette del dizionario variabili standard'''
#     hC = headerCheck(df,mcl.variablesDict)
#     if any(hC):
#         for v in df.loc[:,hC].columns:
#             var = mcl.variablesDict[v]
#             if suffix:
#                 tablename = '{}_{}'.format(var['dbtable'],suffix)
#             else:
#                 tablename = var['dbtable']
#             if db_concat == 'upsert':
#                 breakpoint()
#                 # da controllare, errore probabilmente perchè la tabella su db non ha PK definite
#                 ##check the index!!
#                 upsert(engine=engine, df=df[v].to_frame(),schema=schemaname,table_name=tablename,if_row_exists='update')
#             else:
#                 df[v].to_sql(tablename,con=engine,schema=schemaname,if_exists=db_concat, index=True)
#             print('Table {} exported to db'.format(var['dbtable']))
#         # return
#     else:
#         return print('Export to DB failed: no matching between variables and column headers' )

def export_tocsv(df, csvPath, suffix=None):
    '''Esporta le colonne del dataframe in file csv'''
    # hC = headerCheck(df,mcl.variablesDict)
    for v in df.columns:
        if suffix:
            df[v].to_csv(os.path.join(csvPath, '{}_{}.csv'.format(v, suffix)), index=True)
        else:
            df[v].to_csv(os.path.join(csvPath, '{}.csv'.format(v)), index=True)
        print('Table {} exported to csv'.format(v))
    # return


def convertData(data, convert):
    '''apply convert function to data'''
    return eval('data{}'.format(convert))


def ts_lineplot(df, figpath, figTitle, y_uom, modesL=[]):
    '''time series plot'''
    # breakpoint()
    fig = go.Figure()
    # if (modesL == []) & (len(modesL) != df.columns.shape[0]):
    if len(modesL) > 0:
        if len(modesL) != df.columns.shape[0]:
            raise Exception('check modesL input!!')
        else:
            for c, m in zip(df.columns, modesL):
                fig.add_trace(go.Scatter(x=df.index, y=df[c], mode=m, name=c))
    else:
        for c in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[c], mode='lines', name=c))
    fig.update_layout(title=figTitle, xaxis_title='Time', yaxis_title=y_uom)
    # fig.write_html(os.path.join(figpath, "{}.html".format(figTitle).replace(' ', '_')))
    # print('{} plot completed'.format(figTitle))
    return fig


def ts_lineplot365(df, figpath, figTitle, y_uom, clrmap=cm.tab10, range=True):
    '''time series cyclostationary plot, optionally with range'''
    # breakpoint()
    fig = go.Figure()
    df365 = df.copy()
    df365['doy'] = df.index.dayofyear.values
    t365 = pd.date_range(start=pd.to_datetime('01-01-1900'), end=pd.to_datetime('31-12-1900'))
    # t365        = np.arange(1,367)
    for i, c in enumerate(df.columns):
        clr = 'rgb{}'.format(clrmap.colors[i])
        if range:
            fig.add_trace(
                go.Scatter(x=t365, y=df365[['doy', c]].groupby('doy').max().T.values[0], name='{} max'.format(c),
                           line=dict(color=clr, width=2, dash='dash')))
            fig.add_trace(
                go.Scatter(x=t365, y=df365[['doy', c]].groupby('doy').min().T.values[0], name='{} min'.format(c),
                           fill='tonexty', line=dict(color=clr, width=2, dash='dash')))
        fig.add_trace(
            go.Scatter(x=t365, y=df365[['doy', c]].groupby('doy').mean().T.values[0], name='{} mean'.format(c),
                       line=dict(color=clr, width=4)))
    # breakpoint()
    fig.update_layout(title=figTitle, xaxis_title='Time', yaxis_title=y_uom)
    fig.write_html(os.path.join(figpath, "{}.html".format(figTitle).replace(' ', '_')))
    print('{} plot completed'.format(figTitle))
    return fig


def events_duration(series, threshold, min_interval=1, operator='greater_equal'):
    ''' Return a time series of events higher (or lower) than a threshold, with the duration of each event expressed in days, considering eventually a minimum interval

        Parameters
        ----------
        series    : pandas time series
            The values to be evaluated
        threshold : float
            The threshold
        min_interval  : int, default=1
            number of days to separate two events
        operator  : str
            operator to be applied to identify the event

        Returns
        ---------
        sOut    : pandas timeseries
            series of first day of the event, with the duration of the event itself expressed as number of days

    '''
    if not (isinstance(series, pd.Series)):
        raise Exception('series input is not a Pandas Series. TODO: handle different input type')

    if operator in ['less', 'lt', '<']:
        idx = seriesn < threshold
    elif operator in ['less_equal', 'le', '<=']:
        idx = series <= threshold
    elif operator in ['greater', 'gt', '>']:
        idx = series > threshold
    elif operator in ['greater_equal', 'ge', '>=']:
        idx = series >= threshold
    else:
        raise Exception('{} operator undefined'.format(operator))
    #
    sD = idx.astype('int').diff()
    # check if series starts during an event with at least 2 elements
    if (idx[0] == 1) & (idx[1] == 1): sD[0] = 1
    # check if series ends during an event
    if (idx[-1] == 1):
        if (idx[-2] == 1):
            sD[-1] = -1  # if the events has at least two days, the last is the end
        else:
            sD[-1] = 0  # if the events is starting the last day of the horizon, it is discarded

    # event start/end
    idxStart = sD == 1
    idxEnd = sD == -1
    if not (idxStart.any()):
        return pd.Series()
    else:
        # remove episode if their distance is lower of the interval
        interval = (sD.index[idxStart][1:] - sD.index[idxEnd][0:-1]).days
        idx_int = interval < min_interval
        idxStart[sD.index[idxStart][1:][idx_int]] = False
        idxEnd[sD.index[idxEnd][0:-1][idx_int]] = False
        # check se serve il valore assoluto...
        duration = (sD.index[idxEnd] - sD.index[idxStart]).days
        # duration  = abs((sD.index[idxEnd][0:-1] - sD.index[idxStart][1:]).days)
        sOut = pd.Series(index=series.index[idxStart], data=duration, name=series.name)
        return sOut


def identify_period(df, dayStart, dayEnd, periodColName):
    '''attach a column with a custom period identifier, based on start/end'''
    if dayStart < dayEnd:
        idx = (df.index.dayofyear >= dayStart) & (df.index.dayofyear <= dayEnd)
    else:
        idx = (df.index.dayofyear >= dayStart) | (df.index.dayofyear <= dayEnd)
    dfPeriod = df.copy().loc[idx, :]
    period_id = ((pd.Series(dfPeriod.index).diff() > pd.Timedelta("1 day")).astype(int).cumsum()).values
    dfPeriod[periodColName] = period_id
    return dfPeriod


def daily_maxdecrease_onwindow(df, win_size, min_periods=1):
    '''given a daily timeseries DataFrame, it returns a DataFrame where for each element the maximum decrease over a given windows has been set '''
    indexer = pd.api.indexers.FixedForwardWindowIndexer(
        window_size=win_size)  # see examples here: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rolling.html
    deltaH = df - df.rolling(window=indexer, min_periods=min_periods).min()
    deltaH[deltaH < 0] = 0
    return deltaH


def period_maxdecrease_onwindow(dfPeriod, win_size, periodColName):
    '''given a daframe with discontinous timeseries related to periods, returns for each period the max of max daily decreases on a given window'''
    # save out columns
    outcols = [c for c in dfPeriod.columns if c != periodColName]
    # create periods unique identifier
    # group on identifier
    deltaH = pd.DataFrame()
    for name, group in dfPeriod.groupby(periodColName):
        periodDH = daily_maxdecrease_onwindow(group[outcols], win_size=win_size)
        deltaH.loc[name, outcols] = periodDH.max()
    return deltaH


def water_deficit(df, wdem, weight=None, power=None):
    '''given a dataframe of streamflows, it returns the waterdeficit, eventually weighted and/or with power'''
    dfdoy = df.index.dayofyear
    wdefDf = wdem.reindex(dfdoy).values - df
    wdefDf[wdefDf < 0] = 0
    if (power is not None) & (weight is not None):
        # formulazione corretta, da discutere:
        # wdefDf = weight.reindex(dfdoy).values * wdefDf.pow(power)
        # formulazione attuale, da rivedere:
        wdefDf = (weight.reindex(dfdoy).values * wdefDf).pow(power)
    elif power is not None:
        wdefDf = wdefDf.pow(power)
    elif weight is not None:
        wdefDf = weight.reindex(dfdoy).values * wdefDf
    return wdefDf


#
# def avgDeficitBeta(q, w, doy):
#     gt = 0.0;
#     for i in range(0, q.shape[0]):
#         qdiv = q[i] - 10
#         if( qdiv<0.0 ):
#             qdiv = 0.0;
#
#         d = w[doy[i]-1] - qdiv;
#         if( d < 0.0 ):
#             d = 0.0;
#
#         if( (doy[i] > 120) and (doy[i] <= 243) ):
#             d = 2*d;
#
#
#         gt = gt + d*d ;
#
#
#     return (gt/q.shape[0])
def removeDuplicates_Df(df, keep='first'):
    '''remove rows with duplicates indexes from a df '''
    idx = df.index.duplicated(keep=keep)
    return df.loc[~idx, :]


def removeDuplicates_D(dfD, keep):
    '''remove  rows with duplicates indexes from each df in a dictionary'''
    dfDOut = {}
    for k in dfD:
        dfDOut[k] = removeDuplicates_Df(dfD[k], keep)
    return dfDOut


# def datetime2matlabdn(dtime):
#     '''taken from: https://stackoverflow.com/questions/8776414/python-datetime-to-matlab-datenum#8776555'''
#     ord = dtime.toordinal()
#     mdn = dtime + dt.timedelta(days = 366)
#     frac = (dtime - dt.datetime(dtime.year,dtime.month,dtime.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
#     return mdn.toordinal() + frac

def get_df_MASH(data, ma_w, y_w):
    '''mash plot data preparation'''
    if not (isinstance(data, pd.Series) | (isinstance(data, pd.DataFrame) & (data.shape[1] == 1))):
        breakpoint()
        raise Exception('input data must be Series or 1d DataFrame')
    data_ma = data.rolling(ma_w).mean()
    dfMash = pd.DataFrame()
    for y_start in np.arange(data_ma.index.year.min(), data_ma.index.year.max() - y_w):
        y_end = y_start + y_w - 1
        idx = (data_ma.index.year >= y_start) & (data_ma.index.year <= y_end)
        dfW = data_ma.loc[idx, :]
        dfMash['{}-{}'.format(y_start, y_end)] = dfW.groupby([dfW.index.dayofyear]).mean()

    return dfMash.iloc[0:-1, :]


def plot_df_MASH(df, figTitle, uom, figPath):
    '''create a MASH static plot, assuming to have already prepared columns, with year intervals as names'''
    fig, ax = plt.subplots(figsize=(16, 9))
    df.plot(colormap='viridis', legend=False, ax=ax)
    norm = matplotlib.colors.Normalize(vmin=int(df.columns[0][0:4]), vmax=int(df.columns[-1][0:4]))
    s_m = matplotlib.cm.ScalarMappable(cmap=matplotlib.cm.viridis, norm=norm)
    s_m.set_array([])
    plt.colorbar(s_m)
    # plt.show(block=False)
    ax.set_title(figTitle)
    ax.set_xlabel('Day of the year')
    ax.set_ylabel(uom)
    fig.savefig(os.path.join(figPath, '{}.png'.format(figTitle.replace(' ', '_'))))
    plt.close()
    print('{} plotted'.format(figTitle))
    return fig

##############trash# #
# def fileName2DfS2(fileList):
#     filesDf = pd.DataFrame(fileList, columns=['fullpath'])
#     filesDf['filename'] = filesDf['fullpath'].apply(lambda x: os.path.basename(x).split('.')[0])
#     filesDf['rootpath'] = filesDf['fullpath'].apply(lambda x: os.path.dirname(x))
#     filesDf['folder'] = filesDf['fullpath'].apply(lambda x: os.path.dirname(x).split(os.sep)[-1])
#     filesDf['fuso'] = filesDf['filename'].apply(lambda x: x.split('_')[0][0:3])
#     filesDf['tile'] = filesDf['filename'].apply(lambda x: x.split('_')[0][3:])
#     filesDf['data'] = filesDf['filename'].apply(lambda x: x.split('_')[1].split('T')[0])
#     filesDf['ora']  = filesDf['filename'].apply(lambda x: x.split('_')[1].split('T')[1])
#     filesDf['sat']  = filesDf['filename'].apply(lambda x: x.split('_')[2])
#     filesDf['proc'] = filesDf['filename'].apply(lambda x: x.split('_')[3])
#     filesDf['res']  = filesDf['filename'].apply(lambda x: x.split('_')[4])
#     filesDf['banda']= filesDf['filename'].apply(lambda x: '_'.join(x.split('_')[5:]))
#     filesDf['ext']  = filesDf['fullpath'].apply(lambda x: os.path.basename(x).split('.')[1])
#     return filesDf
#
# def fileName2DfClass(fileList):
#     filesDf = pd.DataFrame(fileList, columns=['fullpath'])
#     filesDf['filename'] = filesDf['fullpath'].apply(lambda x: os.path.basename(x).split('.')[0])
#     filesDf['rootpath'] = filesDf['fullpath'].apply(lambda x: os.path.dirname(x))
#     filesDf['folder'] = filesDf['fullpath'].apply(lambda x: os.path.dirname(x).split(os.sep)[-1])
#     filesDf['tile'] = filesDf['filename'].apply(lambda x: x.split('_')[0])
#     filesDf['data'] = filesDf['filename'].apply(lambda x: x.split('_')[1])
#     filesDf['sat']  = filesDf['filename'].apply(lambda x: x.split('_')[2])
#     filesDf['ext']  = filesDf['fullpath'].apply(lambda x: os.path.basename(x).split('.')[1])
#     return filesDf
