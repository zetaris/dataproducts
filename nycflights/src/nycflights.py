import streamlit as st
#import pandas as pd
#import numpy as np
import datetime
#import altair as alt
#import plotly.graph_objects as go
import urllib
import json
from os.path import dirname, join


# wide page layout
st.set_page_config(page_title='NYC Travel', layout="wide", page_icon='favicon.ico')

# Weather API key
#VC_KEY = st.secrets['vc_api_key']

# cwd
CWD = dirname(__file__)

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



