from flask import Flask, render_template, url_for, request, redirect, session, jsonify, make_response
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
import csv
import io
import pandas as pd
import numpy as np
from collections import Counter
from itertools import combinations
import os
import threading

# import modin.pandas as pd
# import asyncio

CASES = ['comboMatrixWithVar', 'comboMatrixNoVar', 'comboMatrixWithVarEmail', 'comboMatrixNoVarEmail', 'mostoftenSoldWithVar',  'mostoftenSoldNoVar']

app = Flask(__name__)
alldata = [] 
def get_data_set_up(df):
    df.rename(columns={'Lineitem name':'Lineitem_name'}, inplace=True)
    df.rename(columns={'Lineitem quantity':'Lineitem_quantity'}, inplace=True)
    dff = df[[ 'Name', 'Lineitem_name', 'Lineitem_quantity', 'Email']]
    mydata = df[[ 'Name', 'Lineitem_name', 'Lineitem_quantity', 'Email']]
    #duplicate rows where one item is bought multiple times
    dff = dff.loc[dff.index.repeat(dff.Lineitem_quantity)]
    dff = dff[[ 'Name', 'Lineitem_name', 'Email']]
    numbitemsOrdered = len(dff)
    numbOrders = len(dff.groupby('Name'))
    uniqueProductsWithVar = len(dff['Lineitem_name'].unique())
    #filter by group with more than one item
    dff2 = dff.groupby('Name').filter(lambda g: len(g) > 1)
    numbGroupedOrders = len(dff2.groupby('Name'))
    #average items per basket
    averageBasket = dff.groupby('Name').size().agg('mean')
    averageBasket = round(averageBasket, 2)
    #get average items per grouped basket
    averageGroupedBasket = dff2.groupby('Name').size().agg('mean')
    averageGroupedBasket = round(averageGroupedBasket , 2)
    #get number of unique products sold (with variante included as separate)
    #get number of unique product inside all grouped orders (with variante included as separated)
    UniqueProdInGroupOrdersWithVar = len(dff2['Lineitem_name'].unique())
    #Take variante out
    dff3 = dff
    dff3['Lineitem_name'] = dff3['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )
    uniqueProductsNoVar = len(dff3['Lineitem_name'].unique())
    #get number of unique product inside all grouped orders (with variante not included as separated)
    dff3Grouped = dff3.groupby('Name').filter(lambda g: len(g) > 1)
    UniqueProdInGroupOrdersNoVar = len(dff3Grouped['Lineitem_name'].unique())
    comboMatrixWithVar = Findmatrixes(dff2,'Name')

    global alldata
    alldata.extend((numbOrders, numbitemsOrdered, numbGroupedOrders, averageBasket, averageGroupedBasket, uniqueProductsWithVar, uniqueProductsNoVar,
    UniqueProdInGroupOrdersWithVar, UniqueProdInGroupOrdersNoVar,  mydata, comboMatrixWithVar))
    return alldata


@app.route('/',methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        global alldata
        
        if request.files.get('fileupload', None):
            df = pd.read_csv(request.files.get('fileupload'))
            alldata = []
            try:
                alldata = get_data_set_up(df)
                return render_template('/dynamic.html', cases= CASES, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                    averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                    UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8],  comboMatrixWithVar = alldata[10], tab = 'combo') 
                    # mydata = alldata[9],
                # comboMatrixWithVar = alldata[9], comboMatrixNoVar = alldata[10], comboMatrixWithVarEmail= alldata[11], comboMatrixNoVarEmail = alldata[12]
            except:
                return 'There was a mistake, your file doesnt seem to be in the right format'
        elif 'No Variante' in request.form:
            
            mydata = alldata[9]
            data = mydata.loc[mydata.index.repeat(mydata.Lineitem_quantity)]
            data = data[[ 'Name', 'Lineitem_name', 'Email']]   
            data['Lineitem_name'] = data['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )
            dff3Grouped = data.groupby('Name').filter(lambda g: len(g) > 1)
            comboMatrixNoVar = Findmatrixes(dff3Grouped, 'Name')
            return render_template('/dynamic.html', cases = CASES, data = comboMatrixNoVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], tab = 'combo' )
# comboMatrix
    return render_template('/index.html')

def getmatemailwithvar():
    global alldata
    mydata = alldata[9]
    data = mydata.loc[mydata.index.repeat(mydata.Lineitem_quantity)]
    data = data[[ 'Name', 'Lineitem_name', 'Email']]
    comboMatrixWithVarEmail = Findmatrixes(data.groupby('Email').filter(lambda g: len(g) > 1), 'Email')
    return comboMatrixWithVarEmail

@app.route("/data", methods=['GET', 'POST'])
def getinfo():
    global alldata
    mydata = alldata[9]
    data = mydata.loc[mydata.index.repeat(mydata.Lineitem_quantity)]
    data = data[[ 'Name', 'Lineitem_name', 'Email']]
    
    if request.method == 'POST':
         
        if 'comboMatrixWithVar' in request.form:
            data2 = data.groupby('Name').filter(lambda g: len(g) > 1)
            comboMatrixWithVar = Findmatrixes(data2,'Name')
            return render_template('/dynamic.html',cases = CASES, data = comboMatrixWithVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8] )

        elif 'No Variante' in request.form:   
            data['Lineitem_name'] = data['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )
            dff3Grouped = data.groupby('Name').filter(lambda g: len(g) > 1)
            comboMatrixNoVar = Findmatrixes(dff3Grouped, 'Name')
            return render_template('/dynamic.html', cases = CASES, data = comboMatrixNoVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8],  tab = "combo")
