from bottle import route,run,get,post,request,template
from sklearn import svm
from sklearn import datasets
import pandas as pd
import numpy as np
import csv
import cgi
import codecs
import pdb
import main

@route('/plot',method = 'POST')
def greet(name='Stranger'):
    # Get the data
    csv_str = str(request.POST['upload'].file.read(),'utf-8')
    array_str = csv_str.split('\r\n')
    array_pre = []
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

@post('/complete')
def data_result():
    str = request.POST['class_column']
    pdb.set_trace()
    ## TODO:関数をフォームの入力データで呼び出せる構成にする
    ## テストデータのパス
    ## TODO:テストデータ(DataFrameをpostから受け取る)
    train_data_path = './data/titanic/train.csv'
    ##Class Mapping
    mapping_fl = False
    ## TODO:(スコアリング列のカラム数を受け取る)
    ## スコアリング列のカラム番号
    scoring_columns = 1
    ## TODO:(除外するカラム名を受け取る)
    ## 除外するカラム名
    exclude_columns_names = ['Name','Ticket','Cabin']
    ## スコアリングデータのパス
    score_data_path =  './data/titanic/test.csv'
    result = main.main(train_data_path,scoring_columns,mapping_fl,exclude_columns_names,score_data_path)
    ex_impute = result[0].to_html()
    ex_rfe = result[1].to_html()
    ex_result = result[2].to_html()
    return template('result', result = ex_result , pre = ex_impute, rfe = ex_rfe)

run(host='localhost', port=8080, debug=True)