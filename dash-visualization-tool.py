from dash import Dash, html, dcc, Output, Input, ctx
import dash_bootstrap_components as dbc
# import plotly.express as px

# import plotly.graph_objects as go
# import networkx as nx
import dash_cytoscape as cyto



import pandas as pd
import pandapower as pp
import pandapower.plotting as pplt
# import pandapower.topology as top
# import plotly as plot
# import pandapower.plotting.plotly as pplotly

# import plotly.graph_objects as go
# import numpy as np
# from pandapower.plotting.plotly import get_plotly_color_palette
import matplotlib.pyplot
import numpy as np

from create_net import createLVnet, createMVnet
from generate_stylesheet import generate_stylesheet, generate_gradient_scale_line_loading, generate_gradient_scale_vlevel_undervoltage
from generate_cytoscape_elements import generate_nodes, generate_edges



##### creating LV net #####
pathLV = 'data/spanish_LV_net/'

bus_df = pd.read_excel(pathLV+'bus_df.xlsx')
bus_df= bus_df.drop(columns={'Unnamed: 0'})

ext_grid_df = pd.read_excel(pathLV+'ext_grid_df.xlsx')

line_df = pd.read_excel(pathLV+'line_df.xlsx')
line_df = line_df.drop(columns={'Unnamed: 0'})


load_per_bus_df = pd.read_excel(pathLV+'load_per_bus_df.xlsx')

netLV = createLVnet(bus_df, line_df, ext_grid_df, load_per_bus_df)

pathMV = 'data/MV_benchmarks/'
netMV = createMVnet(pathMV+'bus33.json')

Pandanet = netMV

pp.runpp(Pandanet)
loading_values = Pandanet.res_line.loading_percent.values
vlevels_pu = Pandanet.res_bus.vm_pu.values





## DASHH



green_to_red = ['#00FF00','#11FF00','#22FF00','#33FF00','#44FF00','#55FF00','#66FF00','#77FF00','#88FF00','#99FF00',
                '#AAFF00','#BBFF00','#CCFF00','#DDFF00','#EEFF00','#FFFF00','#FFEE00','#FFDD00','#FFCC00','#FFAA00','#FF9900','#FF8800',
                '#FF7700','#FF6600','#FF5500','#FF4400','#FF3300','#FF2200','#FF1100','#FF0000']

cut_off_v_pu_hardcoded = 0.95 # cut_off_v_pu is hardcoded

generate_gradient_scale_line_loading(green_to_red)
generate_gradient_scale_vlevel_undervoltage(green_to_red,cut_off_v_pu_hardcoded) # cut_off_v_pu is hardcoded




## Global variables used in callbacks
loading_values = Pandanet.res_line.loading_percent.values
vlevels_pu = Pandanet.res_bus.vm_pu.values

lines_to_activate = []  
lines_to_deactivate = []

### application time
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX]) 

app.layout = html.Div([

        dbc.Row( dbc.Col (html.H3('Visualization of Power Flow Results'), width= {'size': 6 ,'offset': 4},)
        ),
        
        dbc.Row([
            
                dbc.Col([
                        cyto.Cytoscape(
                            id='net map',
                            autolock = True,
                            autounselectify = False,
                            minZoom = 0.07,
                            maxZoom = 100,
                            layout={'name': 'preset'},
                            style={'width': '100%', 'height': '500px'},
                            stylesheet = generate_stylesheet(6,0.5,green_to_red),
                            elements=generate_nodes(Pandanet,vlevel = False,colorgradient=green_to_red) + generate_edges(Pandanet,Loading = False,colorgradient=green_to_red)
                            ),

                        html.Img(src='assets/linegradient.png'),
                        html.Img(src='assets/undervoltagegradient.png'),
                        ],
                    width = {'size':8, 'offset': 0, 'order': 1 }
                        ),

                
                dbc.Col([
                        html.P('Display loading percentage of lines:'),
                        
                        dcc.RadioItems(
                                    id = 'displayloading',
                                    options = ['Yes', 'No'],
                                    value = 'No'
                                    ),             
                        
                        html.P('Display voltage level of busses:'),
                        
                        dcc.RadioItems(
                                    id = 'buslevel',
                                    options = ['Yes', 'No'],
                                    value = 'No',
                        ),
                                
                        dcc.Slider(1,50,
                                    step =2,
                                    value=25,
                                    id = 'bus-size-slider',
                        ),
                                
                        dcc.Slider(1,10,
                                    step =1,
                                    value=6,
                                    id = 'line-size-slider',
                        ),
                        
                        html.P(id='hover-info-node'),
                        
                        html.P(id='hover-info-line'),

                        html.P(id='select-line'),

                        html.Button(id="activate", children="Activate"),
                        html.Button(id="deactivate", children="Deactivate"),
                        html.Button(id="clear", children="Clear"),

                        html.P('activate lines : '),
                        html.P(id='activate lines'),
                        

                        html.P('deactivate lines : '),
                        html.P(id='deactivate lines'),


                        html.P('Rerun Powerflow : '),
                        html.Button(id="commit", children="Commit Changes"),
                        html.P(id='running'),

                        ]
                        ,width= {'size':4, 'offset': 0, 'order': 2 })
        ]),
    ])


@app.callback( # callback naar elements (loading en vlevel)
    Output(component_id='net map',component_property= 'elements'),
    Output('running','children'),
    Input(component_id='displayloading', component_property='value'),
    Input(component_id='buslevel', component_property='value'),
    Input('commit', 'n_clicks')
    )
