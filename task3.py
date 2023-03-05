import altair as alt
import pandas as pd
import numpy as np
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

### TASK 3 ###
df_bw_risk = df_nat[['mager', 'mar_p', 'dmar',
                     'meduc', 'feduc', 'cig_0', 'dbwt']]

df_bw_risk_clean = df_bw_risk[df_bw_risk['mar_p'] != 'U']

df_bw_risk_clean['mage_cat'] = np.where(df_bw_risk_clean['mager'] < 17, '<20',
                               np.where(df_bw_risk_clean['mager'] < 26, '20-25',
                               np.where(df_bw_risk_clean['mager'] < 31, '26-30',
                               np.where(df_bw_risk_clean['mager'] < 36, '31-35',
                               np.where(df_bw_risk_clean['mager'] < 41, '36-40',
                               np.where(df_bw_risk_clean['mager'] < 46, '41-45', '46-50'))))))

#cig daily before preg
df_bw_risk_clean['cig_cat'] =  np.where(df_bw_risk_clean['cig_0'] == 0, 'none',
                               np.where(df_bw_risk_clean['cig_0'] < 5, '<5',
                               np.where(df_bw_risk_clean['cig_0'] < 11, '5-10',
                               np.where(df_bw_risk_clean['cig_0'] < 21, '11-20',
                               np.where(df_bw_risk_clean['cig_0'] < 41, '21-40', '41+')))))

df_bw_risk_clean1 = df_bw_risk_clean.drop(columns = ['mager', 'cig_0'])

df_bw1 = df_bw_risk_clean1.groupby(['mage_cat', 'mar_p', 'dmar', 'meduc', 'feduc', 'cig_cat'], 
                                     group_keys=False).mean().apply(lambda x: x).reset_index()


### TASK 3 ###

### TASK 3 STREAMLIT ###
age_group = df_bw1['mage_cat'].unique()
#age_risk = st.selectbox('Mother Age Group', age_group)
age_risk = st.multiselect('Mother Age Group', age_group)

pat_ack = df_bw1['mar_p'].unique()
#pat_risk = st.selectbox('Paternity Acknowledged', pat_ack)
pat_risk = st.multiselect('Paternity Acknowledged', pat_ack)

mar_status = df_bw1['dmar'].unique()
#mar_risk = st.selectbox('Martial Status', mar_status)
mar_risk = st.multiselect('Martial Status', mar_status)

mom_educ = df_bw1['meduc'].unique()
#['< 8th grade', '9-12th grade', 'High school graduate/GED',
#'Some college', 'Associate', "Bachelor's", "Master's", 'Doctorate/Profession', 'Unknown']
#meduc_risk = st.selectbox('Mother Education', mom_educ)
meduc_risk = st.multiselect('Mother Education', mom_educ)

dad_educ = df_bw1['feduc'].unique()
#feduc_risk = st.selectbox('Father Education', dad_educ)
feduc_risk = st.multiselect('Father Education', dad_educ)

cigs = df_bw1['cig_cat'].unique()
#cig_risk = st.selectbox('Number of Cigarettes (daily before pregnancy)', cigs)
cig_risk = st.multiselect('Number of Cigarettes (daily before pregnancy)', cigs)

#df_subset = df_bw1[(df_bw1['mage_cat'] == age_risk) & 
 #               (df_bw1['mar_p'] == pat_risk) &
  #             (df_bw1['meduc'] == meduc_risk) &
       #         (df_bw1['feduc'] == feduc_risk) &
         #       (df_bw1['cig_cat'] == cig_risk)]
df_subset = df_bw1[(df_bw1['mage_cat'].isin(age_risk)) &
                (df_bw1['mar_p'].isin(pat_risk)) &
                (df_bw1['dmar'].isin(mar_risk)) &
                (df_bw1['meduc'].isin(meduc_risk)) &
                (df_bw1['feduc'].isin(feduc_risk)) &
                (df_bw1['cig_cat'].isin(cig_risk))].reset_index()

#selected_countries = st.multiselect('Country', countries)
#subset = subset[subset["Country"].isin(selected_countries)]

### TASK 3 STREAMLIT ###

