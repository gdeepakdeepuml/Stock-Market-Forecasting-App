import streamlit as st 
import pandas as pd 
import yfinance as yf 
from plotly import graph_objs as go 
from datetime import date 
from fbprophet import Prophet 
from fbprophet.plot import plot_plotly 
import cufflinks as cf 
import base64 

# title  
heading = """
    <h1 style="text-align: center;"> Stock Market Forecasting App<h1>
    <h5 style="text-align: center;"> if a human investor can be successful, for what reason can't a meachine?<h5>
    """
st.markdown(heading,unsafe_allow_html=True)

Start = "2015-01-01"
today = date.today().strftime("%Y-%m-%d")

#stocks = ('GOOG', 'AAPL', 'MSFT', 'GME') 
ticker_list = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/s-and-p-500-companies/master/data/constituents_symbols.txt')
selected_com = st.selectbox("select the company that you are intersted in.",ticker_list) 
#st.write(len(ticker_list)) 

tickerData = yf.Ticker(selected_com) 
data_stock = tickerData.history(period="1d",start=Start,end=today)

# Ticker information
string_logo = '<img src=%s>' % tickerData.info['logo_url']
st.write("""  
    # The Selected Company Information and Summary  
    ***   
""") 
a,b,c = st.beta_columns(3)
b.markdown(string_logo, unsafe_allow_html=True,)  
d,e,f = st.beta_columns(3)
string_name = tickerData.info['longName']
e.header('**%s**' % string_name)
info_com = tickerData.info['longBusinessSummary'] 
st.write(info_com)

@st.cache
def load_data_from(sotck):
    data = yf.download(sotck,Start,today)
    data.reset_index(inplace=True)
    return data 


#temp = st.text("loading the data..")
data = load_data_from(selected_com) 
#temp.text("loading data ... Done") 

st.subheader("here is the raw data of {}".format(string_name)) 
st.write(data.tail())  

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(data), unsafe_allow_html=True) 

#f1,f2 = st.beta_columns(2)
def plot_ram_data():
    fig = go.Figure() 
    fig.add_trace(go.Scatter(x=data['Date'],y=data['Open'],name="stock_open"))
    fig.add_trace(go.Scatter(x=data['Date'],y=data['Close'],name="stock_open"))
    fig.layout.update(title_text="Time Series data with Rangeslider for open and close", xaxis_rangeslider_visible=True) 
    st.plotly_chart(fig) 

def plot_ram_data2():
    fig = go.Figure() 
    fig.add_trace(go.Scatter(x=data['Date'],y=data['Volume'],name="stock_open"))
    fig.layout.update(title_text="Time Series data with Rangeslider for the volume of stock", xaxis_rangeslider_visible=True) 
    st.plotly_chart(fig)   

def plot_high_data():
    fig4 = go.Figure() 
    fig4.add_trace(go.Scatter(x=data['Date'],y=data["High"],name="stock_high"))
    fig4.add_trace(go.Scatter(x=data['Date'],y=data["Low"],name="stock_low")) 
    fig4.layout.update(title_text = "Time Series data with Rangeslider for high and low", xaxis_rangeslider_visible=True)
    st.plotly_chart(fig4)

plot_ram_data()
#plot_high_data()
plot_ram_data2() 

# Bollinger bands 
st.write("**Bollinger Band**") 
plot = cf.QuantFig(data_stock,title='First Quant Figure',legend="top",name="GS")  
plot.add_bollinger_bands() 
fig = plot.iplot(asFigure=True) 
st.plotly_chart(fig)


# Predict forecast with Prophet.
st.write(""" 
    # Time Series Forecast of Stocks  

    A time series is a sequence of observations taken sequentially in time.
    
    Time Series Forecasting is Making predictions about the future is called extrapolation in the classical statistical handling of time series data.

    Forecasting involves taking models fit on historical data and using them to predict future observations for some period of time.
""")
n_years = st.slider("choose Years of the Predictions:",1,5)
time = n_years * 365

df_train = data[['Date','Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train) 

futures_dates = m.make_future_dataframe(periods=time) 

forcaste = m.predict(futures_dates) 

# show the plots of forcaste 
st.subheader("Forcast Data ... ")
st.write(forcaste.tail()) 

st.write(f'Forecast plot for {n_years} years')
fig2 = plot_plotly(m,forcaste) 
st.plotly_chart(fig2) 

st.write("Forcaste Components- Trend,Weekly,Yearly") 
fig3 = m.plot_components(forcaste)
st.write(fig3) 
