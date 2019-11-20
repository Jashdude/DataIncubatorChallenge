import pandas as pd
from sodapy import Socrata
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from math import *

MY_APP_TOKEN = '<<Replace With you Token>>'
client = Socrata("data.lacity.org", app_token=MY_APP_TOKEN)

question_list = ["Q1: How many bookings of arrestees were made in 2018?",
        "Q2: How many bookings of arrestees were made in the area with the most arrests in 2018?",
        "Q3: What is the 95% quantile of the age of the arrestee in 2018? Only consider the following charge groups for your analysis: "
        "Vehicle Theft, Robbery, Burglary, Receive Stolen Property",
        "Q4: There are differences between the average age of an arrestee for the various charge groups. Are these differences statistically significant? For this question, "
        "calculate the Z-score of the average age for each charge group. "
        "Report the largest absolute value among the calculated Z-scores.",
        "Q5: Felony arrest incidents have been dropping over the years. Using a trend line (linear estimation) for the data from 2010 and 2018 (inclusive), "
        "what is the projected number of felony arrests in 2019? Round to the nearest integer. "
        "Note, the data set includes arrests for misdemeanor, felonies, etc.",
        "Q6. How many arrest incidents occurred within 2 km from the Bradbury Building in 2018? Use (34.050536, -118.247861) "
        "for the coordinates of the Bradbury Building",
        "Q7: How many arrest incidents were made per kilometer on Pico Boulevard during 2018? For this question, "
        "we will need to estimate the length of Pico Boulevard, which mostly stretches from east to west. "
        "To estimate the length of Pico Boulevard",
        "Q8.Some types of arrest incidents in certain areas occur at a highly disproportionate rate compared to their frequency city-wide. "
        "For example, let's say that the rate of larceny arrests (charge group code 6) is 1% in Devonshire (area ID 17). "
        "This rate may appear low but what if larceny arrests constitute 0.1 % city-wide?"
                 ]

#Q1 - How many bookings of arrestees were made in 2018?
#URL - "https://data.lacity.org/resource/yru6-6re4.json?$where=arst_date between '2018-01-01T00:00:00.000' and '2018-12-31T00:00:00.000'"

q1_res = client.get("yru6-6re4", where= "arst_date between '2018-01-01T00:00:00.000' and '2018-12-31T00:00:00.000'", limit=150000)
df = pd.DataFrame.from_records(q1_res)
#print(len(df))

# Q2: How many bookings of arrestees were made in the area with the most arrests in 2018?
q2_res = df.groupby(['area','area_desc']).size().sort_values(ascending=False).\
    reset_index(name ='Count').drop_duplicates(subset='area_desc')
#print(q2_res.loc[q2_res['Count'].idxmax()])

# Q3: What is the 95% quantile of the age of the arrestee in 2018?
charge_group = ['Vehicle Theft', 'Robbery', 'Burglary', 'Receive Stolen Property']

q3_res = df[df['grp_description'].isin(charge_group)]
print(len(q3_res))

q3_quant_df = q3_res[['age']]
q3_quant_df.age = q3_quant_df.age.astype(float)
#print(f"Describe: {q3_quant_df['age'].describe(percentiles=[0.95])}")

quant = q3_quant_df.quantile(0.95, axis=0)
#print(quant.astype(float))

#Q4: There are differences between the average age of an arrestee for the various charge groups.
# Are these differences statistically significant? For this question,
# calculate the Z-score of the average age for each charge group. Report the largest absolute value among the calculated Z-scores.
minors = ['Pre-Delinquency', 'Non-Criminal Detention']

q4_res = df[~df['grp_description'].isin(minors)]
#print(len(q4_res))
q4_res.age = q4_res.age.astype(float)
q4_res['z-score'] = (q4_res.age - q4_res.age.mean())/q4_res.age.std(ddof=0)
#print(abs(q4_res['z-score']).max())

#Q5: Felony arrest incidents have been dropping over the years. Using a trend line (linear estimation)
# for the data from 2010 and 2018 (inclusive), # what is the projected number of felony arrests in 2019?
# Round to the nearest integer. "
# https://data.lacity.org/resource/yru6-6re4.json?$where=arst_date between '2018-01-01T00:00:00.000' and '2018-12-31T00:00:00.000' and arst_typ_cd = 'F"

