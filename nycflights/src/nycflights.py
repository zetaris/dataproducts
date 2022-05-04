import streamlit as st
import pandas as pd
import numpy as np
import jaydebeapi
import datetime
import altair as alt
import plotly.graph_objects as go
import json, random, urllib 
from os.path import dirname, join


# wide page layout
st.set_page_config(page_title='NYC Flights', layout="wide", page_icon='favicon.ico')

# cwd
CWD = dirname(__file__)
# Aviation Edge key
AE_KEY = st.secrets['ae_api_key']
# Weather API key
VC_KEY = st.secrets['vc_api_key']
# zetaris credentials
VDW_USER = st.secrets['vdw_username']
VDW_PASS = st.secrets['vdw_password']
# lightning connection
driver_class = "com.zetaris.lightning.jdbc.LightningDriver"
driver_file = join(CWD, '../../driver/ndp-jdbc-driver-2.1.0.12-driver.jar')
connection_string = 'jdbc:zetaris:clouddatafabric@nycdata.5e3fe4a3.datafabric.zetaris.com/RestClient=https'

@st.cache(allow_output_mutation=True)
def lightning():
    '''create cached lightning connection'''
    # connect to lightning
    con = jaydebeapi.connect(driver_class, connection_string, {'user':VDW_USER, 'password':VDW_PASS}, driver_file)
    return con.cursor()

# session state
if 'airportsFlag' not in st.session_state:
    st.session_state['airportsFlag'] = True

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

# sidebar description
st.sidebar.write(' ')
st.sidebar.write(' ')
st.sidebar.subheader('NYC Flights')
#st.sidebar.subheader('Description')
st.sidebar.info('Enter trip departure date and departure airport.')
st.sidebar.info('Select a flight number to view flight details, estimated airport travel time, and recommended time to leave.')
# data sources
st.sidebar.subheader('Data Sources')
st.sidebar.info('Flight data sourced from Aviation Edge Flight Schedule API.')
st.sidebar.info('Weather data sourced from Visual Crossing Weather API.')
st.sidebar.info('Yellow Taxi Trip data produced by the NYC Taxi and Limousine Commission domain.')


# main columns
c1, c2 = st.columns([2, 3])
c1.write(' ')
c1.write(' ')
#c1.subheader('Travel Details')

def dateChange():
    st.session_state['airportsFlag'] = False
    # set airportSelect to index 0
    st.session_state.airport_selector = airport_list[0]

# date selector
# today date as YYYY-MM-DD
today = datetime.datetime.today()
one_week = pd.to_datetime('today') + pd.Timedelta(days=8)
date = c1.date_input('Travel date', min_value=one_week, value=one_week, on_change=dateChange)
airport_list = ['', 'John F. Kennedy (JFK)', 'La Guardia (LGA)', 'Newark (EWR)']
# airport selection from dropdown menu
airportSelect = c1.selectbox('Airport', airport_list, disabled=st.session_state['airportsFlag'], key='airport_selector')
if airportSelect == '':
    # stop if airport not selected
    st.stop()
airport = airportSelect[-4:-1]

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
####
#st.write(df.head(1))

# extract values
ddf = pd.DataFrame()
ddf['flight'] = df['flight'].apply(lambda x: x['iataNumber']).apply(lambda x: x.upper())
ddf['departure'] = df['departure'].apply(lambda x: x['scheduledTime'])
# exclude records with empty departure value
ddf = ddf[ddf['departure'] != '']
# sort by departure time
ddf = ddf.sort_values(by=['departure'], ascending=False)

# airport
#ddf['airport'] = df['departure'].apply(lambda x: x['iataCode']).apply(lambda x: x.upper())
# terminal
ddf['terminal'] = df['departure'].apply(lambda x: x['terminal'])
# gate
#ddf['gate'] = df['departure'].apply(lambda x: x['gate'])
# airline
#ddf['airline'] = df['airline'].apply(lambda x: x['name'])
# aircraft
#ddf['aircraft'] = df['aircraft'].apply(lambda x: x['modelText'])
# destination
ddf['destination'] = df['arrival'].apply(lambda x: x['iataCode']).apply(lambda x: x.upper())
# arrival time
ddf['arrival'] = df['arrival'].apply(lambda x: x['scheduledTime'])
# dest terminal
#ddf['terminal'] = df['arrival'].apply(lambda x: x['terminal'])

# flights table display
#st.markdown(hide_table_row_index, unsafe_allow_html=True)
#st.table(ddf)    

# flights dataframe display
c2.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
c2.dataframe(ddf)

# delay section
d1, d2 = st.columns([2, 3])
d1.write(' ')
d1.write(' ')
d1.write('**Flight Details**')

