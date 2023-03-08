import altair as alt
import pandas as pd
import numpy as np
import streamlit as st
from vega_datasets import data

st.set_page_config(layout = 'wide', page_title = 'CDC Natality 2021', page_icon = ':baby:')

### READ IN DATA ###
@st.cache_data
def load_data():
    bw_risk_alice = pd.read_csv('data/bw_risk_alice.csv')
    mm_county_fiona = pd.read_csv('data/mm_county_fiona.csv')
    morb_group_isabel = pd.read_csv('data/morb_group_isabel.csv')
    morb_group2_isabel = pd.read_csv('data/morb_group2_isabel.csv')
    rate_risk_alice = pd.read_csv('data/rate_risk_alice.csv')
    sum_risk_alice = pd.read_csv('data/sum_risk_alice.csv')

    return bw_risk_alice, mm_county_fiona, morb_group_isabel, morb_group2_isabel, rate_risk_alice, sum_risk_alice

bw_risk_alice, mm_county_fiona, morb_group_isabel, morb_group2_isabel, rate_risk_alice, sum_risk_alice = load_data()
### READ IN DATA ###


### PLOT FIONA ###
### BACKGROUND PLOT ###
# import state data
states = alt.topo_feature(data.us_10m.url, 'states')

# set common features
width = 575 #900
height  = 450
project = 'albersUsa'

# create the background plot
background = alt.Chart(states
).mark_geoshape(
    fill='lightgrey',
    stroke='white'
).properties(
    width=width,
    height=height
).project(
    project)

### BASE PLOT ###
# import county data
counties = alt.topo_feature(data.us_10m.url, 'counties')

# create a selector to link graphs
selector = alt.selection_single(fields = ['County of Residence'])

# create the base plot
chart_base = alt.Chart(counties
).properties( 
    width=width,
    height=height
).project(
    project
).add_selection(
    selector
).transform_lookup(
    lookup="id",
    from_=alt.LookupData(mm_county_fiona, "county-id", ['Avg_Age_MM', 'percent_MM', 'County of Residence']))

### AGE PLOT ###
# create the color scale for age
age_scale = alt.Scale(domain=[mm_county_fiona["Avg_Age_MM"].min(), mm_county_fiona["Avg_Age_MM"].max()], scheme='blueorange')

# create the age plot 
chart_age = chart_base.mark_geoshape(stroke='black').encode(
    color = alt.Color("Avg_Age_MM:Q", scale = age_scale, title = "Age(y)"),
     tooltip=[alt.Tooltip('County of Residence:N', title = "County"), alt.Tooltip('Avg_Age_MM:Q', title = "Age of Mothers with Mordibity")]
).transform_filter(
    selector)

### PERCENT PLOT ###
# create the color scale for percentages
percent_scale = alt.Scale(domain=[mm_county_fiona["percent_MM"].min(), mm_county_fiona["percent_MM"].max()], scheme='oranges')

# create the percentage plot
chart_percent = chart_base.mark_geoshape(stroke='black').encode(
    color = alt.Color('percent_MM:Q', scale = percent_scale, title = "Percent Morbidity"),
    tooltip=[alt.Tooltip('County of Residence:N', title = "County"), alt.Tooltip('percent_MM:Q', title = "Percent Morbidity")]
).transform_filter(
    selector)

### COMBINED PLOT ###
# combine plots 
mm_chart = alt.hconcat(background + chart_age, background + chart_percent
).resolve_scale(
    color='independent')
### PLOT FIONA ###


### PLOTTING ISABEL ###
# create selector for outcome, add to dropdown
outcome = morb_group2_isabel['no_mmorb'].unique()
outcome_dropdown = alt.binding_select(options=outcome)
outcome_select = alt.selection_single(fields=['no_mmorb'], bind=outcome_dropdown, 
                                     name= "Maternal Morbidity Outcome", init = {'no_mmorb': outcome[0]})

