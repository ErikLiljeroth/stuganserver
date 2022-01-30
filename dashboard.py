from tokenize import Number
from turtle import title
import streamlit as st
import pandas as pd
import numpy as np
import mysql.connector as msc
import toml
from datetime import datetime, timedelta
import plotly_express as px

st.set_page_config(layout="wide")

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Reading data
toml_data = toml.load("./.streamlit/secrets.toml")
# saving each credential into a variable
HOST_NAME = toml_data['mysql']['host']
DATABASE = toml_data['mysql']['database']
PASSWORD = toml_data['mysql']['password']
USER = toml_data['mysql']['user']
PORT = toml_data['mysql']['port']

# Using the variables we read from secrets.toml
mydb = msc.connect(host=HOST_NAME, database=DATABASE,user=USER, passwd=PASSWORD, use_pure=True, port=PORT)

@st.cache
def sql_request():
    return pd.read_sql('SELECT * FROM temphumi;', mydb)

@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

# what is received is dataframe
all_data = sql_request()
all_data['dtg'] = pd.to_datetime(all_data['dtg'], format="%Y-%d-%m %H:%M:%S")
all_data.sort_values(by='dtg')

# Prepare downloadable csv
csv = convert_df(all_data)

# --- Compute yesterday's data if exists ---
if all_data.empty:
    current_data['temperature'] = None
    current_data['humidity'] = None
else:
    current_data = all_data.iloc[-1]
    yesterday = current_data.dtg - timedelta(hours=24)
    yesterday_data = all_data.loc[all_data['dtg'] == yesterday].squeeze(axis=0)

#----------------------------
#------- Render App ---------
#----------------------------

# Plot title
buffh1, header, buffh2 = st.columns([0.3,6,0.3])
header.title('Data krypgrund sommarstugan')

# Sidebar & filtering logic for specific data
month = 'alla månader'
month_dict = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'maj':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'okt':10, 'nov':11, 'dec':12}
years = list(pd.DatetimeIndex(all_data['dtg']).year) # Filter for unique years
unique_years = list(np.unique(years))
unique_years.insert(0, 'all data')
st.sidebar.markdown('**Välj särkilt år och månad för data:**')
year  = st.sidebar.selectbox('Välj år', unique_years, index=0) #index=unique_years.index(unique_years[-1])
if (year != 'all data'):
    month = st.sidebar.selectbox('Välj månad', ['alla månader','jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'])
    print(f'year: {year}, month= {month}')

# --- Plot metrics ---
header.write('Appen visar aktuell och historisk data för temperatur till vänster och luftfuktighet till höger.\n Under den nuvarande datan finns förändringen jämfört med samma tidpunkt föregående dygn.')


buff1, c1, buff2, c2, buff3 = st.columns([0.3,3,0.1,3,0.3])

if not yesterday_data.empty:
    delta_temp = np.round(current_data.temperature - yesterday_data.temperature, decimals=1)
    delta_humi = np.round(current_data.relative_humidity - yesterday_data.relative_humidity, decimals=1)
    if abs(delta_temp) > 0:
        c1.metric('temperatur just nu', f'{current_data.temperature}\N{DEGREE SIGN}C', f'{delta_temp}\N{DEGREE SIGN}C', delta_color='off')
    if abs(delta_humi) > 0:
        c2.metric('relativ luftfuktighet just nu', f'{current_data.relative_humidity}%', f'{delta_humi} %-enheter', delta_color='off')
else:
    temp = current_data['temperature']
    humi = current_data['humidity']
    c1.metric('temperatur just nu', f'{temp}\N{DEGREE SIGN}C' )
    c2.metric('relativ luftfuktighet just nu', f'{humi}%')

if year == 'all data':
    df_temp = all_data[['dtg', 'temperature']].copy()
    df_humidity = all_data[['dtg', 'relative_humidity']]
elif month == 'alla månader':
    filtered_data = all_data[all_data['dtg'].dt.year == year]
    df_temp = filtered_data[['dtg', 'temperature']].copy()
    df_humidity = filtered_data[['dtg', 'relative_humidity']]
else:
    filtered_data = all_data[all_data['dtg'].dt.month == month_dict[month]]
    df_temp = filtered_data[['dtg', 'temperature']].copy()
    df_humidity = filtered_data[['dtg', 'relative_humidity']]

if df_temp.empty or df_humidity.empty:
    c1.write('ingen data...')
    c2.write('ingen data...')
else:
    fig_temp = px.line(df_temp, x='dtg', y='temperature',markers=True, labels={'dtg':'tid', 'temperature':'temperatur'})
    fig_temp['data'][0]['line']['color']='rgb(202,71,47)'
    fig_temp.update_layout(showlegend=True)
    fig_humidity = px.line(df_humidity, x='dtg', y='relative_humidity', markers=True, labels={'dtg':'tid', 'relative_humidity':'relativ luftfuktighet'})
    fig_humidity['data'][0]['line']['color']='rgb(11,132,165)'
    c1.plotly_chart(fig_temp, use_container_width = True)
    c2.plotly_chart(fig_humidity, use_container_width = True)


# Separating line
text = '''
---
'''

st.markdown(text)

# Footer
bufff1, footer, bufff2 = st.columns([3,1,3])

# Render download-button for data
footer.download_button(
    "Ladda ner all data",
    csv,
    "stugan_data.csv",
    "text/csv",
    key='download-csv'
)