import pandas as pd
import numpy as np
import akshare as ak
import tushare as ts

from scipy import stats
import streamlit as st
import plotly.express as px

import time as time
from datetime import datetime,timedelta


################### 读取数据 ###################

df_weekly_metric_index=pd.read_csv('./index_weekly_metric.csv',converters={'trade_date':str})

################### I.总体固定汇总 ###################
today = datetime.today()
dt_L3Yr=(today + timedelta(days=-1080)).strftime('%Y%m%d')
trade_date_max=df_weekly_metric_index['trade_date'].max()

df_sum_1=df_weekly_metric_index.loc[(df_weekly_metric_index['trade_date']==trade_date_max),['index_code','名称','pe_ttm','pb']].reset_index(drop=True)

index_name_list=list(set(df_weekly_metric_index['名称']))
for i in index_name_list:
  for j in ['pe_ttm','pb']:
    tmp=df_weekly_metric_index.loc[(df_weekly_metric_index['名称']==i) & (df_weekly_metric_index['trade_date']>=dt_L3Yr),j]
    x=float(df_sum_1.loc[df_sum_1['名称']==i,j])
    x_pct=stats.percentileofscore(tmp, x)
    df_sum_1.loc[df_sum_1['名称']==i,"3年分位数_"+j]=x_pct

st.markdown('## I.整体统计')
st.text('最新数据点：'+trade_date_max)
st.table(df_sum_1[['index_code','名称','pe_ttm','3年分位数_pe_ttm','pb','3年分位数_pb']])


################### II.单指数分析 ###################

st.markdown('## II.指数分析')

################### 输入参数 ###################

col1, col2 = st.columns(2)
### 指数选择
with col1:
  index_name_selected=st.selectbox('选择指数',index_name_list)

### 指标选择

metric_list=['pe_ttm','pb']

with col2:
  metric_selected=st.selectbox('选择指标',metric_list)

### 时间参数

today = datetime.today()
dt_start =  today + timedelta(days=-720)


col3, col4 = st.columns(2)

with col3:
  dt_start_2=str(st.date_input('开始日期', dt_start)).replace('-','')
  
with col4:
  dt_end_2=str(st.date_input('结束日期', today)).replace('-','')



################### 数据处理 ###################

df_weekly_metric_index_2=df_weekly_metric_index[(df_weekly_metric_index['trade_date']>=dt_start_2) & (df_weekly_metric_index['trade_date']<=dt_end_2) & (df_weekly_metric_index['名称']==index_name_selected)]
df_weekly_metric_index_2['50分位']=df_weekly_metric_index_2[metric_selected].quantile(0.5)
df_weekly_metric_index_2['75分位']=df_weekly_metric_index_2[metric_selected].quantile(0.75)
df_weekly_metric_index_2['25分位']=df_weekly_metric_index_2[metric_selected].quantile(0.25)

################### 数据展示 ###################


### 分指数汇总 ###


st.markdown('#### '+index_name_selected+' '+metric_selected)

fig1 = px.line(df_weekly_metric_index_2, x = 'trade_date', y = [metric_selected,'25分位','50分位','75分位'])
st.plotly_chart(fig1)


