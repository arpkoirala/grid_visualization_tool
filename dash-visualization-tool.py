from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px

import plotly.graph_objects as go
import networkx as nx
import dash_cytoscape as cyto



import pandas as pd
import pandapower as pp
import pandapower.plotting as pplt
import pandapower.topology as top
import networkx as nx
import plotly as plot
import pandapower.plotting.plotly as pplotly

import plotly.graph_objects as go
import numpy as np
from pandapower.plotting.plotly import get_plotly_color_palette
from create_net import createLVnet, createMVnet

from numpy import floor



##### creating LV net #####
pathLV = 'data/spanish_LV_net/'

bus_df = pd.read_excel(pathLV+'bus_df.xlsx')
bus_df= bus_df.drop(columns={'Unnamed: 0'})

ext_grid_df = pd.read_excel(pathLV+'ext_grid_df.xlsx')

line_df = pd.read_excel(pathLV+'line_df.xlsx')
line_df = line_df.drop(columns={'Unnamed: 0'})


load_per_bus_df = pd.read_excel(pathLV+'load_per_bus_df.xlsx')

netLV = createLVnet(bus_df, line_df, ext_grid_df, load_per_bus_df)
pp.runpp(netLV)

loading_values = netLV.res_line.loading_percent.values
vlevels_pu = netLV.res_bus.vm_pu.values

## DASHH

# function to help generate the elements 
green_to_red = ['#00FF00','#11FF00','#22FF00','#33FF00','#44FF00','#55FF00','#66FF00','#77FF00','#88FF00','#99FF00',
                '#AAFF00','#BBFF00','#CCFF00','#DDFF00','#EEFF00','#FFFF00','#FFEE00','#FFDD00','#FFCC00','#FFAA00','#FF9900','#FF8800',
                '#FF7700','#FF6600','#FF5500','#FF4400','#FF3300','#FF2200','#FF1100','#FF0000']


def generate_nodes(pandanet,vlevel,colorgradient):
    maxgran = len(colorgradient)
    all_nodes =[]
    ext_grid = pandanet.ext_grid.bus.values
    gran = 6
    if vlevel:
        vlevels = pandanet.res_bus.vm_pu.values
        diff = (1-vlevels)/0.05*gran
        classis = floor(diff)
        colorindex = classis*maxgran/gran
        colorindex = colorindex.astype(int)
        for node in pandanet.bus.index:
            x_coord = int(pandanet.bus_geodata.x[node]*10) # !!! COORDINATES ARE x 10, 
            y_coord = int(pandanet.bus_geodata.y[node]*10) 
            if node in ext_grid:
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': 'ext_grid'})
            elif colorindex[node] < maxgran:
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': colorgradient[colorindex[node]][1:]})  
            else:
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord},'classes': colorgradient[maxgran -1][1:]})
    else:
        for node in pandanet.bus.index:
            x_coord = int(pandanet.bus_geodata.x[node]*10)
            y_coord = int(pandanet.bus_geodata.y[node]*10)
            if node in ext_grid:
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': 'ext_grid'})
            else:
                all_nodes.append({'data':{'id': str(node)}, 'position': {'x': x_coord, 'y': -y_coord}, 'classes': 'buswhite'})
    return all_nodes

def generate_edges(pandanet,Loading,colorgradient):

    # closed_lines = netLV.switch[netLV.switch.closed == True].element.values.tolist()
    open_lines = netLV.switch[netLV.switch.closed == False].element.values.tolist()
    # lines_no_switch =  [x for x in netLV.line.index if x not in netLV.switch.element.values]
    # closed_lines.append(lines_no_switch)

    all_edges =[]
    if Loading:

        loading_levels = pandanet.res_bus.vm_pu.values
        colorindex = floor(loading_levels*len(colorgradient)/100)
        colorindex = colorindex.astype(int)

        for edge in pandanet.line.index:
            edge_class=''
            if edge in open_lines:
                edge_class='open-switch'
            elif pandanet.res_line.loading_percent[edge] > 100:
                edge_class='line-overloaded'
            else:
                edge_class=colorgradient[colorindex[edge]][1:] + 'line'
            all_edges.append({'data': {'label': str(edge), 'source': str(pandanet.line.from_bus[edge]), 'target': str(pandanet.line.to_bus[edge])},'selectable': True,'classes': edge_class})
        return all_edges
    else:
        for edge in pandanet.line.index:
            if edge in open_lines:
                all_edges.append({'data': {'label': str(edge),'source': str(pandanet.line.from_bus[edge]), 'target': str(pandanet.line.to_bus[edge])},'selectable': True,'classes': 'open-switch'})
            else:
                all_edges.append({'data': {'label': str(edge),'source': str(pandanet.line.from_bus[edge]), 'target': str(pandanet.line.to_bus[edge])},'selectable': True,'classes': 'line-black'})
        return all_edges


