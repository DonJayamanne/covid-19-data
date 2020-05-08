# %% [markdown]
# * Looks like the press is starting to ask some of the same questions I'm asking with this analysis:
#     * https://www.mercurynews.com/2020/04/08/how-california-has-contained-coronavirus-and-new-york-has-not/
#  %%
import time
t0 = time.clock()

#  %%
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly

default_line_thickness=2
default_width = 1280
default_height = 800
default_plot_color = 'rgba(0, 0, 0, 0)'
default_grid_color = 'rgba(225, 225, 225, 255)'

webpage_folder = 'webpage/'
html_graphs = open(webpage_folder + "CovidAnalysis.html",'w',)
html_graphs.write("<html><head><style>div {margin-left:50px; margin-right:5%; font-family: \"Verdana\"}</style></head><body>"+"\n")
html_graphs.write('<div style=\'margin:50px\'><h1>Data as of ' + datetime.now().strftime('%m/%d/%y')+ '<br/></h1>')
#html_graphs.write('<div style=\'margin:50px\'><h1>Data as of 04/25/2020<br/></h1>')
html_graphs.write('''
Please wait to load all the graphs. This page is not setup to be fast loading. :)<br/><br/>
Also be aware that you can now can single click on a location in the legend to show and hide that
location in the graph. If you double click, you will hide all other locations, except for the one you
double clicked.
</div>''')
#  %% [markdown]
# **********************************************************************************************************
# # Setup
# 1. Read in the covid-19-data from nytimes for state and county (https://github.com/nytimes/covid-19-data)
# 2. Pull in a city density table
# 3. Pull in a state density table
# 4. Identify list of states, counties and cities to graph
# **********************************************************************************************************
#  %%
state_cov_data = pd.read_csv('us-states.csv')
county_cov_data = pd.read_csv('us-counties.csv')

population_county = pd.read_csv('county-population-2013.csv')
population_county.drop(columns={'Core_Based_Statistical_Area'}, inplace=True)
population_county.rename(columns={'population2013': 'population'}, inplace=True)
population_county.index = [population_county.county, population_county.state]

population_city_density = pd.read_csv('city_density.csv')
population_city_density = population_city_density.rename(columns={'City': 'citystate', 'Population Density (Persons/Square Mile)': 'density', '2016 Population': 'population', 'Land Area (Square Miles)': 'area'} )
population_city_density[['city', 'state']] = population_city_density.citystate.str.split(', ', expand=True)

population_state_density = pd.read_csv('state_density.csv')
population_state_density = population_state_density.rename(columns={'State': 'state', 'Density': 'density', 'Pop': 'population', 'LandArea': 'area'})

# Create a state abbreviation to full name mapping dataframe.
state_abbrev = pd.read_csv('StateAbbrev.csv')
state_abbrev.index = state_abbrev.abbrev
state_abbrev.drop(columns='abbrev', inplace=True)

# Get the land area table for county, split the 'county, SS' column into two.
county_land_area = pd.read_csv('LandAreaCounties.csv')
county_density = county_land_area['Areaname'].str.split(', ', n=1, expand=True)
county_density.rename(columns={0: 'county', 1: 'state'}, inplace=True)
county_density.dropna(inplace=True)
county_density.state = county_density.state.map(state_abbrev.state)

county_land_area['county'] = county_density.county
county_land_area['state'] = county_density.state
county_land_area.dropna(inplace=True)
county_land_area['key'] = county_land_area.county + ',' + county_land_area.state
county_land_area.drop_duplicates(subset='key', inplace=True)
county_land_area.index = county_land_area.key
county_land_area.drop(columns={'Areaname', 'county', 'state', 'key'}, inplace=True)

county_density['population'] = population_county.loc[list(county_density.itertuples(name=None, index=False))].population.values
county_density['key'] = county_density.county + ',' + county_density.state
county_density['area'] = county_density.key.map(county_land_area.land_area)
county_density['density'] = county_density.population / county_density.area
county_density.dropna(subset=['density'], inplace=True)

county_cities_east = [
    ['District of Columbia', 'District of Columbia', ['District of Columbia'], False],
    ['Massachusetts', 'Suffolk', ['Boston'], False],
    ['New York', 'Bronx', ['New York'], False],
    ['New York', 'Queens', ['New York'], False],
    ['New York', 'Kings', ['New York'], False],
    ['New York', 'Manhattan', ['New York'], False],
    ['New York', 'Brooklyn', ['New York'], False],
    ['New York', 'Staten Island', ['New York'], False],
    ['New York', 'New York City', ['New York'], False],
    ['New Jersey', 'Bergen', ['Newark', 'Jersey City'], False],
    ['Pennsylvania', 'Philadelphia', ['Philadelphia'], False]
]

