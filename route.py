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
    array_fin = []
    for i in array_str:
        array_fin.append(i.split(','))

    pdb.set_trace()
    df = pd.DataFrame(array_str).to_html()
    return template(df,name=name,pd=df)

@get('/index')
def datacheck():
    return template('index')


@get('/complete')
def data_result():
    return template('result')

run(host='localhost', port=8080, debug=True)