# set up a sorted bar plot showing cancer deaths in 2019
plot = alt.Chart(morb_group_isabel).mark_bar().encode(
    x = alt.X('dob_mm', title = 'Month',  sort= ["January", "February", "March", "April" , 
                                                   "May", "June", "July",  "August", 'September', 
                                                   'October', 'November', 'December']),
    y = alt.Y('dob_tt:Q', title = 'Birth Count'),
    color = alt.Color('no_mmorb:N', title = 'Maternal Morbidity', scale=alt.Scale(
        range=[' #0F52BA', '#87CEEB']), legend = alt.Legend(
        orient = 'top',
        direction = 'horizontal',
        labelFontSize = 15,
        titleFontSize = 17)),
    tooltip = [alt.Tooltip('dob_tt:Q', title ='Count')]
).properties(
    width = 400,
    height = 500).configure_axis(
    titleFontSize = 20,
    labelFontSize = 15)

# angle the x-axis labels and include full label
plot2 = plot.configure_axisBottom(
    labelAngle = 270,
    labelLimit = 0)


# create a selector for month, add to legend
month_selection = alt.selection_single(fields=['dob_mm'], bind='legend')

# create selector for outcome, add to dropdown
outcome = morb_group2_isabel['no_mmorb'].unique()
outcome_dropdown = alt.binding_select(options=outcome)
outcome_select = alt.selection_single(fields=['no_mmorb'], bind=outcome_dropdown, 
                                     name= "Maternal Morbidity Outcome", init = {'no_mmorb': outcome[0]})

line = alt.Chart(morb_group2_isabel).mark_line(point=True).encode(
  x = alt.X('bins', title = 'Time', sort = ['0:00-1:00', '1:01-2:00', '2:01-3:00', '3:01-4:00', '4:01-5:00',
                         '5:01-6:00', '6:01-7:00', '7:01-8:00', '8:01-9:00', '9:01-10:00', '10:01-11:00',
                         '11:01-12:00', '12:01-13:00', '13:01-14:00', '14:01-15:00', '15:01-16:00',
                         '16:01-17:00', '17:01-18:00', '18:01-19:00', '19:01-20:00', '20:01-21:00',
                         '21:01-22:00', '22:01-23:00', '23:01-24:00']),
  y = alt.Y('dob_tt:Q', title = 'Births'),
  color = alt.Color('dob_mm', title = 'Month', legend = alt.Legend(titleFontSize = 17),
                    sort = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                           'September', 'October', 'November', 'December']),
  opacity=alt.condition(month_selection, alt.value(1), alt.value(0.1)), # add opacity
  tooltip = [alt.Tooltip('dob_tt:Q', title ='Count')]
).properties(
    width = 800,
    height = 500
).add_selection(
    outcome_select
).transform_filter(
    outcome_select
).add_selection(
month_selection).configure_axis(
    titleFontSize = 20,
    labelFontSize = 15)

# angle the x-axis labels and include full label
line2 = line.configure_axisBottom(
    labelAngle = 65,
    labelLimit = 0)
### PLOTTING ISABEL ###


### DATA ALICE###
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

# selector thingies #
age_group = bw_risk_alice['mage_cat'].unique()
pat_ack = bw_risk_alice['mar_p'].unique()
mar_status = bw_risk_alice['dmar'].unique()
mom_educ = bw_risk_alice['meduc'].unique()
dad_educ = bw_risk_alice['feduc'].unique()
cigs = bw_risk_alice['cig_cat'].unique()
# selector thingies #
### DATA ALICE ###


### STREAMLIT THINGIES ###
## header ##
st.write('# 2021 CDC Natality - Maternal Morbidity and Birth Risks')
st.write('Authors: Fiona McBride, Isabel Smokelin, Alice Saparov')
st.write('These visualizations use the 2021 Natality Public Use dataset from the Centers \
         for Disease Control and Prevention. This dataset contains information related to \
         all documented births in the United States of America for the year 2021.')
## header ##

## maps ##
st.write('## Maternal Morbidity Trends in the United States')
st.write('Investigating maternal morbidity trends across different counties. \
         Select a county to highlight it on both maps. Mouseover to see county specific information.')
row4_1, row4_2 = st.columns(2)
with row4_1:
    st.write('### Average Age of Mothers with Maternal Morbidities')
with row4_2: 
    st.write('### Percent of Births Resulting in Maternal Mordibity')
st.altair_chart(mm_chart)
## maps ##

