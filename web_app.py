import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
import plotly.express as px

# path of the dataset which should be present in the same folder as the python file
DATA_URL = (
    r"C:\Users\DELL PC\Desktop\web_app\`Motor_Vehicle_Collisions_-_Crashes.csv`"
)

st.title("Motor Vehicle collision in New York City 🗽 💥 🚗") #provide the heading
st.markdown("Note : This application is a streamlit dashboard that can be used to analyze motor vehicle collision in NYC") # provide the sub heading 

# reading the dataset
@st.cache(persist = True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows = nrows, parse_dates = [['CRASH DATE','CRASH TIME']])
    data.dropna(subset = ['LATITUDE','LONGITUDE'], inplace = True)
    lowercase = lambda x:str(x).lower()
    data.rename(lowercase,axis = 'columns', inplace = True)
    # print(data.columns)
    data.rename(columns = {'crash date_crash time' : 'date/time', 'number_of_persons_injured' : 'injured_persons','number of pedestrians injured':'injured_pedestrians','number of cyclist injured':'injured_cyclists','number of motorist injured':'injured_motorists','on street name' : 'on_street_name'}, inplace = True)
    return data

data = load_data(100000) # Here we are just analysing 100000 rows out of 1.6 million rows
original_data = data

# plotting the 2d points on New York City map representing the location of the accidents or collisions which can be altered using slider in web app 
st.header("Where are the most people injured in NYC")
injured_people = st.slider("Number of persons injured in vehicle", 0,19) # 19 = maximum number of peopleinjured
st.map(data.query("injured_persons >= @injured_people")[["latitude","longitude"]].dropna(how = "any"))

# Number of collision represented in 3D format of New York City map at given time, where time can also be altered using slitered in web app

st.header("How many collisions occur during a given time of day ?")
# hour = st.selectbox("Time Of collision", range(0,24),1)
hour = st.slider("Time of collision", 0,23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collision between %i:00 and %i:00" % (hour,(hour + 1) % 24))

midpoint = (np.average(data['latitude']), np.average(data['longitude']))

# Use of pydeck library which is used to give the 3D effects and to alter the other aspects such as radius and pitch of the plots 
st.write(pdk.Deck(
    map_style = "mapbox://style/mapbox/light-v9",
    initial_view_state = {
        "latitude" : midpoint[0],
        "longitude" : midpoint[1],
        "zoom" : 11,
        "pitch" : 50,
    },
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data = data[['date/time','latitude','longitude']],
            get_position = ['longitude','latitude'],
            radius = 100,
            extruded = True,
            pickable = True,
            elevation_scale = 4,
            elevation_range = [0,1000],
        ),
    ],
))

# Ploting of histogram to represent the trend in accident in given hour. Here the breakdown is in minutes. 
st.header("Breakdown by minute between %i:00 and %i:00" % (hour,(hour+1)%24))

filtered_data = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
hist = np.histogram(filtered_data['date/time'].dt.minute, bins  = 60, range = (0,60))[0]
chart_data = pd.DataFrame({'minute' : range(60),'crashes' : hist})
fig = px.bar(chart_data, x = 'minute', y = 'crashes', hover_data = ['minute','crashes'], height = 400)
st.write(fig)

# Represents the top 5 streets where most number of accidents occured segregated by type of people injured
st.header("Top 5 dangerous streets by affected type of people injured ")
select = st.selectbox('Affected type of people',['Pedestrians','Cyclists','Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how="any")[:5])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how="any")[:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how="any")[:5])


# Raw dataeset 
if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