### PLOT TASK 3 ###
points = alt.Chart().mark_point().encode(
    x = alt.X('index:O'),
    y = alt.Y('dbwt:Q', scale = alt.Scale(domain = [300, 6700])),
    tooltip = 'dbwt:Q'
)

line_min = alt.Chart(pd.DataFrame({'y': [2500]})).mark_rule(color = 'black').encode(
    y = 'y', size = alt.SizeValue(3))
line_max = alt.Chart(pd.DataFrame({'y': [4000]})).mark_rule(color = 'black').encode(
    y = 'y', size = alt.SizeValue(3)
)

line_risk = alt.Chart().mark_rule(color = 'firebrick').encode(
    y = 'mean(dbwt):Q',
    size = alt.SizeValue(3),
    tooltip = 'mean(dbwt):Q'
)

chart3 = alt.layer(points, line_min, line_max, line_risk, data = df_subset)
### PLOT TASK 3 ###

### TASK 4 ###
df_natality_clean = df_nat[df_nat['no_mmorb'] == 0]

df_natality_clean1 = df_natality_clean[[
    #no mat morb, no infec, gest diabetes, hypertension
    'no_infec', 'rf_gdiab', 'rf_ghype', 
    #mat transfusion, perineal lac, ruptered uterus, unplan hyst, admit icu
    'mm_mtr', 'mm_plac', 'mm_rupt', 'mm_uhyst', 'mm_aicu']]

for i in ['mm_mtr', 'mm_plac', 'mm_rupt', 'mm_uhyst', 'mm_aicu', 'rf_gdiab', 'rf_ghype']:
    df_natality_clean1[i] = df_natality_clean1[i] == 'Y'

df_natality_clean2 = pd.melt(
     df_natality_clean1, id_vars = ['no_infec', 'rf_gdiab', 'rf_ghype'], 
     var_name = 'outcome', value_name = 'yn')

df_natality_clean2['yn'] = df_natality_clean2['yn'].astype(int)

df_fml1 = df_natality_clean2.groupby(['no_infec', 'rf_gdiab', 'rf_ghype', 'outcome'], 
    group_keys = False).sum().apply(lambda x: x).reset_index()

df_fml4 = pd.melt(
     df_natality_clean1, id_vars = ['mm_mtr', 'mm_plac', 'mm_rupt', 'mm_uhyst', 'mm_aicu'], 
     var_name = 'risk_factor', value_name = 'yn'
)
df_fml4['yn'] = df_fml4['yn'].astype(int)
df_fml5 = df_fml4.groupby('risk_factor').sum().reset_index()
### TASK 4 ###


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

### ALTAIR CHARTS ###
chart0 = alt.Chart(df_fml5).mark_bar().encode(
    x = alt.X('risk_factor', sort = 'y'), 
    y = alt.Y('yn'),
    tooltip = 'yn',
    color = 'risk_factor'
)

### ALTAIR CHARTS ###


### RISK SELECTOR ###
#risk_factor = ['no_infec', 'rf_gdiab', 'rf_ghype']
#selected_risk = st.selectbox('Risk Factor', risk_factor)
selected_risk = 'no_infec'
selected_risk = st.radio('Select Risk', ('no_infec', 'rf_gdiab', 'rf_ghype'))

df_fml2 = df_natality_clean2.groupby([selected_risk, 'outcome', 'yn'], 
    group_keys=False).count().apply(lambda x: x).reset_index()

df_fml2['Rate'] = get_rate(df_fml2)
df_fml3 = df_fml2[df_fml2['yn'] == 1]
### RISK SELECTOR ###


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

col1, col2, col3, col4 = st.columns((2,1,1,1))
with col1:
    st.altair_chart(chart0, use_container_width=False)
#st.altair_chart(chart1, use_container_width=False)
with col2: 
    st.altair_chart(chart2, use_container_width=False)
with col4:
    st.altair_chart(chart3, use_container_width=False)

#countries_in_subset = subset["Country"].unique()
#if len(countries_in_subset) != len(countries):
 #   if len(countries_in_subset) == 0:
  #      st.write("No data avaiable for given subset.")
   # else:
    #    missing = set(countries) - set(countries_in_subset)
     #   st.write("No data available for " + ", ".join(missing) + ".")
