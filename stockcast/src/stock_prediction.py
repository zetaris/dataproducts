# pip install streamlit fbprophet yfinance plotly
import streamlit as st
from datetime import date
from os.path import dirname, join
import yfinance as yf
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd


# can only be called once per app, and must be called as the first Streamlit command
st.set_page_config(
    page_title="Stock Price Forecast",
    layout="wide",
    page_icon='z_favicon.jpeg',
    initial_sidebar_state="collapsed",
)

h1, h2, h3 = st.columns(3)
h1.title('Stock Price Forecast')
h1.write('Data Product powered by Zetaris Data Mesh')
h3.image('https://www.zetaris.com/hs-fs/hubfs/Zetaris-3D---FINAL-V2.png?width=300&name=Zetaris-3D---FINAL-V2.png')


START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")
CWD = dirname(__file__) # /app/stockcast/src
st.subheader('')

# increase sidebar width
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 500px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 500px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# initiate empty sidebar on load
st.sidebar.header('')

# get list of stocks from data/djia_stocks.csv
stocks_df = pd.read_csv(join(CWD, '../data/djia.tsv'), sep='\t')
stocks = list(stocks_df['symbol'].unique())
stocks.extend(('GOOG', 'TSLA'))
stocks.insert(0, '')
stocks.sort()
selected_stock = st.selectbox('Select stock for prediction', stocks)

n_years = st.slider('Years of prediction:', 1, 4)
period = n_years * 365

# write stock info to sidebar
if selected_stock:
    load_info = st.info('Loading data...')
    # get company info from yfinance
    stock = yf.Ticker(selected_stock)
    info = stock.info
    # display company name
    cname = info['longName'] 
    st.sidebar.header(cname)
    # get and display logo
    logo_url = info['logo_url']
    # for each key in info, display key as a header and value as a text
    for key, value in info.items():
        st.sidebar.subheader(key)
        st.sidebar.write(value)



@st.cache
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data

if selected_stock:
    #data_load_state = st.text('Loading data...')
    data = load_data(selected_stock)
    # delete load_info
    load_info.empty()

#if selected_stock and st.checkbox('Show stock info'):
#    st.subheader('Stock Info')
#    stock = yf.Ticker(selected_stock)
#    st.write(stock.info)


# Plot raw data
def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
    fig.update_layout(yaxis_title=selected_stock)
    fig.layout.update(xaxis_rangeslider_visible=True)
    fig.layout.update(legend_orientation="h")
    st.plotly_chart(fig, use_container_width=True)

if selected_stock:
    
    col1, col2, col3 = st.columns((4, 2, 1))
    col3.image(logo_url, width=50)
    col1.header(cname)
    currentPrice = info.get('currentPrice')
    prevClose = info.get('previousClose')
    col2.metric(label="Last Price", value=currentPrice, delta='%.2f' % (currentPrice - prevClose))
    st.subheader('Historical Stock Price')
    plot_raw_data()

if selected_stock and st.checkbox('Show historical stock data'):
    st.subheader('Raw historical data')
    st.write(data.tail())

if selected_stock:
    # Predict forecast with Prophet.
    forecast_load_info = st.info('Forecast prediction...')
    df_train = data[['Date','Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)

    # add horizontal spacing
    st.write(' ')
    st.write(' ')
    st.write(' ')

    forecast_load_info.empty()
    st.subheader('Stock Price Forecast')

    fig1 = plot_plotly(m, forecast)
    # set y-axis label
    fig1.update_layout(yaxis_title=selected_stock)
    # set x-axis label to blank
    fig1.update_layout(xaxis_title='')
    st.plotly_chart(fig1, use_container_width=True)

# Show and plot forecast
if selected_stock and st.checkbox('Show stock forecast data'):
    st.subheader('Forecast data')
    st.write(forecast.tail())

if selected_stock:
    # add horizontal spacing
    st.write(' ')
    st.write(' ')
    st.write(' ')

    # forecaset components
    st.subheader('Forecast Components')
    fig2 = m.plot_components(forecast)
    st.write(fig2)