## temporal ##
st.write('## Overview of Births and Maternal Morbidity in 2021')
st.write('A broad overview of maternal morbidity counts in 2021 and births per hour for each month. \
         Mouseover bars on the left to see specific month counts. \
         Select months from the legend to highlight them in the right plot, \
         and can also filter the maternal morbidity outcome.')
row3_1, row3_2 = st.columns([1,2])
with row3_1:
    st.write('### USA Maternal Morbidity in 2021')
with row3_2: 
    st.write('### Births per hour in 2021')
## temporal ##

## risk factors ##
st.write('## Maternal Morbidity Risk Factors')
st.write('Investigate how risk factors affect maternal morbidity. \
         Mouseover on the left plot bars enables specifc counts per risk to be seen. \
         Select specifc risks on the right to see maternal outcome rates (mouseover enabled for rate).\
         Legend selection is also available to highlight a chosen outcome.')
row1_1, row1_2 = st.columns([1,1.8])
with row1_1:
    st.write('### Count of Maternal Morbidity')
with row1_2: 
    st.write('### Outcome Rates for Selected Risk Factor')
    selected_risk = st.radio('Select Risk', 
                             ('No Infection','Gestational Diabetes','Gestational Hypertension'), 
                             index = 1,
                             horizontal = True)
## risk factors ##

## birthweight ##
st.write('## Risk Factor Effects on Birthweight')
st.write('Investigate specific risk factors on birthweight (g) by selecting any \
         number of risk factors on the left. Black bars in the plot correspond \
         to the range of a normal birthweight. The red line indicates the average of \
         the points shown. Mouseover is available to view details regarding specific points. \
         Scroll within the plot to zoom in and out over the range of birthweights.')
row2_1, row2_2 = st.columns([1,2.5])
with row2_1:
    st.write('### Select Risk Factors')
    #selectors
    age_risk = st.multiselect('Mother Age Group', age_group, ['20-25'])
    pat_risk = st.multiselect('Paternity Acknowledged', pat_ack, ['Y', 'N'])
    mar_risk = st.multiselect('Martial Status', mar_status, ['Married', 'Unmarried'])
    meduc_risk = st.multiselect('Mother Education', mom_educ, ['Associate', "Bachelor's"])
    feduc_risk = st.multiselect('Father Education', dad_educ, ['Some college', 'Associate'])
    cig_risk = st.multiselect('Number of Cigarettes (daily before pregnancy)', cigs, ['none'])
with row2_2: 
    st.write('### Mean Birthweight for Selected Risk Factors')
## birthweight ##
### STREAMLIT THINGIES ###

### PLOTTING ALICE ###
## PLOT - RISK SUM ##
chart0 = alt.Chart(sum_risk_alice).mark_bar().encode(
    x = alt.X('Risk Factor', sort = 'y'), 
    y = alt.Y('Count'),
    color = alt.condition(
        alt.datum['Risk Factor'] == selected_risk,  # If the year is 1810 this test returns True,
        alt.value('#71797E'),     # which sets the bar orange.
        alt.value('#D3D3D3')   # And if it's not true it sets the bar steelblue.
    ),
    tooltip = 'Count').properties(
    width = 360,
    height = 650).configure_axisBottom(
    labelAngle = 305,
    labelLimit = 0, 
    labelFontSize = 12).configure_axis(
    titleFontSize = 17).configure_axisY(
    labelFontSize = 15)
## PLOT - RISK SUM ##

## SUBSET - MMORB RISK ##
rate_risk_alice = rate_risk_alice[rate_risk_alice['No Infection'] != 9]
rate_risk_alice['No Infection'] = rate_risk_alice['No Infection'].map({0: 'Infection', 1: 'No Infection'})
rate_risk_alice['Gestational Diabetes'] = rate_risk_alice['Gestational Diabetes'].map({False: 'No Gest. Diabetes', True: 'Gest. Diabetes'})
rate_risk_alice['Gestational Hypertension'] = rate_risk_alice['Gestational Hypertension'].map({False: 'No Gest. Hypertension', True: 'Gest. Hypertension'})
df_fml2 = rate_risk_alice.groupby([selected_risk, 'Outcome', 'yn'], 
    group_keys=False).count().apply(lambda x: x).reset_index()
df_fml2['Rate'] = get_rate(df_fml2)
df_fml3 = df_fml2[df_fml2['yn'] == 1]
## SUBSET - MMORB RISK  ##

