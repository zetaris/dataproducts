import streamlit as st
import pandas as pd
#import numpy as np
import jaydebeapi
import datetime
#import altair as alt
#import plotly.graph_objects as go
import urllib
import json
from os.path import dirname, join


# wide page layout
st.set_page_config(page_title='NYC Flights', layout="wide", page_icon='favicon.ico')

# Weather API key
#VC_KEY = st.secrets['vc_api_key']

# cwd
CWD = dirname(__file__)
# aviation edge key
AE_KEY = st.secrets['ae_api_key']

# sidebar theme
#st.markdown( """ <style> .sidebar .sidebar-content { background-image: linear-gradient(#2e7bcf,#2e7bcf); color: white; } </style> """, unsafe_allow_html=True, )
#st.markdown("""<style> section[data-testid=“stSidebar”] div[class=“css-17eq0hr e1fqkh3o1”] {background-image: linear-gradient(#8993ab,#8993ab);color: white} </style>""",unsafe_allow_html=True)

# sidebar width
# increase sidebar width
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 400px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 400px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# hide table index CSS to inject contained in a string
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """

# hide dataframe index CSS to inject contained in a string
hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """

# main banner
st.image(join(CWD, '../images/nycgo.jpg'), use_column_width=True)

# footer
st.markdown("""<style> footer {visibility: hidden;} </style>""", unsafe_allow_html=True) 

# powered by Zetaris
h1, h2, h3 = st.columns([2, 7, 2])
h1.image(join(CWD, '../images/poweredby.jpg'), use_column_width=True)

# sidebar logo
s1,s2,s3 = st.sidebar.columns([1,5,1])
s2.image(join(CWD, '../images/zetaris.horizontal.png'), use_column_width=True)


# main columns
c1, c2 = st.columns([1, 1])

# date selector
# today date as YYYY-MM-DD
today = datetime.datetime.today()
one_week = pd.to_datetime('today') + pd.Timedelta(days=8)
date = c1.date_input('Travel date', min_value=one_week, value=one_week)
airport_list = ['John F. Kennedy (JFK)', 'La Guardia (LGA)', 'Newark (EWR)']
# airport selection from dropdown menu
airport = c1.selectbox('Airport', airport_list)[-4:-1]

@st.cache
def get_flights(date=None, airport='JFK'):
    'get flights for a given date or today if None'
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    qstring = 'http://aviation-edge.com/v2/public/flightsFuture?key=%s&type=departure&iataCode=%s&date=%s' % (AE_KEY, airport, date)
    result = urllib.request.urlopen(qstring)
    flights = json.loads(result.read().decode('utf-8'))
    return flights


flights = get_flights(date, airport)

df = pd.DataFrame(flights)
# drop weekday
df = df.drop(columns=['weekday'])
#st.write(df.head(1))

# extract values
ddf = pd.DataFrame()
ddf['flight'] = df['flight'].apply(lambda x: x['iataNumber']).apply(lambda x: x.upper())
ddf['departure'] = df['departure'].apply(lambda x: x['scheduledTime'])
# sort by departure time
ddf = ddf.sort_values(by=['departure'])
# airport
ddf['airport'] = df['departure'].apply(lambda x: x['iataCode']).apply(lambda x: x.upper())
# terminal
ddf['terminal'] = df['departure'].apply(lambda x: x['terminal'])
# gate
#ddf['gate'] = df['departure'].apply(lambda x: x['gate'])
# airline
#ddf['airline'] = df['airline'].apply(lambda x: x['name'])
# aircraft
#ddf['aircraft'] = df['aircraft'].apply(lambda x: x['modelText'])
# drop records where departure is None
ddf = ddf.dropna(subset=['departure'])

# flights table display
#st.markdown(hide_table_row_index, unsafe_allow_html=True)
#st.table(ddf)    

# flights dataframe display
c2.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
c2.dataframe(ddf)


# extract flight number and departure time from flights
flist = [(f.get('flight').get('iataNumber'), f.get('departure').get('scheduledTime')) for f in flights]
#flist = [f.get('flight').get('iataNumber').upper() for f in flights]
# sort by departure time
flist.sort(key=lambda x: x[1])
flist = [f[0].upper() for f in flist]
c1.selectbox('Flight number', flist)