county_cities_west = [
    ['Arizona', 'Maricopa', ['Phoenix'], False],
    ['California', 'Los Angeles', ['Los Angeles'], False],
    ['California', 'San Francisco', ['San Francisco'], False],
    ['California', 'San Diego', ['San Diego'], False],
    ['Washington', 'King', ['Seattle'], True],
    ['Washington', 'Snohomish', ['Everett'], True]
]

county_cities_south = [
    ['Florida', 'Miami-Dade', ['Miami'], False],
    ['Florida', 'Broward', ['Fort Lauderdale'], False],
    ['Florida', 'Duval', ['Jacksonville'], False],
    ['Georgia', 'Fulton', ['Atlanta'], False],
    ['Louisiana', 'Orleans', ['New Orleans'], False],
    ['South Carolina', 'Charleston', ['Charleston'], True],
    ['Tennessee', 'Davidson', ['Nashville'], False],
    ['Texas', 'Harris', ['Houston'], False],
    ['Texas', 'Bexar', ['San Antonio'], False],
    ['Texas', 'Dallas', ['Dallas'], False],
    ['Texas', 'Travis', ['Austin'], False]
]

county_cities_midwest = [
    ['Illinois', 'Cook', ['Chicago'], False],
    ['Indiana', 'Hamilton', ['Carmel'], False],
    ['Indiana', 'Marion', ['Indianapolis'], False],
    ['Michigan', 'Wayne', ['Detroit'], False],
    ['Wisconsin', 'Milwaukee', ['Milwaukee'], False],
    ['Ohio', 'Cuyahoga', ['Cleveland'], True]
]

county_cities_east_map = pd.DataFrame(county_cities_east, columns = ['state', 'county', 'cities', 'show_by_default'])
county_cities_west_map = pd.DataFrame(county_cities_west, columns = ['state', 'county', 'cities', 'show_by_default'])
county_cities_midwest_map = pd.DataFrame(county_cities_midwest, columns = ['state', 'county', 'cities', 'show_by_default'])
county_cities_south_map = pd.DataFrame(county_cities_south, columns = ['state', 'county', 'cities', 'show_by_default'])

states_east = county_cities_east_map.drop(columns=['cities', 'county']).drop_duplicates()
states_west = county_cities_west_map.drop(columns=['cities', 'county']).drop_duplicates()
states_midwest = county_cities_midwest_map.drop(columns=['cities', 'county']).drop_duplicates()
states_south = county_cities_south_map.drop(columns=['cities', 'county']).drop_duplicates()
states = pd.concat([states_east, states_midwest, states_west, states_south])
states.reset_index(inplace=True)

counties_cities = pd.concat([county_cities_east_map, county_cities_west_map, county_cities_midwest_map, county_cities_south_map])
counties_cities.reset_index(inplace=True)

# %% [markdown]
# **********************************************************************************************************
# # New cases per day
# **********************************************************************************************************
# %%
def movingaverage(values, window):
    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'valid')
    return sma

def plotnewcases(state='all', county='all', show_by_default=True):
    if (state == 'all'):
        total_cases_by_date = state_cov_data.groupby('date').sum()
        minimum_cases = 100
    elif (county == 'all'):
        total_cases_by_date = state_cov_data[state_cov_data.state == state].groupby('date').sum()
        minimum_cases = 15
    else:
        total_cases_by_date = county_cov_data[(county_cov_data.state == state) & (county_cov_data.county == county)].groupby('date').sum()
        minimum_cases = 15

    if (len(total_cases_by_date) > 0):
        total_cases_by_date = total_cases_by_date.reset_index()
        total_cases_by_date = total_cases_by_date[total_cases_by_date.cases > minimum_cases]
        delta_cases = total_cases_by_date.cases.to_numpy()[1:] - total_cases_by_date.head(len(total_cases_by_date)-1).cases.to_numpy()[0:]

        delta_cases_ma = movingaverage(delta_cases, 7)
        df = pd.DataFrame(delta_cases_ma, columns=['new'])
        df['days'] = df.index
        df = df[df.new.gt(0).idxmax():]
        df.reset_index(inplace=True)

        if (state != 'all' and county != 'all'):
            name = state + ' - ' + county
        else:
            name = state

        if (show_by_default):
            visible = True
        else:
            visible = 'legendonly'

        fig.add_trace(
            go.Scatter(x=df.days, y=df.new, mode='lines', name=name, line = { 'width': default_line_thickness },
            hovertemplate='new cases: %{y:,.0f}<br>day: %{x}', visible=visible)
        )

