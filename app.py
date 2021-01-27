from flask import Flask, render_template, url_for, request, redirect, session, jsonify, make_response
import csv
import io
import pandas as pd
import numpy as np
from collections import Counter
from itertools import combinations
import os
import threading

app = Flask(__name__)
alldata = [] 
def get_data_set_up(df):
    df.rename(columns={'Lineitem name':'Lineitem_name'}, inplace=True)
    df.rename(columns={'Lineitem quantity':'Lineitem_quantity'}, inplace=True)
    dff = df[[ 'Name', 'Lineitem_name', 'Lineitem_quantity', 'Email']]
    mydata = df[[ 'Name', 'Lineitem_name', 'Lineitem_quantity', 'Email']]
    dff = dff.loc[dff.index.repeat(dff.Lineitem_quantity)]
    dff = dff[[ 'Name', 'Lineitem_name', 'Email']]

    mostoftenAll = dff[['Name', 'Lineitem_name']]
    mostoftenAll = mostoftenAll.groupby('Lineitem_name').count().reset_index()
    mostoftenAll.columns = ['Lineitem_name', 'count']
    mostoftenAll = mostoftenAll.sort_values('count', ascending=False)


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
    UniqueProdInGroupOrdersWithVar, UniqueProdInGroupOrdersNoVar,  mydata, comboMatrixWithVar, mostoftenAll))
    return alldata

global tab
global comboMatrixNoVarEmail
global comboMatrixNoVar
global comboMatrixWithVarEmail
global dataNoVar
global mostoftenSoldWithVar
global mostoftenSoldNoVar
global mostsoldAllNoVar
global l
global l2
global mybestmat
tab = "combo-content"
comboMatrixNoVarEmail = None
comboMatrixNoVar = None
comboMatrixWithVarEmail = None
mostoftenSoldWithVar = None
mostoftenSoldNoVar = None
mostsoldAllNoVar = None
l = []
l2 = []
mybestmat = None

