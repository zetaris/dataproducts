from gc import callbacks
import streamlit as st
import streamlit_option_menu as stom
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
import urllib
import json
import random
from os.path import dirname, join



# wide page layout
st.set_page_config(page_title='NYC Travel', layout="wide", page_icon='favicon.ico')

# Weather API key
VC_KEY = st.secrets['vc_api_key']

# cwd
CWD = dirname(__file__)

h1, h2, h3 = st.columns(3)
h1.title('NYC Travel Portal')
h1.write('Data Product powered by Zetaris Data Mesh')
h3.image('https://www.zetaris.com/hs-fs/hubfs/Zetaris-3D---FINAL-V2.png?width=300&name=Zetaris-3D---FINAL-V2.png')


icon_base = 'https://raw.githubusercontent.com/visualcrossing/WeatherIcons/main/PNG/2nd%%20Set%%20-%%20Color/%s.png'

# date picker
st.sidebar.header('Travel Details')
# select a date between today to two weeks from now
today = pd.to_datetime('today')
# two weeks from now
two_weeks = pd.to_datetime('today') + pd.Timedelta(days=13)
date_range = pd.date_range(start=today, end=two_weeks)
date = st.sidebar.date_input('Travel date', min_value=today, max_value=two_weeks, value=today)
# select an hour of the day
slider_hour = st.sidebar.slider('Hour of the day', 0, 23, today.hour)
# format slider_hour as a hh:mm:ss string
slider_hour_str = "%02d:00:00" % slider_hour
if slider_hour == 0:
    prev_hour_str = "23:00:00"
else:
    prev_hour_str = "%02d:00:00" % (slider_hour - 1)

# add slider_hour to date hours
date_hour = pd.to_datetime(date) + pd.Timedelta(hours=slider_hour)
# write timestamp to sidebar
st.write('**%s**' % date_hour.strftime("%H:%M %A, %B %d, %Y"))
# pickup zones
puzone = st.sidebar.selectbox('Pickup Zone', ['Downtown', 'Uptown', 'Midtown', 'Far East', 'Far West'])

# dropdown menu
airport_list = ['John F. Kennedy (JFK)', 'LaGuardia (LGA)', 'Newark (EWR)']
# airport selection from dropdown menu
airport = st.sidebar.selectbox('Airport', airport_list)


st.sidebar.write('')
st.sidebar.write('')
# data card
with st.sidebar:
    menu = stom.option_menu(
        menu_title = 'Data Card',
        options = ['Description', 'Data Owner', 'Domain', 'Data Sources', 'Data Access'],
        icons = ['journal-text', 'person', 'diagram-3', 'boxes', 'code-slash'],
        default_index=0,
        menu_icon='card-heading',
        #orientation="horizontal",
        styles={
            "nav-link" : {"--hover-color": "#27a7d2"},
            "nav-link-selected": {"background-color": "#27a7d2"},
            "icon": {"color": "#27a7d2"}
        }
    )

    if menu == 'Description':
        smenu = stom.option_menu(
            menu_title='Description',
            options=['This data product provides a visual representation of NYC travel times, predicted delays, weather, and collisions for a given date and hour of the day.'],
            default_index=-1,
            menu_icon='journal-text',
            styles={
                "nav-link" : {"--hover-color": "#27a7d2"},
                "nav-link-selected": {"background-color": "#27a7d2"},
                "icon": {"color": "#27a7d2"}
            }
        )
    elif menu == 'Data Owner':
        smenu = stom.option_menu(
            menu_title='Data Owner',
            options=['Data Mesh Demos'],
            default_index=-1,
            menu_icon='person',
            styles={
                "nav-link" : {"--hover-color": "#27a7d2"},
                "nav-link-selected": {"background-color": "#27a7d2"},
                "icon": {"color": "#27a7d2"}
            }
        )
    elif menu == 'Domain':
        smenu = stom.option_menu(
            menu_title='Data Owner',
            options=['NYC Travel'],
            default_index=-1,
            menu_icon='diagram-3',
            styles={
                "nav-link" : {"--hover-color": "#27a7d2"},
                "nav-link-selected": {"background-color": "#27a7d2"},
                "icon": {"color": "#27a7d2"}
            }
        )
    elif menu == 'Data Sources':
        smenu = stom.option_menu(
            menu_title='Data Sources',
            options=['NYC Open Data Portal', 'NYC Taxi Trips', 'Visual Crossing Weather'],
            default_index=-1,
            menu_icon='boxes',
            styles={
                "nav-link" : {"--hover-color": "#27a7d2"},
                "nav-link-selected": {"background-color": "#27a7d2"},
                "icon": {"color": "#27a7d2"}
            }
        )
    elif menu == 'Data Access':
        smenu = stom.option_menu(
            menu_title='Data Access',
            options=['NYC Open Data Portal', 'NYC Taxi Trips', 'Visual Crossing Weather'],
            default_index=-1,
            menu_icon='code-slash',
            styles={
                "nav-link" : {"--hover-color": "#27a7d2"},
                "nav-link-selected": {"background-color": "#27a7d2"},
                "icon": {"color": "#27a7d2"}
            }
        )
    else:
        pass


