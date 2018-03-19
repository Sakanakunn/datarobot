from bottle import route,run,get,post,request,template
from sklearn import svm
from sklearn import datasets
import pandas as pd
import numpy as np
import csv
import cgi
import codecs
import pdb

@route('/plot',method = 'POST')
def greet(name='Stranger'):
    # Get the data
    csv_str = str(request.POST['upload'].file.read(),'utf-8')
    array_str = csv_str.split('\r\n')
    array_pre = []
    ## todo iris以外のデータでout of Rangeになるバグを修正する
    for i in array_str:
        array_pre.append(i.split(','))
    array_fin_dic = {}
    for idx1,i in enumerate(array_pre[0]):
        values = []
        for idx2,t in enumerate(array_pre):
            if idx2 != 0:
                values.append(t[idx1])
        array_fin_dic[str(i)] = values

    df = pd.DataFrame.from_dict(array_fin_dic).head().to_html()
    return template('confirm',name=df)

@get('/index')
def datacheck():
    return template('index')

@get('/complete')
def data_result():
    return template('result')

run(host='localhost', port=8080, debug=True)