@app.route('/',methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        global alldata
        global data
        global tab
        global comboMatrixNoVarEmail
        global comboMatrixNoVar
        global comboMatrixWithVarEmail
        global dataNoVar
        global mostoftenSoldWithVar
        global mostoftenSoldNoVar
        global mostsoldAllNoVar
        global l
        global l2
        global mybestmat

        if request.files.get('fileupload', None):
            df = pd.read_csv(request.files.get('fileupload'))
            alldata = []
            try:
                alldata = get_data_set_up(df)
                mydata = alldata[9]
                data = mydata.copy()
                data = data.loc[mydata.index.repeat(data.Lineitem_quantity)]
                data = data[[ 'Name', 'Lineitem_name', 'Email']]
                dataNoVar = data.copy()
                dataNoVar['Lineitem_name'] = dataNoVar['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )
                
                return render_template('/dynamic.html', numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                    averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                    UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8],  comboMatrixWithVar = alldata[10], tab = tab, mostoftenAll=alldata[11], checkedNoVar = "", checkCusto = "" ) 
            except:
                return 'There was a mistake, your file doesnt seem to be in the right format'
        elif request.is_json: 
                r = request.get_json()
                tab = r.get("tab")
                print(tab)
        
        elif tab == "combo-content":
            print(request.form.getlist('my_checkbox'))
            l =  request.form.getlist('my_checkbox')

            if "no var" in l and "custo" in l:
                if comboMatrixNoVarEmail is None:
                    # dataNoVar = data
                    # dataNoVar['Lineitem_name'] = dataNoVar['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )
                    comboMatrixNoVarEmail = Findmatrixes(dataNoVar.groupby('Email').filter(lambda g: len(g) > 1), 'Email')
                    
                else:
                    print("data no var already exist")
                # if request.form.get("submit_a"):
                
                    # return getCSV(comboMatrixNoVarEmail)
                return render_template('/dynamic.html', data = comboMatrixNoVarEmail, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                    averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                    UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], tab = tab, mostoftenAll=alldata[11], checkedNoVar = "checked", checkedCusto = "checked")
            
            elif 'no var' in l: 
                if comboMatrixNoVar is None:  
                    # data['Lineitem_name'] = data['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )
                    dff3Grouped = dataNoVar.groupby('Name').filter(lambda g: len(g) > 1)
                    comboMatrixNoVar = Findmatrixes(dff3Grouped, 'Name')
                    # c = "checked"
                else:
                    print("data no var already exist")
                return render_template('/dynamic.html', data = comboMatrixNoVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                    averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                    UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], tab = tab, mostoftenAll=alldata[11], checkedNoVar = "checked", checkedCusto = "")
            elif "custo" in l:
                if comboMatrixWithVarEmail is None:
                    comboMatrixWithVarEmail = Findmatrixes(data.groupby('Email').filter(lambda g: len(g) > 1), 'Email')
                return render_template('/dynamic.html', data = comboMatrixWithVarEmail, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                    averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                    UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], tab = tab, mostoftenAll=alldata[11], checkedCusto = "checked", checkedNoVar = ""  )
            else:
                return render_template('/dynamic.html', numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],      
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8],  comboMatrixWithVar = alldata[10], tab = tab, mostoftenAll=alldata[11], checkedNoVar = "", checkedCusto = "") 
        
        
        elif tab == "MostSold-content":
            print(request.form.getlist('my_checkbox_MostSold'))
            l2 =  request.form.getlist('my_checkbox_MostSold')
            
            if "no var mostsold" in l2 and "grouped orders" in l2:
                if mostoftenSoldNoVar is None:
                    mydt = alldata[9][[ 'Name', 'Lineitem_name']]
                    mydt['Lineitem_name'] = mydt['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )        
                    mostoftenSoldNoVar = mostsold(mydt)
                return render_template('/dynamic.html', data2 = mostoftenSoldNoVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], tab =tab, comboMatrixWithVar = alldata[10],checkedNoVarMostSold = "checked", checkedGrouped = "checked"  )
            
            elif "no var mostsold" in l2:
                #a verifier
                if mostsoldAllNoVar is None:
                    mostsoldAllNoVar = alldata[11].copy()
                    mostsoldAllNoVar['Lineitem_name'] = mostsoldAllNoVar['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )  
                    mostsoldAllNoVar = mostsoldAllNoVar.groupby('Lineitem_name').sum().reset_index()
                    mostsoldAllNoVar = mostsoldAllNoVar.sort_values('count', ascending=False)      
                # mostoftenSoldNoVar = mostsold(mostsoldAllNoVar)
                return render_template('/dynamic.html', data2 = mostsoldAllNoVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], tab =tab, comboMatrixWithVar = alldata[10], checkedNoVarMostSold = "checked", checkedGrouped = "" )
            elif "grouped orders" in l2:
                if mostoftenSoldWithVar is None:
                    mostoftenSoldWithVar = mostsold(alldata[9][[ 'Name', 'Lineitem_name']])
                return render_template('/dynamic.html', data2 = mostoftenSoldWithVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], tab =tab, comboMatrixWithVar = alldata[10], checkedNoVarMostSold = "" , checkedGrouped = "checked")
            else:
                return render_template('/dynamic.html', numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                    averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6], comboMatrixWithVar = alldata[10],
                    UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8], tab =tab, mostoftenAll=alldata[11], checkedNoVarMostSold= "" , checkedGrouped = "")
        elif tab == "matchProduct-content":
            if 'contentSearch' in request.form:
                print('ok')
                r = request.form["contentSearch"]
                print(r)
                if 'variante' in request.form:
                    if comboMatrixNoVar is None:  
                    # data['Lineitem_name'] = data['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )
                        dff3Grouped = dataNoVar.groupby('Name').filter(lambda g: len(g) > 1)
                        comboMatrixNoVar = Findmatrixes(dff3Grouped, 'Name')
                    mybestmat = FindBestMatch(comboMatrixNoVar, r)
                else:
                    mybestmat = FindBestMatch(alldata[10], r)
                print(len(mybestmat))
                print(len(alldata[10]))

                return render_template('/dynamic.html', numbOrders = alldata[0], mybestmat = mybestmat, numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
                    averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
                    UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8],  comboMatrixWithVar = alldata[10], tab = tab, mostoftenAll=alldata[11], checkedNoVar = "", checkCusto = "" )   
    return render_template('/index.html')

