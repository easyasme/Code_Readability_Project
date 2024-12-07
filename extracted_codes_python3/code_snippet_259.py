#from re import T
import streamlit as st
import datetime, time
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
import joblib

def predict(armour_slope,water_level,bed_elevation_at_toe,
            crest_level,armour_density,water_density,
            armour_mass,hs_toe,tp,n_waves,notional_permeability,armour_type):

    data = {
        'Armour Slope [v:h]': [f'1:{armour_slope}'],
        'Water Level [ m Datum]':[float(water_level)],
        'Bed Elevation at Toe [m Datum]':[float(bed_elevation_at_toe)],
        'Crest Level [m Datum]':[float(crest_level)],
        'Armour Density [kg/m3]':[float(armour_density)],
        'Water Density [kg/m3]':[float(water_density)],
        'Armour Mass [kg]':[float(armour_mass)],
        'Significant Wave Height at Toe [m]':[float(hs_toe)],
        'Peak Wave Period [s]':[float(tp)],
        'Number of Waves [-]':[float(n_waves)],
        'Notional Permeability [-]': [float(notional_permeability)],
        'Armour Type':armour_type,

    }

    model = joblib.load('model_best.joblib')

    df = pd.DataFrame(data)

    prediction = model.predict(df)

    return prediction

'''
# Coastal Structure - % Damage
'''
page_load_start_time = time.time()
page_load_time_placeholder = st.sidebar.empty()

armour_type = st.radio(
     "Armour Type:",
     ('XBLOC', 'HANBAR', 'ROCK'))
col1, col2, col3 = st.columns(3)
with col1:
    armour_slope = st.number_input('Armour Slope [1:h]:', value = 1.5)
    crest_level = st.number_input('Crest Level [m Datum]:', value = 3.5)
    
    armour_mass = st.number_input('Armour Mass [kg]:', value = 2000)
    notional_permeability = st.number_input('Notional Permeability [-]:', value = 0.1)

with col2:
    water_level = st.number_input('Water Level [m Datum]:', value = 1.5)
    bed_elevation_at_toe = st.number_input('Bed Elevation at Toe [m Datum]:', value = -3.5)
    armour_density = st.number_input('Armour Density [kg/m3]:', value = 2650)
    water_density = st.number_input('Water Density [kg/m3]:', value = 1020)

with col3:
    hs_toe = st.number_input('Significant Wave Height at Toe [m]:', value = 4.5)
    tp = st.number_input('Peak Wave Period [s]:', value = 12.5)
    n_waves = st.number_input('Number of Waves [-] :', value = 1000)

col1, col2, col3 = st.columns(3)
with col2:
    if st.button('Predict'):
        
        pred = predict(armour_slope,water_level,bed_elevation_at_toe,
                crest_level,armour_density,water_density,
                armour_mass,hs_toe,tp,n_waves,notional_permeability,armour_type)
        
        pred = 100 if pred > 100 else pred

        st.markdown("Estimated Damage: " + str(pred) + "%")

    else:
        st.write('Enter the parameters first')
    page_load_duration = time.time() - page_load_start_time
    page_load_time_placeholder.markdown(f'{round(page_load_duration, 3)} seconds')