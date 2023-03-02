import altair as alt
import pandas as pd
import streamlit as st

### READ IN DATA ###
@st.cache_data
def load_data():
    df1 = pd.read_csv('2021natality_clean1.csv')
    df2 = pd.read_csv('2021natality_clean2.csv')
    df3 = pd.read_csv('2021natality_clean3.csv')
    df4 = pd.read_csv('2021natality_clean4.csv')
    df5 = pd.read_csv('2021natality_clean5.csv')

    df_natality = pd.concat([df1, df2, df3, df4, df5])

    return df_natality

df_nat = load_data()
### READ IN DATA ###

### DATA CLEANING ###
# helper function #
def get_rate(df):
    rates = []
    for i in range(len(df)):
        if i % 2 != 0:
            denom = df.iloc[i-1,3] + df.iloc[i,3]
            rates.append(df.iloc[i-1,3] / denom)
            rates.append(df.iloc[i,3] / denom)
    return rates
# helper function #

df_natality_clean = df_nat[df_nat['no_mmorb'] == 0]

df_natality_clean1 = df_natality_clean[[
    #no mat morb, no infec, gest diabetes, hypertension
    'no_infec', 'rf_gdiab', 'rf_ghype', 
    #mat transfusion, perineal lac, ruptered uterus, unplan hyst, admit icu
    'mm_mtr', 'mm_plac', 'mm_rupt', 'mm_uhyst', 'mm_aicu']]

for i in ['mm_mtr', 'mm_plac', 'mm_rupt', 'mm_uhyst', 'mm_aicu']:
    df_natality_clean1[i] = df_natality_clean1[i] == 'Y'

df_natality_clean2 = pd.melt(
     df_natality_clean1, id_vars = ['no_infec', 'rf_gdiab', 'rf_ghype'], 
     var_name = 'outcome', value_name = 'yn')

df_natality_clean2['yn'] = df_natality_clean2['yn'].astype(int)

df_fml1 = df_natality_clean2.groupby(['no_infec', 'rf_gdiab', 'rf_ghype', 'outcome'], 
    group_keys = False).sum().apply(lambda x: x).reset_index()

#df_fml2 = df_natality_clean2.groupby(['no_infec', 'outcome', 'yn'], 
   # group_keys=False).count().apply(lambda x: x).reset_index()

#df_fml2['Rate'] = get_rate(df_fml2)
#df_fml3 = df_fml2[df_fml2['yn'] == 1]
### DATA CLEANING ###

### STREAMLIT THINGIES ###
st.write('## Task 3 Title')

### P2.1 ###
# replace with st.slider
#year = 2012
#year = st.slider('Year', min(df['Year']), max(df['Year']))
#subset = df[df["Year"] == year]
### P2.1 ###


### P2.2 ###
# replace with st.radio
#sex = "M"
#sex = st.radio('Sex', ('M', 'F'))
#subset = subset[subset["Sex"] == sex]
### P2.2 ###


### P2.3 ###
# replace with st.multiselect
#selected_risk = 'no_infec'
risk_factor = ['no_infec', 'rf_gdiab', 'rf_ghype']
# (hint: can use current hard-coded values below as as `default` for selector)
#countries = [
 #   "Austria",
  #  "Germany",
   # "Iceland",
    #"Spain",
    #"Sweden",
#    "Thailand",
   # "Turkey",
#]
selected_risk = st.selectbox('Risk Factor', risk_factor)

df_fml2 = df_natality_clean2.groupby([selected_risk, 'outcome', 'yn'], 
    group_keys=False).count().apply(lambda x: x).reset_index()

df_fml2['Rate'] = get_rate(df_fml2)
df_fml3 = df_fml2[df_fml2['yn'] == 1]
#subset = subset[subset["Country"].isin(selected_countries)]
### P2.3 ###


### P2.4 ###
# replace with st.selectbox
#cancer = "Malignant neoplasm of stomach"
#cancer = st.selectbox('Cancer Type', df['Cancer'].unique())
#subset = subset[subset["Cancer"] == cancer]
### P2.4 ###
### STREAMLIT THINGIES ###


### ALTAIR CHARTS ###
chart1 = alt.Chart(df_fml1).mark_bar().encode(
    x = alt.X('outcome', sort = 'y'),
    y = alt.Y('sum(yn)'),
    color = alt.Color('outcome'),
    column = 'no_infec',
    tooltip = 'sum(yn)'
).resolve_scale(
  y = 'independent'
)

chart2 = alt.Chart(df_fml3).mark_bar().encode(
    x = alt.X('outcome', sort = 'y'), 
    y = alt.Y('Rate'),
    column = selected_risk, #risk_factor = no_infec
    tooltip = 'Rate',
    color = 'outcome'
)

### ALTAIR CHARTS ###

### P2.5 ###

#chart = alt.Chart(subset).mark_rect().encode(
 #   x=alt.X("Age", sort=ages),
  #  y=alt.Y("Country"),
   # color=alt.Color("Rate", scale=alt.Scale(type='log', domain=(0.01, 1000), clamp=True)),
    #tooltip=["Rate"],
#).properties(
 #   title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
#)
### P2.5 ###

st.altair_chart(chart1, use_container_width=False)
st.altair_chart(chart2, use_container_width=False)

#countries_in_subset = subset["Country"].unique()
#if len(countries_in_subset) != len(countries):
 #   if len(countries_in_subset) == 0:
  #      st.write("No data avaiable for given subset.")
   # else:
    #    missing = set(countries) - set(countries_in_subset)
     #   st.write("No data available for " + ", ".join(missing) + ".")