row = 1
layout = go.Layout(
        title = 'New cases for US',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since new cases started increasing',
        yaxis_title='New cases'
)
fig = go.Figure(layout=layout)
plotnewcases()

fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write('''
<br/><br/><div>
<h1>New cases per day</h1><br/>
This trend line is a moving average of new cases over time. First for the US overall then by state (not all are represented here, just ones I found most interesting.
</div>''')
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")


#############################

row += 1
layout = go.Layout(
        title = 'New cases by state',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since new cases started increasing',
        yaxis_title='New cases'
)

fig = go.Figure(layout=layout)
for index, state in states.iterrows():
    plotnewcases(state.state, 'all', state.show_by_default)

fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")

row += 1
layout = go.Layout(
        title = 'New cases by county',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since new cases started increasing',
        yaxis_title='New cases'
)

fig = go.Figure(layout=layout)
for index, r in counties_cities.iterrows():
    plotnewcases(r.state, r.county, r.show_by_default)

fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")


# %% [markdown]
# **********************************************************************************************************
# # State Totals
# **********************************************************************************************************
# %%
def plottotalcases(state, county = 'all', show_by_default=True):
    if county == 'all':
        data = state_cov_data[state_cov_data.state == state][['date', 'cases']]
    else:
        data = county_cov_data[county_cov_data.state == state][['date', 'cases', 'county']]
        data = data[county_cov_data.county == county][['date', 'cases']]

    data = data[data.cases >= starting_cases]
    if len(data['cases']):
        data.index = [x for x in range(0, len(data))]

        if (show_by_default):
            visible = True
        else:
            visible = 'legendonly'

        if (county == 'all'):
            fig.add_trace(
                go.Scatter(x=data.index, y=data.cases, mode='lines', name=state, line = { 'width': default_line_thickness },
                hovertemplate='total cases: %{y:,.0f}<br>day: %{x}', visible=visible)
            )
        else:
            fig.add_trace(
                go.Scatter(x=data.index, y=data.cases, mode='lines', name=county + ', ' + state, line = { 'width': default_line_thickness },
                hovertemplate='total cases: %{y:,.0f}<br>day: %{x}', visible=visible)
            )

row += 1
starting_cases = 1000
layout = go.Layout(
        title = 'Total cases by state after hitting ' + str(starting_cases) + ' cases',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since ' + str(starting_cases) + ' cases were hit',
        yaxis_title='Total cases'
)

fig = go.Figure(layout=layout)
for index, s in states.iterrows():
    plottotalcases(s.state, 'all', s.show_by_default)

fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write('''
<br/><br/><div>
<h1>State and County Total cases</h1>
</div>''')
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")

#  %% [markdown]
# **********************************************************************************************************
# # County Totals
# **********************************************************************************************************
row += 1
starting_cases = 200
layout = go.Layout(
        title = 'Total cases by county after hitting ' + str(starting_cases) + ' cases',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since ' + str(starting_cases) + ' cases were hit',
        yaxis_title='Total cases'
)
fig = go.Figure(layout=layout)

for index, r in counties_cities.iterrows():
    plottotalcases(r.state, r.county, r.show_by_default)

fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")

#  %% [markdown]
# **********************************************************************************************************
# # State cases adjusted for population
# **********************************************************************************************************
#  %%
def stateplotpercapita(state, show_by_default):
    data = state_cov_data[state_cov_data.state == state][['date', 'cases']]
    data = data[data.cases >= starting_cases]
    state_population = population_state_density[population_state_density.state == state]
    if len(state_population):
        data.index = [x for x in range(0, len(data))]
        plotdata = (data.cases / state_population.population.values[0]) * 1000
        if len(data['cases']):
            if (show_by_default):
                visible = True
            else:
                visible = 'legendonly'

            fig.add_trace(
                go.Scatter(x=data.index, y=plotdata, mode='lines', name=state + ' (' + str.format('{0:,}', state_population.population.values[0]) + ' people)', line = { 'width': default_line_thickness },
                hovertemplate='cases per 1000: %{y:,.0f}<br>day: %{x}', visible=visible)
            )

