import pandas as pd
import streamlit as st
import scipy as sc
import numpy as np
import yfinance as yf

st.set_page_config(layout="wide")
st.title('DCF Model')
top_output_slot = st.empty()
col1, col2 = st.columns(2, gap="small")

stock = st.text_input(label="Company of Interest (ticker):", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible", icon=None, width="stretch", bind=None)
#stock = [input("Company of Interest (ticker):")]
df = pd.DataFrame(columns=["Stock", 'Beta', 'Marketcap'])

treasury_bill = yf.Ticker("^IRX")
current_rate = treasury_bill.info.get("regularMarketPrice")

with col1:
    base_revenue = st.slider("base revenue", min_value=0, max_value=500, step=5, value=200)
    revenue_growth_input = st.slider("revenue growth rate (in %)", min_value=0, max_value=50, step=1, value=10)
    terminal_growth_rate_input = st.slider("terminal growth rate (in %)", min_value=0, max_value=15, step=1, value=2)
    EBIT_margin_input = st.slider("EBIT-Margin (as {%} of rev)", min_value=0, max_value=100, step=1, value=20)
    time_input = st.slider("Time in Years", min_value=0, max_value=50, step=1, value=5)
with col2:
    tax_rate_input = st.slider("tax rate (in %)", min_value=0, max_value=50, step=1, value=23)
    d_a_input = st.slider("d&a (as {%} of rev)", min_value=0, max_value=50, step=1, value = 5)
    capex_input = st.slider("capex", min_value=0, max_value=50, step=1, value=7)
    nwc_input = st.slider("change in nwc", min_value=0, max_value=50, step=1, value=2)
    freespace = st.slider("This does nothing", min_value=0, max_value=10, step=1, value=0)

time = []
time.append(time_input)
        
for i in stock:
    ticker = yf.Ticker(i)
    info = ticker.info
    Beta = info.get('beta')
    debt_to_equity = info.get('debtToEquity')
    market_cap = info.get('marketCap')

d_e = debt_to_equity/100
debt = d_e *market_cap
equity = market_cap-debt
debt_weight = debt/market_cap
equity_weight = equity/market_cap

rf = 0.03
market_return = 0.10
capm = (current_rate/100) + Beta*(market_return - (current_rate/100))
capm_percentage = round(capm*100, 4)

for i in time:
    if i > 1:
        time.append(i-1)    

time.sort()
    
revenue_growth = revenue_growth_input/100
terminal_growth_rate = terminal_growth_rate_input/100
EBIT_margin = EBIT_margin_input/100
tax_rate = tax_rate_input/100
d_a = d_a_input/100
capex = capex_input/100
change_nwc = nwc_input/100

rf_rate = 0.04
risk_premium = 0.05
beta = 1.1
cost_debt = 0.05
debt_weight = 0.30

net_debt = 100
shares_outstanding = 10
current_share_price = 60

rev_year = base_revenue*(1+revenue_growth)
ebit = rev_year*EBIT_margin
NOPAT = ebit*(1-tax_rate)

FCF = NOPAT + d_a - capex - change_nwc  
#for loop in range of input time to calculate PV of estimated FCF at that time period

cost_of_equity = (current_rate/100) + beta*(risk_premium)
cost_of_debt = cost_debt*(1-tax_rate)
wacc = (1-debt_weight)*cost_of_equity + debt_weight*cost_of_debt

timer = [1,2,3,4,5]
PV_FCF = []
projected_CF = []
projected_rev = []

for i in time:
    if i == time[-1]:
        rev_year = base_revenue*((1+revenue_growth)**i)
        projected_rev.append(rev_year)
        ebit = rev_year*EBIT_margin
        NOPAT = ebit*(1-tax_rate)
        d_a_year = d_a*rev_year
        capex_year = capex*rev_year
        change_nwc_year = change_nwc*rev_year
        FCF = NOPAT + d_a_year - capex_year - change_nwc_year
        projected_CF.append(FCF)
        terminal_value = (FCF * (1+terminal_growth_rate))/(wacc - terminal_growth_rate)
        pv_terminal_value = terminal_value/((1+wacc)**i)
        PV_FCF.append(pv_terminal_value)
    else:
        rev_year = base_revenue*((1+revenue_growth)**i)
        projected_rev.append(rev_year)
        ebit = rev_year*EBIT_margin
        NOPAT = ebit*(1-tax_rate)
        d_a_year = d_a*rev_year
        capex_year = capex*rev_year
        change_nwc_year = change_nwc*rev_year
        FCF = NOPAT + d_a_year - capex_year - change_nwc_year
        projected_CF.append(FCF)
        pv_FCF = FCF/((1+wacc)**i)
        PV_FCF.append(pv_FCF)

    
EV = round(sum(PV_FCF), 4)
Equity_value = EV - net_debt
price_per_share = Equity_value / shares_outstanding

print(round(price_per_share, 4))

top_output_slot.metric(label="Intrinsic Share Price", value=round(price_per_share, 4))

with col1:
    st.bar_chart(data=projected_rev, x=None, y=None, x_label="years", y_label="projected revenue", color=None, horizontal=False, sort=True, stack=None, width="stretch", height="content", use_container_width=None)
with col2:
    st.bar_chart(data=projected_CF, x=None, y=None, x_label="years", y_label="projected Cashflows", color=None, horizontal=False, sort=True, stack=None, width="stretch", height="content", use_container_width=None)

st.header("The Calculated CAPM is:")
st.text(capm_percentage)
