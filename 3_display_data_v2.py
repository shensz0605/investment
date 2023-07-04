import pandas as pd
import numpy as np

import scipy
from scipy import stats
import streamlit as st
import plotly.express as px

import time as time
from datetime import datetime,timedelta


st.set_page_config(
        page_title="指数分析",
)

################### 读取数据 ###################

df_weekly_metric_index=pd.read_csv('./index_weekly_metric.csv',converters={'trade_date':str})
df_weekly_metric_stock=pd.read_csv('./stock_weekly_metric.csv',converters={'trade_date':str})
df_fund_index_pct=pd.read_csv('./fund_index_pct.csv')


################### I.总体固定汇总 ###################

#today = datetime.today()
#dt_L3Yr=(today + timedelta(days=-1080)).strftime('%Y%m%d')

trade_date_max=df_weekly_metric_index['trade_date'].max()
dt_L3Yr=(pd.to_datetime(trade_date_max)+ timedelta(days=-1095)).strftime('%Y%m%d')

df_sum_1=df_weekly_metric_index.loc[(df_weekly_metric_index['trade_date']==trade_date_max),['index_code','名称','close','pe_ttm','pb']].reset_index(drop=True)


index_name_list=list(set(df_weekly_metric_index['名称']))
for i in index_name_list:
  for j in ['close','pe_ttm','pb']:
    tmp=df_weekly_metric_index.loc[(df_weekly_metric_index['名称']==i) & (df_weekly_metric_index['trade_date']>=dt_L3Yr),j]
    x=float(df_sum_1.loc[df_sum_1['名称']==i,j])
    x_pct=round(stats.percentileofscore(tmp, x),2)
    df_sum_1.loc[df_sum_1['名称']==i,"3年分位数_"+j]=x_pct

st.markdown('## I.整体统计')
st.text('最新数据点：'+trade_date_max)
st.write(df_sum_1)
#st.write(df_sum_1[['index_code','名称','close','3年分位数_close','pe_ttm','3年分位数_pe_ttm','pb','3年分位数_pb']].style.hide_index().format({"close":"{:.2f}","3年分位数_close":"{:.2f}","pe_ttm":"{:.2f}","3年分位数_pe_ttm":"{:.2f}","pb":"{:.2f}","3年分位数_pb":"{:.2f}"}).to_html()\
#         ,unsafe_allow_html=True)



################### II.单指数分析 ###################

st.markdown('## II.指数分析')

################### 输入参数 ###################

col1, col2 = st.columns(2)
### 指数选择
with col1:
  index_name_selected=st.selectbox('选择指数',index_name_list)

### 指标选择

metric_list=['close','pe_ttm','pb']

with col2:
  metric_selected=st.selectbox('选择指标',metric_list)

### 时间参数

#today = datetime.today()
#dt_start =  today + timedelta(days=-1080)
dt_start =(pd.to_datetime(trade_date_max)+ timedelta(days=-1095))
dt_end = pd.to_datetime(trade_date_max)

col3, col4 = st.columns(2)

with col3:
  dt_start_2=str(st.date_input('开始日期', dt_start)).replace('-','')
  
with col4:
  dt_end_2=str(st.date_input('结束日期', dt_end)).replace('-','')



################### 数据处理 ###################

df_weekly_metric_index_2=df_weekly_metric_index[(df_weekly_metric_index['trade_date']>=dt_start_2) & (df_weekly_metric_index['trade_date']<=dt_end_2) & (df_weekly_metric_index['名称']==index_name_selected)]
df_weekly_metric_index_2['50分位']=df_weekly_metric_index_2[metric_selected].quantile(0.5)
df_weekly_metric_index_2['75分位']=df_weekly_metric_index_2[metric_selected].quantile(0.75)
df_weekly_metric_index_2['25分位']=df_weekly_metric_index_2[metric_selected].quantile(0.25)

################### 数据展示 ###################


### 分指数汇总 ###


st.markdown('#### '+index_name_selected+'：'+metric_selected)

fig1 = px.line(df_weekly_metric_index_2, x = 'trade_date', y = [metric_selected,'25分位','50分位','75分位'])
fig1.update_xaxes(dtick=7)

st.plotly_chart(fig1)

### 指数对应股票分析 ###

top_n = st.radio("按市值TOP ",(5,10),horizontal=True)

df_weekly_metric_stock_2=df_weekly_metric_stock.loc[(df_weekly_metric_stock['名称']==index_name_selected) & (df_weekly_metric_stock['trade_date']>=dt_start_2) & (df_weekly_metric_stock['trade_date']<=dt_end_2),\
                       ['con_code','name','trade_date','total_mv',metric_selected]].sort_values(['con_code','name','trade_date',metric_selected]).reset_index(drop=True)
df_weekly_metric_stock_2['total_mv_pct']=df_weekly_metric_stock_2['total_mv']/df_weekly_metric_stock_2.groupby(['trade_date'])['total_mv'].transform('sum')

tmp=df_weekly_metric_stock_2.groupby('con_code')['total_mv'].sum().reset_index(drop=False).sort_values('total_mv',ascending=False)
top_stock_list=list(tmp['con_code'].head(top_n))

df_weekly_metric_stock_3=df_weekly_metric_stock_2[df_weekly_metric_stock_2['con_code'].isin(top_stock_list)].reset_index(drop=True)

#填充缺失的trade date
tmp_1=list(df_weekly_metric_stock_3['trade_date'].unique())
tmp_2=df_weekly_metric_stock_3[['con_code','name']].drop_duplicates().reset_index(drop=True)

test=pd.DataFrame()

for i in list(tmp_2['con_code']):
    tmp=pd.DataFrame(tmp_1).rename(columns={0:'trade_date'})
    name=list(tmp_2.loc[tmp_2['con_code']==i,'name'])[0]
    tmp['con_code']=i
    tmp['name']=name
    test=pd.concat([test,tmp])
 
df_weekly_metric_stock_3=pd.merge(df_weekly_metric_stock_3[[i for i in df_weekly_metric_stock_3.columns if i!='name']],test,on=['trade_date','con_code'],how='right').sort_values(['con_code','trade_date'])
#st.table(df_weekly_metric_stock_3[df_weekly_metric_stock_3['con_code']=='600585.SH'])

#指标over time
st.markdown('#### '+index_name_selected+'对应股票：'+metric_selected)

fig2 = px.line(df_weekly_metric_stock_3, x = 'trade_date', y = metric_selected, color='name')
fig2.update_xaxes(dtick=7)
st.plotly_chart(fig2)

#市值占比
st.markdown('#### '+index_name_selected+'对应股票：市值占比')

fig3 = px.area(df_weekly_metric_stock_3, x = 'trade_date', y = 'total_mv_pct', color='name')
fig3.update_xaxes(dtick=7)
st.plotly_chart(fig3)


################### III.基金推荐 ###################

st.markdown('## III.基金推荐')

top_fund_n = st.radio("指数成分TOP ",(5,10),horizontal=True)

st.write(df_fund_index_pct[['ts_code','fund_name',index_name_selected]].sort_values(index_name_selected,ascending=False).rename(columns={index_name_selected:index_name_selected+'_占比'}).head(top_fund_n))
#st.write(df_fund_index_pct[['ts_code','fund_name',index_name_selected]].sort_values(index_name_selected,ascending=False).rename(columns={index_name_selected:index_name_selected+'_占比'}).head(top_fund_n)\
#         .style.hide_index().format({index_name_selected+'_占比':"{:.2f}"}).bar(subset=[index_name_selected+'_占比'], align="mid").to_html(),unsafe_allow_html=True)