full_data = client.get("yru6-6re4", where="arst_date between '2010-01-01T00:00:00.000' "
                                      "and '2018-12-31T00:00:00.000'", limit = 1400000)

full_df = pd.DataFrame.from_records(full_data)
print(len(full_df))
full_df['year_of_date'] = pd.to_datetime(full_df['arst_date'])
full_df['year'] = full_df['year_of_date'].dt.year
full_grp_df = full_df.sort_values('year', ascending=True).groupby(['year']).size().reset_index(name = 'Crime_Count')
full_cnt_df = full_grp_df[['year','Crime_Count']]
full_crime_df = full_cnt_df.set_index('year')
print(full_crime_df)
print(full_crime_df.describe())

q5_get = client.get("yru6-6re4", where="arst_date between '2010-01-01T00:00:00.000' "
                                      "and '2018-12-31T00:00:00.000' and arst_typ_cd = 'F'", limit = 1231627)

q5_df = pd.DataFrame.from_records(q5_get)
print(len(q5_df))
q5_df['year_of_date'] = pd.to_datetime(q5_df['arst_date'])
q5_df['year'] = q5_df['year_of_date'].dt.year
#q5_grp_df = q5_df.groupby(['year','arst_typ_cd']).size().sort_values(ascending=True).reset_index(name ='Count')
q5_grp_df = q5_df.sort_values('year', ascending=True).groupby(['year','arst_typ_cd']).size().reset_index(name = 'Felony_Count')
q5_cnt_df = q5_grp_df[['year','Felony_Count']]
q5_felony_df = q5_cnt_df.set_index('year')
print(q5_felony_df)
#print(q5_felony_df.describe())

# Define dependent and independent variables
y = q5_felony_df['Felony_Count']
x1 = full_crime_df['Crime_Count']
x = sm.add_constant(x1)
results = sm.OLS(y, x).fit()
print(results.summary())
print(int(3081.12 + 0.2932 * 104277))

plt.scatter(x1, y)
yhat = 3081.12 + 0.2932* x1
line = plt.plot(x1, yhat, lw=4, c='Orange', label='regression line')
plt.xlabel('Crime_Count', fontsize=10)
plt.ylabel('Felony_Count', fontsize=10)
plt.show()

# "Q6. How many arrest incidents occurred within 2 km from the Bradbury Building in 2018? Use (34.050536, -118.247861) "
#  "for the coordinates of the Bradbury Building"

#"https://data.lacity.org/resource/yru6-6re4.json?$where=arst_date between '2018-01-01T00:00:00.000' and '2018-12-31T00:00:00.000' " \
#"and within_circle(location_1, 34.050536, -118.247861, 2000)"

def distance_calc(long, latt):
        bb_lon = -118.247861
        bb_lat = 34.050536

        lon = long
        lat = latt

        # Earth Radius
        R = 6371

        dlon = lon - bb_lon
        dlat = lat - bb_lat

        a = (sin(dlat/2))**2 + cos(bb_lat) * cos(lat) * (sin(dlon/2))**2
        c = 2 * np.arcsin(min(1,sqrt(a)))
        d = R * c
        return d

#11441
q6_data = client.get("yru6-6re4", where="arst_date between '2018-01-01T00:00:00.000' "
#                                       "and '2018-12-31T00:00:00.000' and within_circle(location_1, 34.050536, -118.247861, 2000)", limit = 1400000)
#q6_data = client.get("yru6-6re4", where="arst_date between '2018-01-01T00:00:00.000' "
                                      "and '2018-12-31T00:00:00.000'", limit = 1400000)

# dist = []
# final_dist = []
q6_data_df = pd.DataFrame.from_records(q6_data)
# for location in q6_data_df['location_1'].get_values():
#         #print(location['latitude'], location['longitude'])
#         dist.append(distance_calc(float(location['longitude']), float(location['latitude'])))
# 
# print(dist)
# final_dist.append([d for d in dist if int(d) <= 2000 ])
# for i in final_dist:
#         print(len(i))

q6_data_df['dist'] = q6_data_df.apply(distance_calc, args=(['location_1'][0],q6_data_df['location_1'][1]))
print(len(q6_data_df))