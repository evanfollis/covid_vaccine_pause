import pandas as pd, numpy as np
import matplotlib
import datetime
import matplotlib.dates as mdates

us_population = 330000000
daily_cases = 50000
daily_vaccinations = 3500000
total_deaths = 563000
total_cases = 31350000

daily_chance_of_covid = daily_cases / us_population
chance_of_death_with_covid = total_deaths / total_cases

# created a vector that decays the Rt value to 0.0 by the end of the year
# I also use this as a multiplier against the chances of catching COVID without the vaccine (decay chances to 0 as well)
Rt = 1.0
days_covid_left = 260 # number of days to end of year as of 4/15/2021
Rt_vector = np.geomspace(
    start=1.0, 
    stop=0.01, 
    num=int(days_covid_left)
)
Rt_vector = (1 - Rt_vector).tolist()[::-1]

def get_deaths(percent_decrease_in_vaccines, days_paused):
    unvaccinated_daily = daily_vaccinations * percent_decrease_in_vaccines
    unvaccinated_with_covid = 0
    for day in range(days_paused):
        chance_of_covid = daily_chance_of_covid * Rt_vector[day]
        daily_unvaccinated_with_covid = unvaccinated_daily * chance_of_covid
        # this next part is used to include all of the people that contaminated people infect
        # this value decays with the Rt vector
        tracker = [daily_unvaccinated_with_covid]
        for i in range(day, days_covid_left, 5):
            tracker.append(tracker[-1] * Rt_vector[i])
        unvaccinated_with_covid += sum(tracker)
    deaths = chance_of_death_with_covid * unvaccinated_with_covid
    return deaths
    
def create_deaths_df(percent_decreases_in_vaccines=[0.1, 0.25]):
    df = pd.DataFrame(index=range(days_covid_left))
    for decrease in percent_decreases_in_vaccines:
        deaths = []
        for i in range(0, days_covid_left):
            deaths.append(get_deaths(decrease, i))
        df[f'{int(decrease * 100)}% Decrease in Vaccines'] = deaths
    df.index = pd.date_range(datetime.datetime.today(), datetime.datetime(2021, 12, 31))
    return df


# Create graph of data
fig, ax = plt.subplots(figsize=(15, 6))

plot_deaths([0.1, .25]).plot(ax=ax)
ax.set_xlabel('')
ax.set_ylabel('Deaths')
ax.set_title('COVID Death Impact From Vaccine Pause', fontsize=14)
ax.get_yaxis().set_major_formatter(
    matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'));