# comboMatrixWithVar = alldata[10]
        elif 'comboMatrixWithVarEmail' in request.form:
            comboMatrixWithVarEmail = Findmatrixes(data.groupby('Email').filter(lambda g: len(g) > 1), 'Email')
            return render_template('/dynamic.html',cases = CASES, data = comboMatrixWithVarEmail, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8] )

        elif 'comboMatrixNoVarEmail' in request.form:
            data['Lineitem_name'] = data['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )
            comboMatrixNoVarEmail = Findmatrixes(data.groupby('Email').filter(lambda g: len(g) > 1), 'Email')
            return render_template('/dynamic.html',cases = CASES, data = comboMatrixNoVarEmail, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8] )

        elif 'mostoftenSoldWithVar' in request.form:
            mostoftenSoldWithVar = mostsold(mydata[[ 'Name', 'Lineitem_name']])
            return render_template('/dynamic.html',cases = CASES, data2 = mostoftenSoldWithVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8] )

        elif 'mostoftenSoldNoVar' in request.form:
            mydt = mydata[[ 'Name', 'Lineitem_name']]
            mydt['Lineitem_name'] = mydt['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )        
            mostoftenSoldNoVar = mostsold(mydt)

            return render_template('/dynamic.html',cases = CASES, data2 = mostoftenSoldNoVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8] )

    return render_template('/dynamic.html', cases = CASES,numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8])



@app.route('/result', methods=["GET", "POST"])
def button():
    global alldata
    if request.method == "POST":
        if request.form.get("submit_a"):
            dftodl = alldata[9]
            resp = make_response(dftodl.to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp
        elif request.form.get("submit_b"):
            dftodl = alldata[10]
            resp = make_response(dftodl.to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp
        elif request.form.get("submit_c"):
            dftodl = alldata[11]
            resp = make_response(dftodl.to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp
        elif request.form.get("submit_d"):
            dftodl = alldata[12]
            resp = make_response(dftodl.to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp


@app.route('/combination',methods=['GET', 'POST'])
def comb():
    global alldata
    if request.method == 'POST':
        r = request.form['contentSearch']
        # try: 
        if 'variante' in request.form:
            mybestmat = FindBestMatch(alldata[9], r)
        else:
            mybestmat =  FindBestMatch(alldata[10], r)
        return render_template('/combination.html', mybestmat = mybestmat)
    return render_template('/index.html')



#get best matches for on speciic product
def FindBestMatch(matrix, item):
  ff =  matrix[matrix['first']==item]
  f = matrix[matrix['second']==item]
  fff = pd.concat([f, ff]).drop_duplicates()
  return fff

def Findmatrixes(df, groupby):
    result = df.groupby([groupby]).agg(lambda g: list(set(combinations(sorted(g), 2))))
    comboMatrix = pd.DataFrame(Counter(result.Lineitem_name.sum()).items(), columns=['combos', 'count'])
    comboMatrix[['first','second']] = pd.DataFrame(comboMatrix.combos.values.tolist(), index= comboMatrix.index)
    comboMatrix = comboMatrix.sort_values('count', ascending=False)
    comboMatrix = comboMatrix.iloc[:, 1: 4]
    return comboMatrix

def mostsold(df):

    dfg = df.groupby('Name').filter(lambda g: len(g) > 1)
    x = dfg.groupby('Lineitem_name').count().reset_index()
    x.columns = ['Lineitem_name', 'count']
    x = x.sort_values('count', ascending=False)
    return x


if __name__ == '__main__':
    
    app.run(debug=True)