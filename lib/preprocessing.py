## TODO Object型以外にもカテゴリ指定するものがあれば追加で指定できる仕様にする
import pandas as pd
from sklearn.preprocessing import Imputer
from sklearn.feature_selection import RFE
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import auc
from sklearn.metrics import auc
from sklearn.metrics import f1_score
from sklearn import metrics
from sklearn.model_selection import GridSearchCV
import xgboost as xgb

## スコアリング用データのImport
def train_read(CsvPath,score_column):
    train_keys = ['X_train','y_train','all_train_columns','objects_train_columns','objects_dummy_train_columns','dtype_dict']
    X_train = CsvPath.ix[:,CsvPath.columns != score_column]
    train_values = [
    ## 特徴量カラムの読み込み
    X_train
    ## 正解ラベルカラムの読み込み
    ,CsvPath.ix[:,score_column]
    ## 全カラム名のArray
    ,CsvPath.columns.values
    ## Objects型に絞り込んだカラム名のArray
    ,CsvPath.loc[:,extract_objects_columns(CsvPath)].columns
    ## 正解ラベルカラムの読み込み
    ,X_train.loc[:,extract_objects_columns(X_train)].columns
    ## データ型を生成
    ,build_dtype_dict(CsvPath.loc[:, extract_objects_columns(CsvPath)].columns)
    ]
    ## return を dict型で生成
    train_set = dict(zip(train_keys,train_values))
    return train_set

## スコアリング用データのImport
def score_read(CsvPath,dtype_dict):
    score_keys = ['X_score']
    X_score =CsvPath
    score_values = [
    ## 特徴量カラムの読み込み
    X_score
    ]
    ## return を dict型で生成
    score_set = dict(zip(score_keys,score_values))
    return score_set


def extract_objects_columns(df):
    dummy_columns_indexes = []
    for i in range(0, df.shape[1]):
        if df.dtypes[i].str == '|O':
            dummy_columns_indexes.append(True)
        else:
            dummy_columns_indexes.append(False)
    return dummy_columns_indexes

def build_dtype_dict(obj_columns):
    values_dict = []
    for i in range(0, obj_columns.values.size):
        values_dict.append(object)
    print(values_dict)
    dtype_dict = dict(zip(obj_columns.values,values_dict))
    return dtype_dict

def onehot_encode(df,object_columns):
    df_ohe = pd.get_dummies(
        df
        ,dummy_na = True
        ,columns = object_columns
    )
    onehot_set = [
        df_ohe
        ,df_ohe.columns
    ]
    return  onehot_set


def impute_missingvalue(df,dummy_columns):
    imp = Imputer(missing_values = "NaN", strategy = "mean", axis = 0)
    imp.fit(df)
    imputed_df = pd.DataFrame(imp.transform(df),columns = dummy_columns )
    return imputed_df


def feature_selection_rfe(df,y):
    selector = RFE(GradientBoostingClassifier(random_state=1)
                   ,n_features_to_select = 10
                   ,step = .005)
    selector.fit(df, y.as_matrix().ravel())
    df_fin = pd.DataFrame(selector.transform(df)
                          ,columns = df.columns[selector.support_])
    return df_fin

def integrate_columns(train_columns,score_df):
    cols_model = set(train_columns)
    cols_score = set(score_df.columns)
    diff1 = cols_model - cols_score
    diff2 = cols_score - cols_model
    df_cols_m = pd.DataFrame(None,columns = train_columns,dtype = float)
    df_cols_m_conc = pd.concat([df_cols_m,score_df])
    df_cols_m_conc_ex = df_cols_m_conc.drop(list(diff2),axis = 1)
    df_cols_m_conc_ex.loc[:, list(diff1)] = df_cols_m_conc_ex.loc[:, list(diff1)].fillna(0, axis=1)
    df_cols_m_conc_ex_reorder = df_cols_m_conc_ex.reindex(train_columns, axis=1)
    return df_cols_m_conc_ex_reorder

def x_check(df_tr,df_sc):
    print(df_tr.info())
    print(df_sc.info())
    print(df_tr.head())
    print(df_sc.head())
    print(set(df_tr.columns.values) - set(df_sc.columns.values))

def build_pipeline(classifiers,classifier_pipe_names):
    pipelines = []
    for i in classifiers:
        pipelines.append(Pipeline([('scl',StandardScaler()),('est',i)]))
    pipelines_dict = dict(zip(classifier_pipe_names,pipelines))
    return pipelines_dict

def train_pipeline_with_grid(pipeline_dict,X_train,y_train):
    # パラメータグリッドの設定
    grid_parameters = []
    grid_parameters.append({'est__C': range(1,100,1), 'est__penalty': ['l1', 'l2']})
    grid_parameters.append({'est__n_estimators': range(1,100,2)
                            ,'est__criterion': ['gini','entropy']})
    grid_parameters.append({'est__n_estimators': range(1,100,2)
                            ,'est__subsample': [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]})
    grid_parameters.append({'est__learning_rate': [0.1, 0.3, 0.5],
              'est__max_depth': [2, 3, 5, 10],
              'est__subsample': [0.5, 0.8, 0.9, 1]
              })
    trained_pipeline_dict = {}

    for i,j in zip(pipeline_dict.keys(),grid_parameters):
        print(y_train)
        print(pipeline_dict[i])
        print(j)
        gs = GridSearchCV(estimator=pipeline_dict[i], param_grid=j, scoring='f1', cv=3, n_jobs = -1)
        trained_pipeline_dict[i] = gs.fit(X_train,y_train.as_matrix().ravel())
    return trained_pipeline_dict

def split_holdout(X,y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    return X_train,y_train,X_test,y_test

def Scoring_TrainedModel(trained_pipeline_dict,X_test,y_test):
    alg_names = []
    accuracy_scores = []
    roc_scores = []
    f1_scores = []
    result_dict = {}
    for key in trained_pipeline_dict.keys():
        alg_names.append(key)
        accuracy_scores.append(float(accuracy_score(y_test.as_matrix().ravel(),trained_pipeline_dict[key].predict(X_test))))
        f1_scores.append(float(f1_score(y_test.as_matrix().ravel(), trained_pipeline_dict[key].predict(X_test))))
        fpr, tpr, thresholds = metrics.roc_curve(y_test.as_matrix().ravel(), trained_pipeline_dict[key].predict(X_test))
        roc_scores.append(metrics.auc(fpr, tpr))
    result_dict['0_alg_name'] = alg_names
    result_dict['1_accuracy_score'] = accuracy_scores
    result_dict['2_auc_score'] = roc_scores
    result_dict['3_F1_score'] = f1_scores
    result_dict = pd.DataFrame.from_dict(result_dict)

    return result_dict