import streamlit as st
import openai
from os.path import dirname, join


# wide page layout
st.set_page_config(page_title='Sequel', layout="wide", page_icon='favicon.ico')

# cwd
CWD = dirname(__file__)
# GPT3 key
openai.api_key = st.secrets['gpt_key']
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

# footer
st.markdown("""<style> footer {visibility: hidden;} </style>""", unsafe_allow_html=True) 


h1, h2, h3 = st.columns([3, 1, 2])
h1.title('Natural Language Database Interface')
#h1.write('Data Product powered by Zetaris Data Mesh')
h3.image(join(CWD, '../images/zetaris.horizontal.png'), width=248)

i1, i2, i3 = st.columns([1, 7, 2])
i1.image(join(CWD, '../images/poweredby.jpg'), use_column_width=True)

st.write(' ')
st.write(' ')

# sidebar logo
s1,s2,s3 = st.sidebar.columns([1,1,1])
s2.image(join(CWD, '../images/z.png'), width=84)

# sidebar description
st.sidebar.write(' ')
st.sidebar.write(' ')
st.sidebar.write(' ')
st.sidebar.write(' ')
#st.sidebar.subheader('SQL Demo')
#st.sidebar.subheader('Description')
st.sidebar.info('Describe a query in natural language and receive the corresponding SQL statement.')


# main form
form = st.form(key='my-form')
text = form.text_area('Enter plain text description of query:', height=60, placeholder='Example: Join customers and sales and region tables and select total sales by year for customers that reside in NYC')
submit = form.form_submit_button('Submit')

if submit and text:
    response = openai.Completion.create(
    engine="text-davinci-002",
    #engine='code-davinci-002',
    prompt=f'Generate an SQL query. {text}',
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    # write response as streamlit code
    sql = response.choices[0].text
    st.write(' ')
    st.code(sql, language='sql')









