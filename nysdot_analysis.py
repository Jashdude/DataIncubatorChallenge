import pandas as pd
from sodapy import Socrata
import statsmodels.api as sm
import matplotlib.pyplot as plt

token = 'xZVOY6de69f7Wym6roVBmRd39'
client = Socrata("data.ny.gov", app_token=token)

results = client.get("ah74-pg4w", limit=2400000)
full_df = pd.DataFrame.from_records(results)

print(full_df.groupby(['event_type']).size().sort_values(ascending=False).reset_index(name ='Count').describe())
print(full_df.groupby(['facility_name']).size().sort_values(ascending=False).reset_index(name ='Count').describe())

full_df['year_of_date'] = pd.to_datetime(full_df['create_time'])
full_df['year'] = full_df['year_of_date'].dt.year
full_df['day_of_week'] = full_df['year_of_date'].dt.weekday_name
full_grp_df = full_df.sort_values('year', ascending=True).groupby(['year']).size().reset_index(name = 'Yearly_Count')
full_cnt_df = full_grp_df[['year','Yearly_Count']]
full_year_df = full_cnt_df.set_index('year')
full_day_df = full_df.sort_values('day_of_week', ascending=True).groupby(['day_of_week']).size().reset_index(name = 'Day_Count')
full_day_cnt_df = full_day_df[['day_of_week','Day_Count']]
full_dcnt_df = full_day_cnt_df.set_index('day_of_week')
print(full_dcnt_df)

data = pd.crosstab(full_cnt_df.year, full_cnt_df.Yearly_Count).plot(kind='bar')
plt.title('Traffic Events Count by Year')
plt.xlabel('Year')
plt.ylabel('Count of Events')
plt.savefig('traffic_evnt_cnt')
plt.show()

day_cnt_data = pd.crosstab(full_day_cnt_df.day_of_week, full_day_cnt_df.Day_Count).plot(kind='bar')
plt.title('Traffic Events Count by Day of Week')
plt.xlabel('Day of Week')
plt.ylabel('Count of Events')
plt.savefig('traffic_evnt_daily_cnt')
plt.show()