# extract flight number and departure time from flights
#flist = [(f.get('flight').get('iataNumber'), f.get('departure').get('scheduledTime')) for f in flights]
flist = ddf[['flight', 'departure']]
# uppercase flight number
flist['flight'] = flist['flight'].apply(lambda x: x.upper())
# insert empty row
flist = flist.append(pd.Series(['', ''], index=flist.columns), ignore_index=True)
# sort flist by departure time
flist = flist.sort_values(by=['departure'], ascending=False)

flightNum = c1.selectbox('Flight number', flist['flight'])
if flightNum == '':
    st.stop()
d1.code('Flight Number: %s' % flightNum)
# get flight details from flights
flight = [f for f in flights if f['flight']['iataNumber'].upper() == flightNum]
###
# st.write(flight)

# sidebar flight details
# st.sidebar.subheader('Flight Details')
# for item in flight:
#     for k, v in item.items():
#         if k in ('weekday', 'codeshared'):
#             continue
#         st.sidebar.write(k)
#         v = dict([(x,y) for x,y in v.items() if y != ''])
#         # convert v to dataframe
#         v = pd.DataFrame(v, index=[0])
#         st.sidebar.dataframe(v)

# chart trip delay
# flight departure tiume
departure = flight[0]['departure']['scheduledTime']
depHour = int(departure[:2])
#departure = datetime.datetime.strptime(departure, '%H:%M')
d1.code('Departure Time: %s' % departure)

# convert detaprture to datetime
departure = datetime.datetime.strptime(departure, '%H:%M')
# subtract 45 mins from departure time
checkin = departure - datetime.timedelta(minutes=45)
d1.write('**When do I need to leave to check-in on time?**')
d1.code('Checkin Time: %s' % (checkin.strftime('%H:%M')))

# hourly probability of delay
hours = ['%02d:00' % x for x in range(0, 24)]
delay = [5.88744589, 5.11280239, 5.2020454 ,  6.03790087,  6.64281398,
        10.88871278,  17.06624028,  28.81446728, 40.74875574, 50.19265685,
        55.78954048,  24.36287642,  12.684458  , 15.35649996, 31.7883561 ,
       48.66204771, 54.51793124, 60.46380269, 54.49042022, 31.69195251,
       12.63465126, 11.93111295, 13.74051771, 16.67041873]

# subset
xvals = hours[depHour-3:depHour+1]
yvals = delay[depHour-3:depHour+1]
seed = int(str(date).replace('-', '')) + int(str(hash(airport))[:6])
np.random.seed(seed)
# create hrs delay dataframe using hours and delay
hrs = pd.DataFrame({'delay':yvals}, index=range(depHour-3,depHour+1))
# add positive delta to delay
hrs['delay'] = hrs['delay'] + np.abs(np.random.normal(0, 10, len(hrs)))
# set upper bound to 95
hrs['delay'] = np.minimum(hrs['delay'], 95)

# calculate travel time
# get depHour delay value from hrs
depDelay = hrs.loc[depHour].get('delay')
#depDelay = hrs[depHour].delay
travelTime = (1 + depDelay / 100) * 60
# convert travel time to hours and minutes
travelTime = datetime.timedelta(minutes=travelTime)
# write travel time as hours and minutes
#d1.write('**Travel Time**')
d1.code('Estimated Travel Time: %s hr %s mins' % (travelTime.seconds // 3600, (travelTime.seconds // 60) % 60))
# subtract travelTime fom checkin time
leaveTime = checkin - travelTime
# write leave time
d1.code('Recommended Leave Time: %s' % leaveTime.strftime('%H:%M'))

# plot hourly probability of delay
#fig, ax = plt.subplots()
#ax.plot(hours, delay, 'r-')
#ax.set_xlabel('Hour')
#ax.set_ylabel('Probability of delay')
#ax.set_title('Hourly probability of delay')
#st.pyplot(fig)

# bar chart hourly probability of delay without legend
#st.bar_chart(delay_df, use_container_width=True)

fig = go.Figure()
# multiple yvals by 0.1
yerrs = [y * sd for (y, sd) in zip(yvals, (0.09, 0.11, 0.12, 0.14))]

# with colorscale
#fig.add_trace(go.Bar(y=yvals, x=xvals, name="delay", marker={'color': yvals, 'colorscale': 'ylorrd'}))
# with error bars
fig.add_trace(go.Bar(y=yvals, x=xvals, name="delay", error_y=dict(type='data', array=yerrs)))
#fig.add_trace(go.Bar(y=hrs['delay'], x=xvals, name="delay"))
# add y vals to each bar with error bars
#fig.add_trace(go.Scatter(y=yvals, x=xvals, name="error", error_y=dict(type='data', array=yerrs)))

# show color bar
#fig.update_layout(coloraxis_showscale=True)
# add yaxis title
fig.update_layout(yaxis_title='Likelihood of Delay')

# set y axis range to 100
#fig.update_layout(yaxis_range=[0, 100])
# set background color to green between y values 0 and 20

fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='#000'
)
d2.plotly_chart(fig, key="delay_chart")
#c2.bar_chart(delay_df, height=400)