row += 1
starting_cases = 1000
layout = go.Layout(
        title = 'Total state cases per 1,000 people after hitting ' + str(starting_cases) + ' cases',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since ' + str(starting_cases) + ' cases were hit',
        yaxis_title='Total cases per 1,000 people'
)
fig=go.Figure(layout=layout)

for index, s in states.iterrows():
    stateplotpercapita(s.state, s.show_by_default )

fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write('''
<br/><br/><div>
<h1>State and County cases adjusted for population</h1><br/>
To better get a sense of how different states may be handling the virus outbreak, you can
adjust the graphs to account for the number of people who live in each state. A state that has
100,000 people vs 8,000,000 people will obviously look far better with regard to total cases
because they have 80x less people. By factoring in the population of a state, this is difference
is accounted for.
</div>''')
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")

#  %% [markdown]
# **********************************************************************************************************
# # County cases adjusted for population
# **********************************************************************************************************
#  %%
def countyplotpercapita(state, county, show_by_default):
    data = county_cov_data[county_cov_data.state == state][['date', 'cases', 'county']]
    data = data[county_cov_data.county == county][['date', 'cases']]
    data = data[data.cases >= starting_cases]
    county_population = population_county[(population_county.state == state) & (population_county.county == county)]
    if len(county_population):
        data.index = [x for x in range(0, len(data))]
        plotdata = (data.cases / county_population.population.values[0]) * 1000
        if len(data['cases']):
            if (show_by_default):
                visible = True
            else:
                visible = 'legendonly'

            fig.add_trace(
                go.Scatter(x=data.index, y=plotdata, mode='lines', name=county + ', ' + state + ' (' + str.format('{0:,}', county_population.population.values[0]) + ' people)', line = { 'width': default_line_thickness },
                hovertemplate='cases per 1000: %{y:,.0f}<br>day: %{x}', visible=visible)
            )

row += 1
starting_cases = 1000
layout = go.Layout(
        title = 'Total county cases per 1,000 people after hitting ' + str(starting_cases) + ' cases',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since ' + str(starting_cases) + ' cases were hit',
        yaxis_title='Total cases per 1,000 people'
)
fig=go.Figure(layout=layout)

for index, r in counties_cities.iterrows():
    countyplotpercapita(r.state, r.county, r.show_by_default)

fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")

#  %% [markdown]
# **********************************************************************************************************
# # State cases adjusted for population density
# **********************************************************************************************************
#  %%
def stateplotbydensity(state, show_by_default):
    data = state_cov_data[state_cov_data.state == state][['date', 'cases']]
    data = data[data.cases >= starting_cases]
    state_density = population_state_density[population_state_density.state == state]
    if len(state_density):
        data.index = [x for x in range(0, len(data))]
        plotdata = (data.cases / state_density.density.values[0])
        if len(data['cases']):
            lastindex = len(data) - 1
            if (show_by_default):
                visible = True
            else:
                visible = 'legendonly'

            fig.add_trace(
                go.Scatter(x=data.index, y=plotdata, mode='lines', name=state + ' (' + str.format('{0:,}', int(round(state_density.density.values[0],0))) + ' ppl/mi^2)', line = { 'width': default_line_thickness },
                hovertemplate='density adjusted cases: %{y:,.0f}<br>day: %{x}', visible=visible)
            )

row += 1
starting_cases = 200
layout = go.Layout(
        title = 'Total state trend after hitting ' + str(starting_cases) + ' cases factoring out population density',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since ' + str(starting_cases) + ' cases were hit',
        yaxis_title='Total density adjusted cases'
)
fig=go.Figure(layout=layout)

for index, s in states.iterrows():
    stateplotbydensity(s.state, s.show_by_default)

fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write('''
<br/><br/><div>
<h1>State cases adjusted for population density</h1><br/>
Each state and county obviously has a population and an area in which this population lives. *Pretend* for a moment that Texas only has 100,000
people total. Also *pretend* that Rhode Island has 100,000 people. However, you also know that the
land area of Rhode Island is much, much smaller than that of Texas. So, if Rhode Island gets 5,000 cases of the virus
and Texas also gets 5,000 case, then you can say with high confidence that the people in Texas are likely completely
ignoring advice to keep a minimum distance from others. I mean how else could they have the same number of cases as Rhode Island
where the same number of people are packed together?<br/>
<br/>
This graph removes this consideration from the comparison between states. As you can see, New Jersey is doing far worse than
than Ohio, Washington and California.
</div>''')
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")