@st.cache
def get_weather(date=None):
    'get weather for a given date or today if None'
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    qstring = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/new%%20york%%20city/%s/%s?unitGroup=metric&key=%s&contentType=json" % (date, date, VC_KEY)
    result = urllib.request.urlopen(qstring)
    fcast = json.loads(result.read().decode('utf-8'))
    day = fcast.get('days')[0]
    hours = day.get('hours')
    return day, hours

# weather metrics
day, hours = get_weather(date)
# conditions
conditions = day.get('conditions')
# hourly weather df
hrs = pd.DataFrame(hours)

m1, m2 = st.columns(2)

# travel delay indictor
m1.header('Travel Delay Indicator')

# overall delay-hour-condition model
dhc = pd.read_csv(join(CWD, '../data/airport_hour_conditions_delay.tsv'), sep='\t')

#st.write(dhc.head())

# gauge percentage of delayed trips
delay = dhc[(dhc.conditions==conditions) & (dhc.hour==slider_hour)].delay_indicator.values[0]


fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = delay,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'font': {'size': 8}},
    delta = {'reference': 100, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
    gauge = {
        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "blue"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 33], 'color': 'green'},
            {'range': [33, 66], 'color': 'orange'},
            {'range': [66, 100], 'color': 'red'}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 100}}))

if delay < 33:
    m1.write('**Relatively low chance of travel delay**')
elif delay < 50:
    m1.write('**Medium chance of travel delay**')
elif delay < 66:
    m1.write('**Medim to high chance of travel delay**')
elif delay < 88:
    m1.write('**High chance of travel delay**')
else:
    m1.write('**Very high chance of travel delay**')

# fig size
fig.update_layout(
    width=150,
    height=150,
    margin=dict(l=0, r=0, t=0, b=0),
    #paper_bgcolor='rgba(0,0,0,0)',
    #plot_bgcolor='rgba(0,0,0,0)',
    font=dict(
        family="Courier New, monospace",
        size=8,
        color="#7f7f7f"
        )
)
m1.write(fig)


# obtain weather for slider_hour_str
hour = hrs[hrs['datetime']==slider_hour_str]
temp = hour.temp.values[0]
precip = hour.precip.values[0]
humidity = hour.humidity.values[0]
wind = hour.windspeed.values[0]
desc = day.get('description')
icon = day.get('icon')
icon_url = icon_base % icon
m2.header('Weather Forecast')
m2.write('**%s**' % desc[:-1])
m2.image(icon_url, width=120)

# spacer
st.write(' ')

# previous hour metrics
phour = hrs[hrs['datetime']==prev_hour_str]
prev_temp = phour.temp.values[0]
prev_precip = phour.precip.values[0]
prev_humidity = phour.humidity.values[0]
prev_wind = phour.windspeed.values[0]

# calculate deltas
tempdelta = '%.1f °C' % (temp - prev_temp)
precipdelta = '%.1fmm' % (precip - prev_precip)
humiditydelta = '%.1f%%' % (humidity - prev_humidity)
winddelta = '%.1fkph' % (wind - prev_wind)

# create three columns
col1, col2, col3, col4 = st.columns(4)

col1.metric(label='Temperature', value='%.1f °C' % temp, delta=tempdelta)
precip_delta_color = 'off' if precipdelta == 0 else 'normal'
col2.metric(label='Rainfall', value='%.1f mm' % precip, delta=precipdelta, delta_color=precip_delta_color)
col3.metric(label='Humidity', value='%.1f%%' % humidity, delta=humiditydelta)
col4.metric(label='Wind Speed', value='%.1f kph' % wind, delta=winddelta)


# plot hourly temp, precip, and humidity
# set index to hour
hrs.set_index('datetime', inplace=True)

w1, w2 = st.columns(2)
# temp
w1.subheader('Temperature')
w1.line_chart(hrs['temp'], height=200, use_container_width=True)
# precip
w2.subheader('Rainfall')
w2.line_chart(hrs['precip'], height=200)

x1, x2 = st.columns(2)
# humidity
x1.subheader('Humidity')
x1.line_chart(hrs['humidity'], height=200)
# wind
x2.subheader('Wind Speed')
x2.line_chart(hrs['windspeed'], height=200)

# delay prediction
st.header("Travel Delay Prediction")
st.write('Likelihood of delay from %s to %s' % (puzone, airport))
# hourly probability of delay
hrs['delay'] = [1.88744589, 5.11280239, 10.2020454 ,  9.03790087,  7.64281398,
        15.88871278,  27.06624028,  48.81446728, 60.74875574, 70.19265685,
        65.78954048,  34.36287642,  22.684458  , 15.35649996, 41.7883561 ,
       58.66204771, 74.51793124, 85.46380269, 54.49042022, 31.69195251,
       12.63465126, 11.93111295, 13.74051771, 16.67041873]
# add positive random noise to delay
hrs['delay'] = hrs['delay'] + np.abs(np.random.normal(0, slider_hour, len(hrs)))
st.bar_chart(hrs['delay'], height=400)


# airport locations
la_guardia = [40.7900, -73.8700]
jfk = [40.6650, -73.7821]
newark = [40.7090, -74.1805]
zoom_level = 12

st.header('Collisions')
st.write('NYC police reported motor vehicle collisions between %s and %s' % (prev_hour_str, slider_hour_str))
# plot map points
# 
df = pd.read_csv(join(CWD, '../data/nyc_collisions_2022_jan_feb.csv'))
st.map(df[df.hour==slider_hour][['latitude', 'longitude']])

