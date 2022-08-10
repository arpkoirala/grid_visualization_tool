from dash import Dash, dcc, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px

##1) build components
##2)make the layout
##3) interaction via the callback


#incorporate data into app

df=px.data.medals_long()

# building components

app = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])
mytitle = dcc.Markdown(children='# Power Systems Plots')
mygraph = dcc.Graph(figure={})
dropdown = dcc.Dropdown(options=['Bar Plot', 'Scatter Plot'],
                        value='Bar Plot',  # initial value displayed when page first loads
                        clearable=False)

#Customize your own layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([mytitle], width=6)
    ], justify='center'),
    dbc.Row([
        dbc.Col([mygraph], width=12)
    ]),
    dbc.Row([
        dbc.Col([dropdown], width=6)
    ], justify='center'),

], fluid=True)

# Callback
@app.callback(
    Output(mygraph,component_property='figure'),
    Input(dropdown,component_property='value')
 )

def update_graph(user_input):  # function arguments come from the component property of the Input
    if user_input == 'Bar Plot':
        fig = px.bar(data_frame=df, x="nation", y="count", color="medal")

    elif user_input == 'Scatter Plot':
        fig = px.scatter(data_frame=df, x="count", y="nation", color="medal",
                         symbol="medal")

    return fig  # returned objects are assigned to the component property of the Output



# Run app
if __name__=='__main__':
    app.run_server(port=8051)