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

# date selector
# today date as YYYY-MM-DD
today = datetime.datetime.today()
date = st.date_input('Travel date', min_value=today)
#st.write(date)


@st.cache
def get_flights(date=None):
    'get flights for a given date or today if None'
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    qstring = 'http://aviation-edge.com/v2/public/flightsFuture?key=%s&type=departure&iataCode=JFK&date=%s' % (AE_KEY, date)
    result = urllib.request.urlopen(qstring)
    flights = json.loads(result.read().decode('utf-8'))
    return flights


flights = get_flights(date)

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
ddf['gate'] = df['departure'].apply(lambda x: x['gate'])
# airline
#ddf['airline'] = df['airline'].apply(lambda x: x['name'])
# aircraft
#ddf['aircraft'] = df['aircraft'].apply(lambda x: x['modelText'])

st.write(ddf)

# extract flight number and departure time from flights
flist = [(f.get('flight').get('iataNumber'), f.get('departure').get('scheduledTime')) for f in flights]
# sort by departure time
flist.sort(key=lambda x: x[1])
flist = ['%s %s' % (f[0].upper(), f[1]) for f in flist]
st.selectbox('Flight number', flist)