#  %% [markdown]
# **********************************************************************************************************
# # County cases adjusted for population density
# **********************************************************************************************************
#  %%
def countyplotbydensity(county, state, show_by_default):
    data = county_cov_data[(county_cov_data.county == county) & (county_cov_data.state == state)][['date', 'cases']]
    data = data[data.cases >= starting_cases]
    density = county_density[(county_density.county == county) & (county_density.state == state)]
    if len(density):
        data.index = [x for x in range(0, len(data))]
        plotdata = (data.cases / density.density.values[0])
        if len(data['cases']):
            lastindex = len(data) - 1
            if (show_by_default):
                visible = True
            else:
                visible = 'legendonly'

            fig.add_trace(
                go.Scatter(x=data.index, y=plotdata, mode='lines', name=state + ' - ' + county + ' (' + str.format('{0:,}', int(round(density.density))) + ' ppl/mi^2)', line = { 'width': default_line_thickness },
                hovertemplate='density adjusted cases: %{y:,.0f}<br>day: %{x}', visible=visible)
            )

row += 1
starting_cases = 200
layout = go.Layout(
        title = 'Total county trend after hitting ' + str(starting_cases) + ' cases factoring out population density',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since ' + str(starting_cases) + ' cases were hit',
        yaxis_title='Total density adjusted cases'
)
fig=go.Figure(layout=layout)

for index, r in counties_cities.iterrows():
    countyplotbydensity(r.county, r.state, r.show_by_default)
fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")

#  %% [markdown]
# **********************************************************************************************************
# # City cases adjusted for population
# **********************************************************************************************************
#  %%
def cityplotpercapita(state, city, show_by_default):
    county = 'not found'
    for index, x in counties_cities.iterrows():
        if city in x.cities and state == x.state:
            county = x.county

    cov_at_county_level = county_cov_data[county_cov_data.state == state][county_cov_data.county == county][['date', 'cases']]
    cov_at_county_level = cov_at_county_level[cov_at_county_level.cases >= starting_cases]
    city_population = population_city_density[population_city_density.state == state][population_city_density.city == city]
    if (len(city_population)):
        cov_at_county_level.index = [x for x in range(0, len(cov_at_county_level))]
        plotdata = (cov_at_county_level.cases / city_population.population.values[0]) * 1000
        if len(cov_at_county_level['cases']):
            lastindex = len(cov_at_county_level) - 1
            if (show_by_default):
                visible = True
            else:
                visible = 'legendonly'

            fig.add_trace(
                go.Scatter(x=cov_at_county_level.index, y=plotdata, mode='lines', name=city + ', ' + state + ' (' + str.format('{0:,}', city_population.population.values[0],0) + ' people)', line = { 'width': default_line_thickness },
                    hovertemplate='cases per 1000: %{y:,.3f}<br>day: %{x}', visible=visible)
            )

row += 1
starting_cases = 20
layout = go.Layout(
        title = 'Total city cases per 1,000 people after hitting ' + str(starting_cases) + ' cases',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since ' + str(starting_cases) + ' cases were hit',
        yaxis_title='Total cases per 1,000 people'
)
fig=go.Figure(layout=layout)

for index, r in counties_cities[~counties_cities['cities'].apply(tuple).duplicated()].iterrows():
    for c in r.cities:
        cityplotpercapita(r.state, c, r.show_by_default)

fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write('''
<br/><br/><div>
<h1>City total cases adjusted for population</h1><br/>
To better get a sense of how different cities may be handling the virus outbreak, you can
adjust the graphs to account for the number of people who live in each city. A city that has
100,000 people vs 8,000,000 people will obviously look far better with regard to total cases
because they have 80x less people. By factoring in the population of a city, this is difference
is accounted for.
</div>''')
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")

