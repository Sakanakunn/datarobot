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


@route('/plot', method='POST')
def convert(name='Stranger'):
    # Get the data
    def convert_df(post_name):
        csv_str = str(request.POST[post_name].file.read(), 'utf-8')
        array_str = csv_str.split('\r\n')
        array_pre = []
        for i in array_str:
            array_pre.append(i.split(','))
        array_fin_dic = {}

        for i in array_pre[0]:
            array_fin_dic[str(i)] = ''

        array_pre.pop(0)
        array_pre.pop(-1)
        array_values = []
        array_fin_values = []

        for idx, i in enumerate(array_fin_dic):
            for j in array_pre:
                array_values.append(j[idx])
            array_fin_values.append(array_values)
            array_values = []

        for idx, key in enumerate(array_fin_dic):
            array_fin_dic[key] = array_fin_values[idx]
        df = pd.DataFrame.from_dict(array_fin_dic)
        df_html = pd.DataFrame.from_dict(array_fin_dic).head().to_html()
        return df,df_html
    global df_train_preprocess
    global df_score_preprocess
    df_train_preprocess,df_train_html = convert_df('train')
    df_score_preprocess,df_score_html = convert_df('score')
    pdb.set_trace()
    return template('confirm',train = df_train_html,score = df_score_html)

@get('/index')
def datacheck():
    return template('index')

@post('/complete')
def data_result():
    ## TODO:関数をフォームの入力データで呼び出せる構成にする
    ## テストデータのパス
    ## TODO:テストデータ(DataFrameをpostから受け取る)
    train_data = df_train_preprocess
    ##Class Mapping
    mapping_fl = False
    ## TODO:(スコアリング列のカラム数を受け取る)
    ## スコアリング列のカラム番号
    scoring_columns = request.POST['class_column']
    ## TODO:(除外するカラム名を受け取る)
    ## 除外するカラム名
    exclude_columns_names = request.POST['ex_column']
    ## スコアリングデータのパス
    score_data =  df_score_preprocess
    result = main.main(train_data,scoring_columns,mapping_fl,score_data)
    ex_impute = result[0].to_html()
    ex_rfe = result[1].to_html()
    ex_result = result[2].to_html()
    return template('result', result = ex_result , pre = ex_impute, rfe = ex_rfe)

run(host='localhost', port=8080, debug=True)