from flask import Flask, render_template, url_for, request, redirect, session, jsonify
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



app = Flask(__name__)
alldata = [] 
def get_data_set_up(df):
    
    df.rename(columns={'Lineitem name':'Lineitem_name'}, inplace=True)
    df.rename(columns={'Lineitem quantity':'Lineitem_quantity'}, inplace=True)
    dff = df[[ 'Name', 'Lineitem_name', 'Lineitem_quantity']]
    #duplicate rows where one item is bought multiple times
    dff = dff.loc[dff.index.repeat(dff.Lineitem_quantity)]
    dff = dff[[ 'Name', 'Lineitem_name']]
    numbitemsOrdered = len(dff)
    
    numbOrders = len(dff.groupby('Name'))
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
    uniqueProductsWithVar = len(dff['Lineitem_name'].unique())

    #get number of unique products sold (with variante not included as separate)
    #Take variante out
    dff3 = dff
    dff3['Lineitem_name'] = dff3['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )
    uniqueProductsNoVar = len(dff3['Lineitem_name'].unique())

    #get number of unique product inside all grouped orders (with variante included as separated)
    UniqueProdInGroupOrdersWithVar = len(dff['Lineitem_name'].unique())

    #get number of unique product inside all grouped orders (with variante not included as separated)
    dff3Grouped = dff3.groupby('Name').filter(lambda g: len(g) > 1)
    UniqueProdInGroupOrdersNoVar = len(dff3['Lineitem_name'].unique())

    #product most often sold in groups     - with var
    #remove dup
    # dff4 = dff2.drop_duplicates(subset=['Name', 'Lineitem_name'], keep="first")
    # crossWithVar = pd.crosstab(dff4.Name, dff4.Lineitem_name)
    # sumCrossWithVar = crossWithVar.sum(axis=0).sort_values(ascending=False)
    # mostoftenSoldWithVar = pd.DataFrame({'Lineitem_name': sumCrossWithVar.index, 'count':sumCrossWithVar.values})

    #product most often sold in groups     - with no var
    #remove dup
    # dff5 = dff3Grouped.drop_duplicates(subset=['Name', 'Lineitem_name'], keep="first")
    # crossNoVar = pd.crosstab(dff5.Name, dff5.Lineitem_name)
    # sumCrossNoVar = crossNoVar.sum(axis=0).sort_values(ascending=False)
    # mostoftenSoldNoVar = pd.DataFrame({'Lineitem_name': sumCrossNoVar.index, 'count':sumCrossNoVar.values})

    #get highest combinaison (>1)  - with var
    resultWithVar = dff2.groupby(['Name']).agg(lambda g: list(set(combinations(sorted(g), 2))))

    comboMatrixWithVar = pd.DataFrame(Counter(resultWithVar.Lineitem_name.sum()).items(), columns=['combos', 'count'])
    comboMatrixWithVar[['first','second']] = pd.DataFrame(comboMatrixWithVar.combos.values.tolist(), index= comboMatrixWithVar.index)
    comboMatrixWithVar = comboMatrixWithVar.sort_values('count', ascending=False)
    comboMatrixWithVar = comboMatrixWithVar.iloc[:, 1: 4]

    
    #get highest combinaison (>1)  - no var

    resultNoVar = dff3Grouped.groupby(['Name']).agg(lambda g: list(set(combinations(sorted(g), 2))))

    comboMatrixNoVar = pd.DataFrame(Counter(resultNoVar.Lineitem_name.sum()).items(), columns=['combos', 'count'])
    comboMatrixNoVar[['first','second']] = pd.DataFrame(comboMatrixNoVar.combos.values.tolist(), index= comboMatrixNoVar.index)
    comboMatrixNoVar = comboMatrixNoVar.sort_values('count', ascending=False)
    comboMatrixNoVar = comboMatrixNoVar.iloc[:, 1: 4]

    global alldata
    alldata.extend((numbOrders, numbitemsOrdered, numbGroupedOrders, averageBasket, averageGroupedBasket, uniqueProductsWithVar, uniqueProductsNoVar,
    UniqueProdInGroupOrdersWithVar, UniqueProdInGroupOrdersNoVar, comboMatrixWithVar, comboMatrixNoVar))

    #put df to jason to pass o other routemostoftenSoldWithVar, mostoftenSoldNoVar
    # session["data"] = comboMatrixNoVar.to_json()
    return alldata


# @app.route('/',methods=['GET', 'POST'])
# def upload():
#     if request.method == 'POST':
#         global alldata
#         alldata = []
#         df = pd.read_csv(request.files.get('fileupload'))
#         try:
#             alldata = get_data_set_up(df)
#             return render_template('/index.html', numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#                 averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#                 UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], comboMatrixWithVar = alldata[9], comboMatrixNoVar = alldata[10])
#         except:
#             return 'There was a mistake, your file doesnt seem to be in the right format'
        
#     return render_template('/index.html')

    

# @app.route('/combination',methods=['GET', 'POST'])
# def comb():
#     global alldata
#     if request.method == 'POST':
#         r = request.form['contentSearch']
#         try: 
#             if 'variante' in request.form:
#                 mybestmat = FindBestMatch(alldata[11], r)
#                 # checkbox = request.form['variante']
#                 # if len(mybestmat) > 0:
#                 #     return render_template('/combination.html', numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#                 #     averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#                 #     UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], mostoftenSoldWithVar = alldata[9], 
#                 #     mostoftenSoldNoVar = alldata[10], comboMatrixWithVar = alldata[11], comboMatrixNoVar = alldata[12], mybestmat = mybestmat, checkbox = checkbox)
#                 # else:
#                 #     return 'there was a mistake, it seems the product you entered doesnt have any match'
#             else:
#                 mybestmat =  FindBestMatch(alldata[12], r)
#                 # checkbox = 'not checked'
#             # time.sleep(2)
            
#             return render_template('/combination.html', numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#                 averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#                 UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], mostoftenSoldWithVar = alldata[9], 
#                 mostoftenSoldNoVar = alldata[10], comboMatrixWithVar = alldata[11], comboMatrixNoVar = alldata[12], mybestmat = mybestmat)
        
#             # if len(mybestmat) > 0:
#             #     return render_template('/combination.html', numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#             #     averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#             #     UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], mostoftenSoldWithVar = alldata[9], 
#             #     mostoftenSoldNoVar = alldata[10], comboMatrixWithVar = alldata[11], comboMatrixNoVar = alldata[12], mybestmat = mybestmat, checkbox = checkbox)
#         except:
#             return "There was a mistake"
#     else:                      
#         return render_template('/combination.html', numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#             averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#             UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], mostoftenSoldWithVar = alldata[9], 
#             mostoftenSoldNoVar = alldata[10], comboMatrixWithVar = alldata[11], comboMatrixNoVar = alldata[12])
        
@app.route("/")
def init():
    return render_template('index.html')

@app.route('/loading', methods=['GET','POST'])
def load():
    if request.method == 'POST':
        global thread
        global finished
        finished = False
        df = pd.read_csv(request.files.get('fileupload'))
        def long_running_task(**kwargs):
                your_params = kwargs.get('post_data', {})
                print("Starting long task")
                global alldata
                
                # finished = False
                alldata = []
                alldata = get_data_set_up(df)
                global finished
                finished = True
        thread = threading.Thread(target=long_running_task, kwargs={
                            'post_data': alldata})
        thread.start()
        return render_template('loading.html')
    return render_template('index.html')

@app.route('/result')
def result():
    global alldata
    return render_template('/index.html', numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
            averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
            UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], comboMatrixWithVar = alldata[9], comboMatrixNoVar = alldata[10])

@app.route('/status')
def thread_status():
    """ Return the status of the worker thread """
    return jsonify(dict(status=('finished' if finished else 'running')))


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

if __name__ == '__main__':
    
    app.run(debug=True)