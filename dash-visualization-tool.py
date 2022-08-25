from dash import Dash, html, dcc, Output, Input, ctx
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

import pandas as pd
import pandapower as pp

from create_net import createLVnet, createMVnet # auxilary functions to generate 2 specific networks


from generate_stylesheet import generate_stylesheet, generate_gradient_scale_line_loading, generate_gradient_scale_vlevel_undervoltage, generate_gradient_scale_vlevel_overvoltage 
from generate_cytoscape_elements import generate_nodes, generate_edges, is_radial
# auxilary function are explained in their respective files



##### creating LV and MV net #####
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


#########


green_to_red = ['#00FF00','#11FF00','#22FF00','#33FF00','#44FF00','#55FF00','#66FF00','#77FF00','#88FF00','#99FF00', # Colorgradients have to be a list, with colors represented by hexcode-strings
                '#AAFF00','#BBFF00','#CCFF00','#DDFF00','#EEFF00','#FFFF00','#FFEE00','#FFDD00','#FFCC00','#FFAA00','#FF9900','#FF8800',
                '#FF7700','#FF6600','#FF5500','#FF4400','#FF3300','#FF2200','#FF1100','#FF0000']
green_to_blue = ['#00FF00','#00FF11','#00FF22','#00FF33','#00FF44','#00FF55','#00FF66','#00FF77','#00FF88','#00FF99',
                '#00FFAA','#00FFBB','#00FFCC','#00FFDD','#00FFEE','#00FFFF','#00EEFF','#00DDFF','#00CCFF','#00AAFF','#0099FF','#0088FF',
                '#0077FF','#0066FF','#0055FF','#0044FF','#0033FF','#0022FF','#0011FF','#0000FF']

cut_off_v_pu_hardcoded_undervoltage = 0.90 # cut_off_v_pu is hardcoded; below(or above) the cutt of voltage all nodes will have the same color
cut_off_v_pu_hardcoded_overvoltage = 1.10

##############################################################
Pandanet = netLV  # Change here to the network you want to use
##############################################################

pp.runpp(Pandanet) # run powerflow on the network

generate_gradient_scale_line_loading(green_to_red) #auxilary function to generate an image containing a legend for the colors used to represent the power flow results
generate_gradient_scale_vlevel_undervoltage(green_to_red,cut_off_v_pu_hardcoded_undervoltage) # cut_off_v_pu is hardcoded, also in generate nodes
generate_gradient_scale_vlevel_overvoltage(green_to_blue,cut_off_v_pu_hardcoded_overvoltage)



## Global variables, these have to be global because they are changed during certain callbacks, but later on used in other callbacks
loading_values = Pandanet.res_line.loading_percent.values 
vlevels_pu = Pandanet.res_bus.vm_pu.values
lines_to_activate = [] 
lines_to_deactivate = []


## Dash Application ##

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP]) # An dbc-stylesheet has to be used, otherwise the dbc-layout commands will not work

