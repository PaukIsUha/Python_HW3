from dash import Dash, html, dcc, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objs as go

app = Dash(__name__)

df = pd.read_csv("crimedata.csv")

print(list(df.columns))

states_data = list(df['state'].unique())
crimes_data = ['murders', 'rapes', 'robberies', 'assaults', 'burglaries', 'larcenies', 'auto theft', 'arsons']
race_data = ['white', 'black', 'asian', 'hisp']
cap_to_race = {'white': 'whitePerCap', 'black': 'blackPerCap', 'indian': 'indianPerCap',
               'asian': 'AsianPerCap', 'other': 'OtherPerCap', 'hisp': 'HispPerCap'}
race_name_to_race = {'white': 'racePctWhite', 'black': 'racepctblack',
               'asian': 'racePctAsian', 'hisp': 'racePctHisp'}

app.layout = html.Div(children=[
    html.H1(children='Кол-во преступлений по штатам'),

    html.Div([
        dcc.Dropdown(crimes_data, 'murders', id='crimes-name-for-per-state')
    ]),

    dcc.Graph(
        id='crimes-per-state'
    ),

    html.H1(children='Процент преступлений по рассам'),
    html.Div([

        dcc.Dropdown(states_data + ['ALL'], 'ALL', id='state-for-per-race')
    ]),
    dcc.Graph(
        id='race-pie-chart',
    ),

    html.H1(children='Типы преступлений'),
    html.Div([
        dcc.Dropdown(states_data + ['ALL'], 'ALL', id='state-for-per-types')
    ]),
    dcc.Graph(
        id='types-bar-chart',
    ),

    html.H1(children='Статистика по возрасту'),
    html.Div([
        dcc.Dropdown(states_data + ['ALL'], 'ALL', id='state-for-per-age')
    ]),
    dcc.Graph(
        id='age-pie-chart',
    ),

    html.H1(children='Зависимость кол-во преступлений от дохода на душу населения'),
    html.Div([
        dcc.Dropdown(states_data + ['ALL'], 'ALL', id='state-for-per-cap')
    ]),
    html.Div([
        dcc.Dropdown(race_data, 'hisp', id='race-for-per-age')
    ]),
    dcc.Graph(
        id='cap-graphic',
    ),
])


@app.callback(
    Output('crimes-per-state', 'figure'),
    Input('crimes-name-for-per-state', 'value')
)
def update_main_figure(selected_crime):
    crimes_state = df.groupby(by='state', as_index=False).sum()
    return px.bar(crimes_state, x='state', y=selected_crime)


@app.callback(
    Output('race-pie-chart', 'figure'),
    Input('state-for-per-race', 'value')
)
def update_race_figure(selected_state):
    crimes_state = df
    if selected_state != 'ALL':
        crimes_state = df[df['state'] == selected_state]

    race = {'pct_race': [crimes_state['racepctblack'].mean(),
                         crimes_state['racePctWhite'].mean(),
                         crimes_state['racePctAsian'].mean(),
                         crimes_state['racePctHisp'].mean()],
            'race_name': ['Black', 'White', 'Asian', 'Hisp']}
    return px.pie(values=race['pct_race'], names=race['race_name'])


@app.callback(
    Output('types-bar-chart', 'figure'),
    Input('state-for-per-types', 'value')
)
def update_types_figure(selected_state):
    crimes_state = df
    if selected_state != 'ALL':
        crimes_state = df[df['state'] == selected_state]

    article = {
        'pct_crimes': [crimes_state['murders'].sum(), crimes_state['rapes'].sum(), crimes_state['robberies'].sum(),
                       crimes_state['assaults'].sum(), crimes_state['burglaries'].sum(),
                       crimes_state['larcenies'].sum(),
                       crimes_state['autoTheft'].sum(), crimes_state['arsons'].sum()],
        'crimes_name': crimes_data}
    return px.bar(y=article['pct_crimes'], x=article['crimes_name'], labels=['name crime', 'count'])


@app.callback(
    Output('age-pie-chart', 'figure'),
    Input('state-for-per-age', 'value')
)
def update_age_figure(selected_state):
    crimes_state = df
    if selected_state != 'ALL':
        crimes_state = df[df['state'] == selected_state]

    age = {'pct_age': [crimes_state['agePct12t21'].mean(),
                       crimes_state['agePct12t29'].mean(),
                       crimes_state['agePct16t24'].mean(),
                       crimes_state['agePct65up'].mean()],
           'age_range': ['from 12 to 21', 'from 12 to 29', 'from 16 to 24', '65 up']}
    return px.pie(values=age['pct_age'], names=age['age_range'])


@app.callback(
    Output('cap-graphic', 'figure'),
    Input('state-for-per-cap', 'value'),
    Input('race-for-per-age', 'value')
)
def update_cap_figure(selected_state, selected_race):
    crimes_state = df
    if selected_state != 'ALL':
        crimes_state = df[df['state'] == selected_state]

    crimes_state = crimes_state.groupby(by=cap_to_race[selected_race], as_index=False).sum()
    crimes_state = crimes_state.sort_values(by=cap_to_race[selected_race])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(crimes_state[cap_to_race[selected_race]]), y=list(crimes_state[race_name_to_race[selected_race]])))
    return fig


if __name__ == '__main__':
    app.run_server(debug=False)