def generate_stylesheet(bus_size,line_size):
    all_styles = [{
                    'selector': '.ext_grid',
                    'style': {
                        'background-color': 'yellow',
                        'shape': 'diamond',
                        'height': bus_size,
                        'width' : bus_size,
                        'border-width': bus_size*0.1,
                        'border-color': 'black',
                        }
                },
                {
                    'selector': '.line-overloaded',
                    'style':{
                        'line-color': 'red',
                        'width': line_size*2}
                },
                {
                    'selector': '.line-loaded-50-100',
                    'style':{
                        'line-color': 'orange',
                        'width': line_size*1.5}
                },
                {
                    'selector': '.line-loaded-0-50',
                    'style':{
                        'line-color': 'green',
                        'width': line_size}
                },
                {
                    'selector': '.line-black',
                    'style':{
                        'line-color': 'black',
                        'width': line_size}
                },
                {
                    'selector': '.open-switch',
                    'style':{
                        'line-color': 'purple',
                        'line-style': 'dotted',
                        'width': line_size}
                },
                {
                    'selector': '.buswhite',
                    'style': {
                        'background-color': '#98DEDE',
                        'width' : bus_size,
                        'height' : bus_size,
                        'border-width': bus_size*0.1,
                        'border-color': 'black',}
                },
                {
                    'selector': ':selected',
                    'style': {
                        'line-color': 'blue',
                        'width': 3*line_size,}
                },
                ]
    for hexcode in green_to_red:
        all_styles.append({
                    'selector': '.' + hexcode[1:],
                    'style': {
                        'background-color': hexcode,
                        'width' : bus_size,
                        'height' : bus_size,
                        'border-width': bus_size*0.1,
                        'border-color': 'black',
                        }
                },)
    for hexcode in green_to_red:
        all_styles.append({
                    'selector': '.' + hexcode[1:] + 'line',
                    'style': {
                        'line-color': hexcode,
                        'width': line_size}
                },)

    return all_styles

### application time
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX]) 

app.layout = html.Div([

        dbc.Row( dbc.Col (html.H3('Visualization of Power Flow Results'), width= {'size': 6 ,'offset': 4},)
        ),
        
        dbc.Row([
            
                dbc.Col(
                    cyto.Cytoscape(
                            id='net map',
                            autolock = True,
                            autounselectify = False,
                            minZoom = 0.01,
                            maxZoom = 100,
                            layout={'name': 'preset'},
                            style={'width': '100%', 'height': '500px'},
                            stylesheet = generate_stylesheet(6,0.5),
                            elements=generate_nodes(netLV,vlevel = False,colorgradient=green_to_red) + generate_edges(netLV,Loading = False,colorgradient=green_to_red))
                        ,width = {'size':8, 'offset': 0, 'order': 1 }
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

                        ]
                        ,width= {'size':4, 'offset': 0, 'order': 2 })
        ]),
            
        

    ])


@app.callback( # callback naar elements (loading en vlevel)
    Output(component_id='net map',component_property= 'elements'),
    Input(component_id='displayloading', component_property='value'),
    Input(component_id='buslevel', component_property='value')
    )
def map_style(radio_value_loading, radio_value_buscolor):
    if radio_value_loading =='Yes' and radio_value_buscolor=="Yes":
        return generate_nodes(netLV,vlevel = True,colorgradient=green_to_red) + generate_edges(netLV,Loading = True,colorgradient=green_to_red)
    elif radio_value_loading =='Yes' and radio_value_buscolor=="No":
        return generate_nodes(netLV,vlevel = False,colorgradient=green_to_red) + generate_edges(netLV,Loading = True,colorgradient=green_to_red)
    elif radio_value_loading =='No' and radio_value_buscolor=="Yes":
        return generate_nodes(netLV,vlevel = True,colorgradient=green_to_red) + generate_edges(netLV,Loading = False,colorgradient=green_to_red)
    else:
        return generate_nodes(netLV,vlevel = False,colorgradient=green_to_red) + generate_edges(netLV,Loading = False,colorgradient=green_to_red)

@app.callback( #callback naar stylesheet (grote van elementen)
    Output(component_id='net map',component_property= 'stylesheet'),
    Input(component_id='bus-size-slider', component_property='value'),
    Input(component_id='line-size-slider', component_property='value')
    )
def bus_sizer(bus, line):
    return generate_stylesheet(bus, line)

@app.callback(
            Output('hover-info-node','children'),
            Input('net map', 'mouseoverNodeData'))
def displayTapNodeData(data):
    if data:
        bus_index_str = data['id']
        bus_index = int(bus_index_str)
        vlevel = round(vlevels_pu[bus_index],3)
        return "Bus " + bus_index_str  + " - vm_pu: :" + str(vlevel)

@app.callback(
    Output('hover-info-line','children'),
    Input('net map', 'mouseoverEdgeData')
    )
def displayTapEdgeData(data):
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
        return 'line selected: '+ line_index_str

app.run_server(debug=True)