@app.route('/download', methods=['GET', 'POST'])
def getCSV():
    if "submit_a" in request.form:
        # print(request.form.getlist('my_checkbox'))
        # l =  request.form.getlist('my_checkbox')
        print(l)
        print('button')
        if "no var" in l and "custo" in l:
            resp = make_response(comboMatrixNoVarEmail.to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp 
        elif "no var" in l:
            resp = make_response(comboMatrixNoVar.to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp
        elif "custo" in l:
            resp = make_response(comboMatrixWithVarEmail.to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp
        else:
            resp = make_response(alldata[10].to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp
    if "submit_b" in request.form:
        if "no var mostsold" in l2 and "grouped orders" in l2:
            resp = make_response(mostoftenSoldNoVar.to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp
        elif "no var mostsold" in l2:
            resp = make_response(mostsoldAllNoVar.to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp
        elif "grouped orders" in l2:
            resp = make_response(mostoftenSoldWithVar.to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp
        else:
            resp = make_response(alldata[11].to_csv(index=False))
            resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
            resp.headers["Content-Type"]="text/csv"
            return resp
    if "submit_c" in request.form:
        resp = make_response(mybestmat.to_csv(index=False))
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"]="text/csv"
        return resp


def getmatemailwithvar():
    global alldata
    mydata = alldata[9]
    data = mydata.loc[mydata.index.repeat(mydata.Lineitem_quantity)]
    data = data[[ 'Name', 'Lineitem_name', 'Email']]
    comboMatrixWithVarEmail = Findmatrixes(data.groupby('Email').filter(lambda g: len(g) > 1), 'Email')
    return comboMatrixWithVarEmail

# @app.route("/data", methods=['GET', 'POST'])
# def getinfo():
#     global alldata
#     mydata = alldata[9]
#     data = mydata.loc[mydata.index.repeat(mydata.Lineitem_quantity)]
#     data = data[[ 'Name', 'Lineitem_name', 'Email']]
    
#     if request.method == 'POST':
         
#         if 'comboMatrixWithVar' in request.form:
#             data2 = data.groupby('Name').filter(lambda g: len(g) > 1)
#             comboMatrixWithVar = Findmatrixes(data2,'Name')
#             return render_template('/dynamic.html',cases = CASES, data = comboMatrixWithVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#                 averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#                 UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8] )

#         elif 'No Variante' in request.form:   
#             data['Lineitem_name'] = data['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )
#             dff3Grouped = data.groupby('Name').filter(lambda g: len(g) > 1)
#             comboMatrixNoVar = Findmatrixes(dff3Grouped, 'Name')
#             return render_template('/dynamic.html', cases = CASES, data = comboMatrixNoVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#                 averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#                 UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8],  tab = "combo")
# # comboMatrixWithVar = alldata[10]
#         elif 'comboMatrixWithVarEmail' in request.form:
#             comboMatrixWithVarEmail = Findmatrixes(data.groupby('Email').filter(lambda g: len(g) > 1), 'Email')
#             return render_template('/dynamic.html',cases = CASES, data = comboMatrixWithVarEmail, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#                 averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#                 UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8] )

#         elif 'comboMatrixNoVarEmail' in request.form:
#             data['Lineitem_name'] = data['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )
#             comboMatrixNoVarEmail = Findmatrixes(data.groupby('Email').filter(lambda g: len(g) > 1), 'Email')
#             return render_template('/dynamic.html',cases = CASES, data = comboMatrixNoVarEmail, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#                 averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#                 UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8] )

#         elif 'mostoftenSoldWithVar' in request.form:
#             mostoftenSoldWithVar = mostsold(mydata[[ 'Name', 'Lineitem_name']])
#             return render_template('/dynamic.html',cases = CASES, data2 = mostoftenSoldWithVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#                 averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#                 UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8] )

#         elif 'mostoftenSoldNoVar' in request.form:
#             mydt = mydata[[ 'Name', 'Lineitem_name']]
#             mydt['Lineitem_name'] = mydt['Lineitem_name'].apply(lambda x: x.rsplit(' -', 1)[0] )        
#             mostoftenSoldNoVar = mostsold(mydt)

#             return render_template('/dynamic.html',cases = CASES, data2 = mostoftenSoldNoVar, numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#                 averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#                 UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8] )

#     return render_template('/dynamic.html', cases = CASES,numbOrders = alldata[0], numbitemsOrdered= alldata[1], numbGroupedOrders= alldata[2], averageBasket = alldata[3],
#                 averageGroupedBasket = alldata[4], uniqueProductsWithVar = alldata[5], uniqueProductsNoVar = alldata[6],
#                 UniqueProdInGroupOrdersWithVar = alldata[7], UniqueProdInGroupOrdersNoVar = alldata[8])



# @app.route('/result', methods=["GET", "POST"])
# def button():
#     global alldata
#     if request.method == "POST":
#         if request.form.get("submit_a"):
#             dftodl = alldata[9]
#             resp = make_response(dftodl.to_csv(index=False))
#             resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
#             resp.headers["Content-Type"]="text/csv"
#             return resp
#         elif request.form.get("submit_b"):
#             dftodl = alldata[10]
#             resp = make_response(dftodl.to_csv(index=False))
#             resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
#             resp.headers["Content-Type"]="text/csv"
#             return resp
#         elif request.form.get("submit_c"):
#             dftodl = alldata[11]
#             resp = make_response(dftodl.to_csv(index=False))
#             resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
#             resp.headers["Content-Type"]="text/csv"
#             return resp
#         elif request.form.get("submit_d"):
#             dftodl = alldata[12]
#             resp = make_response(dftodl.to_csv(index=False))
#             resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
#             resp.headers["Content-Type"]="text/csv"
#             return resp


# @app.route('/combination',methods=['GET', 'POST'])
# def comb():
#     global alldata
#     if request.method == 'POST':
#         r = request.form['contentSearch']
#         # try: 
#         if 'variante' in request.form:
#             mybestmat = FindBestMatch(alldata[9], r)
#         else:
#             mybestmat =  FindBestMatch(alldata[10], r)
#         return render_template('/combination.html', mybestmat = mybestmat)
#     return render_template('/index.html')



#get best matches for on speciic product
def FindBestMatch(matrix, item):
  ff =  matrix[matrix['first']==item]
  f = matrix[matrix['second']==item]
  f = f.reindex(columns= ['second', 'first', 'count'])
  f.columns = ['first', 'second', 'count']
  fff = pd.concat([f, ff]).drop_duplicates()
  fff = fff.sort_values('count', ascending=False)
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