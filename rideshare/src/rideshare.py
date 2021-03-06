# -*- coding: utf-8 -*-
# Copyright 2018-2022 Zetaris Pty Ltd.


"""An example of mapping geographic data."""

import streamlit as st
import streamlit_option_menu as stom
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
from os.path import dirname, join


# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(
    page_title="NYC Ride Share",
    layout="wide",
    page_icon='favicon.ico',
    initial_sidebar_state="collapsed",
)


#st.sidebar.header('NYC Ride Share')
#st.sidebar.write('')

# stom menu
with st.sidebar:
    menu = stom.option_menu(
        menu_title='Data Card',
        options=['Description', 'Data Owner', 'Domain', 'Data Source', 'Data Access'],
        icons = ['journal-text', 'person', 'diagram-3', 'boxes', 'code-slash'],
        default_index=0,
        menu_icon='card-heading',
        styles={
            "nav-link" : {"--hover-color": "#27a7d2"},
            "nav-link-selected": {"background-color": "#27a7d2"},
            "icon": {"color": "#27a7d2"}
        }
    )

    if menu == 'Description':
        smenu = stom.option_menu(
            menu_title='Description',
            options=['This data product provides a visual representation of NYC trip pick-ups and drop-offs for a given hour of the day.'],
            default_index=-1,
            menu_icon='journal-text',
            styles={
                "nav-link" : {"--hover-color": "#27a7d2"},
                "nav-link-selected": {"background-color": "#27a7d2"},
                "icon": {"color": "#27a7d2"}
            }
        )


#st.sidebar.subheader('Data Card')
#st.sidebar.write('')
#st.sidebar.subheader('Description')
#st.sidebar.write('Ride share pickups over time in New York City and its major regional airports.')
#st.sidebar.write('')
#st.sidebar.subheader('Data Owner')
#st.sidebar.write('')
#st.sidebar.subheader('Domain')
#st.sidebar.write('')
#st.sidebar.subheader('Data Source')
#st.sidebar.write('')
#st.sidebar.subheader('Data Access')
#st.sidebar.write('')


h1, h2, h3 = st.columns(3)
h1.title('NYC Ride Share')
h1.write('Data Product powered by Zetaris Data Mesh')
h3.image('https://www.zetaris.com/hs-fs/hubfs/Zetaris-3D---FINAL-V2.png?width=300&name=Zetaris-3D---FINAL-V2.png')


# LOAD DATA ONCE
CWD = dirname(__file__)
@st.experimental_singleton
def load_data():
    data = pd.read_csv(
        join(CWD, "../data/uber-raw-data-sep14.csv.gz"), 
        nrows=100000,  # approx. 10% of data
        names=[
            "date/time",
            "lat",
            "lon",
        ],  # specify names directly since they don't change
        skiprows=1,  # don't read header since names specified directly
        usecols=[0, 1, 2],  # doesn't load last column, constant value "B02512"
        parse_dates=[
            "date/time"
        ],  # set as datetime instead of converting after the fact
    )

    return data


# FUNCTION FOR AIRPORT MAPS
def map(data, lat, lon, zoom):
    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 50,
            },
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=data,
                    get_position=["lon", "lat"],
                    radius=100,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
            ],
        )
    )


# FILTER DATA FOR A SPECIFIC HOUR, CACHE
@st.experimental_memo
def filterdata(df, hour_selected):
    return df[df["date/time"].dt.hour == hour_selected]


# CALCULATE MIDPOINT FOR GIVEN SET OF DATA
@st.experimental_memo
def mpoint(lat, lon):
    return (np.average(lat), np.average(lon))


# FILTER DATA BY HOUR
@st.experimental_memo
def histdata(df, hr):
    filtered = data[
        (df["date/time"].dt.hour >= hr) & (df["date/time"].dt.hour < (hr + 1))
    ]

    hist = np.histogram(filtered["date/time"].dt.minute, bins=60, range=(0, 60))[0]

    return pd.DataFrame({"minute": range(60), "pickups": hist})


# STREAMLIT APP LAYOUT
data = load_data()

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns((2, 3))

with row1_1:
    #st.title("NYC Uber Ridesharing Data")
    #st.title('')
    st.write(
    """
    ##
    Examine how rideshare pickups vary over time in New York City and its major regional airports.
    The time slider below allows you to select a specific hour of the day to explore.
    """
    )
    hour_selected = st.slider("Select hour of pickup", 0, 23)

with row1_2:
    pass


# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
row2_1, row2_2, row2_3, row2_4 = st.columns((2, 1, 1, 1))

# SETTING THE ZOOM LOCATIONS FOR THE AIRPORTS
la_guardia = [40.7900, -73.8700]
jfk = [40.6650, -73.7821]
newark = [40.7090, -74.1805]
zoom_level = 12
midpoint = mpoint(data["lat"], data["lon"])


with row2_1:
    st.write(
        """**All New York City between %02d:00 and %02d:00**""" % (hour_selected, hour_selected + 1)
    )
    map(filterdata(data, hour_selected), midpoint[0], midpoint[1], 11)

with row2_2:
    st.write("**LaGuardia Airport**")
    map(filterdata(data, hour_selected), la_guardia[0], la_guardia[1], zoom_level)

with row2_3:
    st.write("**JFK Airport**")
    map(filterdata(data, hour_selected), jfk[0], jfk[1], zoom_level)

with row2_4:
    st.write("**Newark Airport**")
    map(filterdata(data, hour_selected), newark[0], newark[1], zoom_level)

# CALCULATING DATA FOR THE HISTOGRAM
chart_data = histdata(data, hour_selected)

# LAYING OUT THE HISTOGRAM SECTION
st.write(
    f"""**Breakdown of rides per minute between {hour_selected}:00 and {(hour_selected + 1) % 24}:00**"""
)

st.altair_chart(
    alt.Chart(chart_data)
    .mark_area(
        interpolate="step-after",
    )
    .encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=["minute", "pickups"],
    )
    .configure_mark(opacity=0.2, color="red"),
    use_container_width=True,
)