## SUBSET - RISK AVERAGING ##
df_subset3 = bw_risk_alice[(bw_risk_alice['mage_cat'].isin(age_risk)) &
                (bw_risk_alice['mar_p'].isin(pat_risk)) &
                (bw_risk_alice['dmar'].isin(mar_risk)) &
                (bw_risk_alice['meduc'].isin(meduc_risk)) &
                (bw_risk_alice['feduc'].isin(feduc_risk)) &
                (bw_risk_alice['cig_cat'].isin(cig_risk))].reset_index()
## SUBSET - RISK AVERAGING ##

## PLOT - RISK AVERAGING ##
points = alt.Chart().mark_point().encode(
    x = alt.X('index:O', axis = None),
    y = alt.Y('dbwt:Q', scale = alt.Scale(domain = [2000, 4500], clamp = True), title = 'Birthweight (g)'),
    tooltip = [alt.Tooltip('mage_cat', title = 'Mother Age'),
               alt.Tooltip('mar_p', title = 'Paternity Acknowledged'), 
               alt.Tooltip('dmar', title = 'Martial Status'), 
               alt.Tooltip('meduc', title = 'Mother Eduation'), 
               alt.Tooltip('feduc', title = 'Father Education'), 
               alt.Tooltip('cig_cat', title = 'Number of Cigarettes'), 
               alt.Tooltip('dbwt:Q', title = 'Birthweight (g)')]
).properties(
    width = 800,
    height = 600)
line_min = alt.Chart(pd.DataFrame({'Lower birthweight': [2500]})).mark_rule(color = 'black').encode(
    y = 'Lower birthweight', size = alt.SizeValue(3))
line_max = alt.Chart(pd.DataFrame({'Upper birthweight': [4000]})).mark_rule(color = 'black').encode(
    y = 'Upper birthweight', size = alt.SizeValue(3))
line_risk = alt.Chart().mark_rule(color = 'firebrick').encode(
    y = 'mean(dbwt):Q',
    size = alt.SizeValue(3),
    tooltip = [alt.Tooltip('mean(dbwt):Q', title = 'Mean Birthweight')])
chart3 = alt.layer(points, line_min, line_max, line_risk, data = df_subset3).configure_axis(
    titleFontSize = 20,
    labelFontSize = 15).interactive()

overview_hist = alt.Chart().mark_bar().encode(
    alt.X('dbwt:Q', bin = True),
    y = 'count()',
)
line_avgbw = alt.Chart(pd.DataFrame({'Mean birthweight': [2500]})).mark_rule(color = 'black').encode(
    y = 'Lower birthweight', size = alt.SizeValue(3))
## PLOT - RISK AVERAGING ##

## PLOT - MMORB RISK  ##
outcome_selection = alt.selection_single(fields = ['Outcome'], bind = 'legend')

chart2 = alt.Chart(df_fml3).mark_bar().encode(
    x = alt.X('Outcome', sort = 'y', axis = alt.Axis(title = 'Outcome')), 
    y = alt.Y('Rate'),
    column = selected_risk, 
    tooltip = 'Rate',
    color = alt.Color('Outcome', legend = alt.Legend(
        orient = 'top',
        direction = 'horizontal',
        columns = 3,
        labelFontSize = 15,
        titleFontSize = 20), scale = alt.Scale(scheme = 'category10')), 
    opacity = alt.condition(outcome_selection, alt.value(1), alt.value(0.1))).properties(
    width = 350,
    height = 350).configure_axisBottom(
    labelAngle = 305,
    labelLimit = 100,
    labelFontSize = 0).configure_header(
    titleFontSize = 20,
    labelFontSize = 15).configure_axis(
    titleFontSize = 17).configure_axisY(
    labelFontSize = 15).add_selection(
    outcome_selection)
## PLOT - MMORB RISK  ##
### PLOTTING ALICE ###


### STREAMLIT THINGIES ###
with row1_1:
    st.altair_chart(chart0)

with row1_2: 
    st.altair_chart(chart2)

with row2_2:
    st.altair_chart(chart3)

with row3_1:
    st.altair_chart(plot2)

with row3_2:
    st.altair_chart(line2)
### STREAMLIT THINGIES ###