app.layout = dbc.Container([
    # Container, Row and Col commands are used for structuring the layout

        dbc.Row( dbc.Col (html.H3('Visualization of Power-Flow Calculation Results', className='text-center my-1 mp-1'))),
        
        dbc.Row([
            
                dbc.Col([
                        cyto.Cytoscape(
                            id='net map', # id are used to refer to components
                            autolock = True, # locks the nodes in place; nodes cannot be moved by user when this is True
                            # autounselectify = False,
                            minZoom = 0.02,
                            maxZoom = 100,
                            layout={'name': 'preset'},
                            style={'width': '100%', 'height': '500px'},
                            stylesheet = generate_stylesheet(6,0.5,green_to_red,green_to_blue), # defines all the node and edge styles that can be used in the network; generated by auxilary function
                            elements=generate_nodes(Pandanet,vlevel = False,colorgradient1=green_to_red,colorgradient2=green_to_blue,v_cuttoff_under=cut_off_v_pu_hardcoded_undervoltage,v_cuttoff_over=cut_off_v_pu_hardcoded_overvoltage,labels = False) + generate_edges(Pandanet,Loading = False,colorgradient=green_to_red)
                            ), # create all the nodes and edges on the map; also done by auxilary fucntion

                        
                        ], 
                        className="border border-secondary",    
                        width = {'size':9, 'offset': 0, 'order': 1 }
                        ),

                        
                dbc.Col([                               
                                
                        html.P(id='hover-info-node', children = ""), # children contains what will be displayed in the application, it is also the component that is changed in the callbacks
                                
                        html.P(id='hover-info-line', children = ""),

                        html.P(id='select-line', children = ""),

                        html.Button(id="activate", children="Activate"), # children contains the text that is displayed on top of the buttons
                        html.Button(id="deactivate", children="Deactivate"), # Functionality of buttons is explained in their respective callbacks
                        html.Button(id="clear", children="Clear"),

                        html.P('activate lines : '),
                        html.P(id='activate lines',children=""),
                                

                        html.P('deactivate lines : '),
                        html.P(id='deactivate lines',children=""),


                        html.P('Rerun Powerflow : '),
                        html.Button(id="commit", children="Commit Changes"),
                        html.P(id='running',children=""),

                        html.P(id='radiality',children="Radial and Connected: " + str(is_radial(Pandanet))),


                        

                        ]
                    
                    ,className="border border-secondary", width= {'size':3, 'offset': 0, 'order': 2 })
                ]),
        dbc.Row([
            
                dbc.Col([
                        html.Img(src='assets/linegradient.png'), # display the legends for colors used to represent the power flow results
                        html.Img(src='assets/undervoltagegradient.png'),
                        html.Img(src='assets/overvoltagegradient.png'),
                        ],className="border border-secondary", width= {'size':7, 'offset': 0, 'order': 1 }
                        ),
                
                dbc.Col([
                        dbc.Row([
                            
                            dbc.Col([html.P('Display loading percentage of lines:'),]),
                            
                            dbc.Col([dcc.RadioItems( # Radioitems: User can choose between 2 values/options
                                        id = 'displayloading',
                                        options = ['Yes', 'No'],
                                        value = 'No'
                                        ),
                                ])
                            ]),
                        
                        dbc.Row([
                            dbc.Col([html.P('Display voltage level of busses:',className='mp-0'),]),
                            
                            dbc.Col([dcc.RadioItems(
                                    id = 'buslevel',
                                    options = ['Yes', 'No'],
                                    value = 'No',
                                    className='mp-2'),
                                ]),
                            dbc.Col([html.P('Display bus labels:',className='mp-0'),]),
                            
                            dbc.Col([dcc.RadioItems(
                                    id = 'buslabel',
                                    options = ['Yes', 'No'],
                                    value = 'No',
                                    className='mp-2'),
                                ])
                            ]),
                        
                        dbc.Row([
                            dbc.Col([html.P('Node size: '),
                                    
                                    dcc.Slider(1, 50, # sliders to alter the size of the nodes and the lines
                                            step =2,
                                            value=3,
                                            id = 'bus-size-slider',),

                                    html.P('line width: '),                
                                    
                                    dcc.Slider(1,10,
                                            step =1,
                                            value=1,
                                            id = 'line-size-slider',),
                                ])
                            ]),
                    
                        ], className="border border-secondary", width= {'size':5, 'offset': 0, 'order': 2 }),
                ]),

    ], fluid=True)


@app.callback( 
    # This is the callback that handles everything that changes the elements part of the network:
    # - It turns on and off the colorscaling of the nodes and lines
    # - It closes and opens switches when the commit-changes button is pressed, 
    #   the powerflow calculations are also preformed again when this is done
    Output(component_id='net map',component_property= 'elements'),
    Output(component_id='running',component_property='children'),
    Output(component_id='radiality',component_property='children'),
    Input(component_id='displayloading', component_property='value'),
    Input(component_id='buslevel', component_property='value'),
    Input(component_id='commit',component_property= 'n_clicks'),
    Input(component_id='buslabel', component_property='value'),
    )
def map_style(radio_value_loading, radio_value_buscolor,n_clicks,labelsitem):
    
    if labelsitem == 'Yes': # Turns on or off the labels displayed next to the nodes
        labelboolean = True
    else:
        labelboolean = False
    
    if "commit" == ctx.triggered_id: # when the commit button is pressed, the switches are opened and closed
        global lines_to_activate
        global lines_to_deactivate
        global Pandanet
        for line in lines_to_activate:
            switch_index = int(Pandanet.switch[Pandanet.switch.element == line].index[0]) # Return switch_index for a given line
            Pandanet.switch.closed[switch_index]=True
        for line in lines_to_deactivate:
            switch_index = int(Pandanet.switch[Pandanet.switch.element == line].index[0])
            Pandanet.switch.closed[switch_index]=False
        pp.runpp(Pandanet) # The power flow calculations are preformed again
        global loading_values # the global parameters are changed according to the new power flow results
        global vlevels_pu
        loading_values = Pandanet.res_line.loading_percent.values
        vlevels_pu = Pandanet.res_bus.vm_pu.values
        lines_to_activate = []
        lines_to_deactivate = []
        rerun_status = "powerflow recalculated"
    
    else:   
        rerun_status = ""

    if radio_value_loading =='Yes' and radio_value_buscolor=="Yes":  # colorscaling for vlevels and loading levels is turned on according to the values of the RadioItems
        return generate_nodes(Pandanet,vlevel = True,colorgradient1=green_to_red,colorgradient2=green_to_blue,v_cuttoff_under=cut_off_v_pu_hardcoded_undervoltage,v_cuttoff_over=cut_off_v_pu_hardcoded_overvoltage,labels = labelboolean) + generate_edges(Pandanet,Loading = True,colorgradient=green_to_red),rerun_status,"Radial and Connected: " + str(is_radial(Pandanet))
    elif radio_value_loading =='Yes' and radio_value_buscolor=="No":
        return generate_nodes(Pandanet,vlevel = False,colorgradient1=green_to_red,colorgradient2=green_to_blue,v_cuttoff_under=cut_off_v_pu_hardcoded_undervoltage,v_cuttoff_over=cut_off_v_pu_hardcoded_overvoltage,labels = labelboolean) + generate_edges(Pandanet,Loading = True,colorgradient=green_to_red),rerun_status,"Radial and Connected: " + str(is_radial(Pandanet))
    elif radio_value_loading =='No' and radio_value_buscolor=="Yes":
        return generate_nodes(Pandanet,vlevel = True,colorgradient1=green_to_red,colorgradient2=green_to_blue,v_cuttoff_under=cut_off_v_pu_hardcoded_undervoltage,v_cuttoff_over=cut_off_v_pu_hardcoded_overvoltage,labels = labelboolean) + generate_edges(Pandanet,Loading = False,colorgradient=green_to_red),rerun_status,"Radial and Connected: " + str(is_radial(Pandanet))
    else:
        return generate_nodes(Pandanet,vlevel = False,colorgradient1=green_to_red,colorgradient2=green_to_blue,v_cuttoff_under=cut_off_v_pu_hardcoded_undervoltage,v_cuttoff_over=cut_off_v_pu_hardcoded_overvoltage,labels = labelboolean) + generate_edges(Pandanet,Loading = False,colorgradient=green_to_red),rerun_status,"Radial and Connected: " + str(is_radial(Pandanet))