#  %% [markdown]
# **********************************************************************************************************
# # City total cases adjusted for population density
# **********************************************************************************************************
#  %%
def cityplotbydensity(state, city, show_by_default):
    county = 'not found'
    for index, x in counties_cities.iterrows():
        if city in x.cities and state == x.state:
            county = x.county

    data = county_cov_data[county_cov_data.state == state][county_cov_data.county == county][['date', 'cases']]
    data = data[data.cases >= starting_cases]
    city_density = population_city_density[population_city_density.state == state][population_city_density.city == city]
    if (len(city_density)):
        data.index = [x for x in range(0, len(data))]
        plotdata = data.cases / city_density.density.values[0]
        if len(data['cases']):
            lastindex = len(data) - 1
            if (show_by_default):
                visible = True
            else:
                visible = 'legendonly'

            fig.add_trace(
                go.Scatter(x=data.index, y=plotdata, mode='lines', name=city + ', ' + state + ' (' + str.format('{0:,}', int(round(city_density.density.values[0],0))) + ' ppl/mi^2)', line = { 'width': default_line_thickness },
                    hovertemplate='density adjusted cases: %{y:,.3f}<br>day: %{x}', visible=visible)
            )

row += 1
starting_cases = 20
layout = go.Layout(
        title = 'Total city trend after hitting ' + str(starting_cases) + ' cases factoring out population density',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since ' + str(starting_cases) + ' cases were hit',
        yaxis_title='Total density adjusted cases'
)
fig=go.Figure(layout=layout)

for index, r in counties_cities[~counties_cities['cities'].apply(tuple).duplicated()].iterrows():
    for c in r.cities:
        cityplotbydensity(r.state, c, r.show_by_default)

fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write('''
<br/><br/><div>
<h1>City total cases adjusted for population density</h1><br/>
Same trends as described for state cases adjusted for population density, but applied at the city level instead. The intent of
this graph is to discount the consideration that some cities growth rates are so fast because those cities are so densely populated.
This was a common explanation as to why New York was growing so much faster than other cities. Though even when taking density into account,
New York's trend <b>still</b> beats all others.
</div>''')
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")


#  %% [markdown]
# **********************************************************************************************************
# # City deaths adjusted for population density
# **********************************************************************************************************
#  %%
def citydeathsplotbydensity(state, city, show_by_default):
    county = 'not found'
    for index, x in counties_cities.iterrows():
        if city in x.cities and state == x.state:
            county = x.county

    data = county_cov_data[county_cov_data.state == state][county_cov_data.county == county][['date', 'deaths']]
    data = data[data.deaths >= starting_deaths]
    city_density = population_city_density[population_city_density.state == state][population_city_density.city == city]
    if (len(city_density)):
        data.index = [x for x in range(0, len(data))]
        plotdata = data.deaths / city_density.density.values[0]
        if len(data['deaths']):
            if (show_by_default):
                visible = True
            else:
                visible = 'legendonly'

            fig.add_trace(
                go.Scatter(x=data.index, y=plotdata.values, mode='lines', name=city + ', ' + state + ' (' + str.format('{0:,}', int(round(city_density.density.values[0],0))) + ' ppl/mi^2)', line = { 'width': default_line_thickness },
                hovertemplate='density adjusted deaths: %{y}<br>day: %{x}', visible=visible)
            )

row += 1
layout = go.Layout(
        title = 'Total city deaths trend after the first death factoring out population density',
        plot_bgcolor = default_plot_color,
        xaxis_gridcolor = default_grid_color,
        yaxis_gridcolor = default_grid_color,
        width=default_width,
        height=default_height,
        xaxis_title='Days since first person died from covid-19',
        yaxis_title='Total density adjusted deaths'
)
fig=go.Figure(layout=layout)
starting_deaths = 1

for index, r in counties_cities[~counties_cities['cities'].apply(tuple).duplicated()].iterrows():
    for c in r.cities:
        citydeathsplotbydensity(r.state, c, r.show_by_default)

fig.show()
plotly.offline.plot(fig, filename=webpage_folder + 'Chart_'+str(row)+'.html',auto_open=False)
html_graphs.write('''
<br/><br/><div>
<h1>City <b>deaths</b> adjusted for population density</h1><br/>
See description above concerning cases adjusted for population density. This is the same, but is about deaths, not just cases.
</div>''')
html_graphs.write("  <object data=\""+'Chart_'+str(row)+'.html'+"\" width=" + str(default_width * 1.10) + " height=" + str(default_height* 1.10) + "\"></object>"+"\n")

# %%
html_graphs.write('</body></html')
html_graphs.close()

# %%
print('Total run time: ', time.clock() - t0)





# %%