def map_style(radio_value_loading, radio_value_buscolor,n_clicks):
    
    if "commit" == ctx.triggered_id: 
        global lines_to_activate
        global lines_to_deactivate
        global Pandanet
        for line in lines_to_activate:
            switch_index = int(Pandanet.switch[Pandanet.switch.element == line].index[0]) # Return switch_index for a given line
            Pandanet.switch.closed[switch_index]=True
        for line in lines_to_deactivate:
            switch_index = int(Pandanet.switch[Pandanet.switch.element == line].index[0])
            Pandanet.switch.closed[switch_index]=False
        pp.runpp(Pandanet)
        global loading_values
        global vlevels_pu
        loading_values = Pandanet.res_line.loading_percent.values
        vlevels_pu = Pandanet.res_bus.vm_pu.values
        lines_to_activate = []
        lines_to_deactivate = []
        rerun_status = "powerflow recalculated"
    else:   
        rerun_status = """"""

    if radio_value_loading =='Yes' and radio_value_buscolor=="Yes":
        return generate_nodes(Pandanet,vlevel = True,colorgradient=green_to_red) + generate_edges(Pandanet,Loading = True,colorgradient=green_to_red),rerun_status
    elif radio_value_loading =='Yes' and radio_value_buscolor=="No":
        return generate_nodes(Pandanet,vlevel = False,colorgradient=green_to_red) + generate_edges(Pandanet,Loading = True,colorgradient=green_to_red),rerun_status
    elif radio_value_loading =='No' and radio_value_buscolor=="Yes":
        return generate_nodes(Pandanet,vlevel = True,colorgradient=green_to_red) + generate_edges(Pandanet,Loading = False,colorgradient=green_to_red),rerun_status
    else:
        return generate_nodes(Pandanet,vlevel = False,colorgradient=green_to_red) + generate_edges(Pandanet,Loading = False,colorgradient=green_to_red),rerun_status

@app.callback( #callback naar stylesheet (grote van elementen)
    Output(component_id='net map',component_property= 'stylesheet'),
    Input(component_id='bus-size-slider', component_property='value'),
    Input(component_id='line-size-slider', component_property='value')
    )
def bus_sizer(bus, line):
    return generate_stylesheet(bus, line,green_to_red)

@app.callback(
            Output('hover-info-node','children'),
            Input('net map', 'mouseoverNodeData'))
def displayHoverNodeData(data):
    if data:
        bus_index_str = data['id']
        bus_index = int(bus_index_str)
        vlevel = round(vlevels_pu[bus_index],3)
        return "Bus " + bus_index_str  + " - vm_pu: :" + str(vlevel)

@app.callback(
    Output('hover-info-line','children'),
    Input('net map', 'mouseoverEdgeData')
    )
def displayHoverEdgeData(data):
    if data:
        line_index_str = data['label']
        line_index = int(line_index_str)
        loading = round(loading_values[line_index],1)
        return "line " + line_index_str  + " - Loading: :" + str(loading) + "%"

@app.callback(
    Output('select-line','children'),
    Input('net map', 'tapEdgeData')
    )
def displayTapEdgeData(data):
    if data:
        line_index_str = data['label']
        line_index = int(line_index_str)
        open_lines = Pandanet.switch[Pandanet.switch.closed == False].element.values.tolist() ### Pandanet is hardcoded here
        lines_no_switch =  [x for x in Pandanet.line.index if x not in Pandanet.switch.element.values]
        if line_index in open_lines:
            line_status = 'Inactive'
        elif line_index in lines_no_switch: 
            line_status = 'Active, No Switch'
        else:
            line_status = 'Active'
        return 'line selected: '+ line_index_str + ', Status: ' + line_status 
    else:
        return 'no line is selected'



@app.callback(
    Output('activate lines','children'),
    Input('activate', 'n_clicks'),
    Input('net map', 'tapEdgeData'),
    Input('clear', 'n_clicks')
    )
def add_to_activate_lines(n_clicks1,line_data,n_clicks2):
    global lines_to_activate
    if "clear" == ctx.triggered_id:
        lines_to_activate = []
    elif line_data:
        line_index_str = line_data['label']
        line_index = int(line_index_str)
        open_lines = Pandanet.switch[Pandanet.switch.closed == False].element.values.tolist()       
        if line_index in open_lines:
            if  "activate" == ctx.triggered_id:
                if line_index not in lines_to_activate:
                    lines_to_activate.append(line_index)
    return str(lines_to_activate)


@app.callback(
    Output('deactivate lines','children'),
    Input('deactivate', 'n_clicks'),
    Input('net map', 'tapEdgeData'),
    Input('clear', 'n_clicks')
    )
def add_to_deactivate_lines(n_clicks1,line_data,n_clicks2):
    global lines_to_deactivate
    if "clear" == ctx.triggered_id:
        lines_to_deactivate = []
    elif line_data:
        line_index_str = line_data['label']
        line_index = int(line_index_str)
        closed_lines = Pandanet.switch[Pandanet.switch.closed == True].element.values.tolist()
        if line_index in closed_lines:
            if  "deactivate" == ctx.triggered_id:
                if line_index not in lines_to_deactivate:
                    lines_to_deactivate.append(line_index)   
    return str(lines_to_deactivate) 

app.run_server(debug=True)