@app.callback( 
    # Changes the size of the nodes and edges, when the sliders are changed
    # Only the stylesheet of the network-map has to be changed to realise this, not the elements themselves
    Output(component_id='net map',component_property= 'stylesheet'),
    Input(component_id='bus-size-slider', component_property='value'),
    Input(component_id='line-size-slider', component_property='value')
    )
def bus_sizer(bus, line):
    return generate_stylesheet(bus_size=bus, line_size=line, colorgradient1= green_to_red,colorgradient2 =green_to_blue) # Stylesheet is generated again, with new values for bus and line size

@app.callback( 
    # displays info when hovering over a node, info stays displayed until user hovers over another node
            Output('hover-info-node','children'),
            Input('net map', 'mouseoverNodeData'))
def displayHoverNodeData(data):
    if data:
        bus_index_str = data['id']
        bus_index = int(bus_index_str)
        vlevel = round(vlevels_pu[bus_index],3) # uses global variable vlevel to acces the voltage level of a node
        return "Bus " + bus_index_str  + " - vm_pu: :" + str(vlevel)

@app.callback( 
    # displays info when hovering over a line, info stays displayed until user hovers over another line
    Output(component_id='hover-info-line',component_property='children'),
    Input(component_id='net map',component_property= 'mouseoverEdgeData')
    )
def displayHoverEdgeData(data):
    if data:
        line_index_str = data['label']
        line_index = int(line_index_str)
        loading = round(loading_values[line_index],1) # uses global variable loading values to acces the loading percentage of a line
        return "line " + line_index_str  + " - Loading: :" + str(loading) + "%"

@app.callback( 
    # displays info when a line is selected
    Output('select-line','children'),
    Input('net map', 'tapEdgeData')
    )
def displayTapEdgeData(data):
    if data:
        line_index_str = data['label']
        line_index = int(line_index_str)
        open_lines = Pandanet.switch[Pandanet.switch.closed == False].element.values.tolist() 
        lines_no_switch =  [x for x in Pandanet.line.index if x not in Pandanet.switch.element.values]
        if line_index in open_lines:
            line_status = 'Inactive'
        elif line_index in lines_no_switch: 
            line_status = 'Active, No Switch'
        else: # The remaining lines are the closed/active lines
            line_status = 'Active'
        return 'line selected: '+ line_index_str + ', Status: ' + line_status 
    else:
        return 'no line is selected'



@app.callback( 
    # this callback will add a line to a (global) list called 'lines_to_activate', when the line is selected and the activate button is pressed. The line will only be added to this list, and will not yet be activated
    Output('activate lines','children'),
    Input('activate', 'n_clicks'),
    Input('net map', 'tapEdgeData'),
    Input('clear', 'n_clicks')
    )
def add_to_activate_lines(n_clicks1,line_data,n_clicks2):
    global lines_to_activate
    if "clear" == ctx.triggered_id: # detects when the clear button is pressed. When the clear button is pressed, the list 'lines_to_activate' is cleared
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
    # this callback will add a line to a (global) list called 'lines_to_deactivate', when the line is selected and the deactivate button is pressed. The line will only be added to this list, and will not yet be deactivated
    Output('deactivate lines','children'),
    Input('deactivate', 'n_clicks'),
    Input('net map', 'tapEdgeData'),
    Input('clear', 'n_clicks')
    )
def add_to_deactivate_lines(n_clicks1,line_data,n_clicks2):
    global lines_to_deactivate
    if "clear" == ctx.triggered_id: # detects when the clear button is pressed. When the clear button is pressed, the list 'lines_to_deactivate' is cleared
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

app.run_server(debug=True) # Turn on debug for error messages on the webpage