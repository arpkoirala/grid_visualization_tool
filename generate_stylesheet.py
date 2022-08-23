import matplotlib.pyplot
import numpy as np

# generate_stylesheet generates a list which contains all the different stylesheets that can be used in the cytoscape network map.
# a style sheet contains a 'selector' and a 'style'.
# The style attributre contains all of the styling parameters like color, shape and size.
# The selector attribute is used to select a style when generating elements


def generate_stylesheet(bus_size,line_size,colorgradient1,colorgradient2): 
    all_styles = [{
                    'selector': '.ext_grid', #style for nodes connected to an external grid
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
                    'selector': '.line-black',
                    'style':{
                        'line-color': 'black',
                        'width': line_size}
                },
                {
                    'selector': '.open-switch', # style for line that are not active/ switched open
                    'style':{
                        'line-color': 'grey',
                        'line-style': 'dotted',
                        'width': line_size}
                },
                {
                    'selector': '.line-nan', # style when the powerflow calculations return a NaN value for a certain line or node
                    'style':{
                        'line-color': 'purple',
                        'width': line_size}
                },
                {
                    'selector': '.bus-nan',
                    'style': {
                        'background-color': 'purple',
                        'shape': 'star',
                        'height': bus_size,
                        'width' : bus_size,
                        'border-width': bus_size*0.1,
                        'border-color': 'black',
                        }
                },
                {
                    'selector': '.busstandard',
                    'style': {
                        'background-color': '#98DEDE',
                        'width' : bus_size,
                        'height' : bus_size,
                        'border-width': bus_size*0.1,
                        'border-color': 'black',}
                },
                {
                    'selector': '.line-overloaded',
                    'style': {
                        'line-color': '#FF0000',
                        'width': line_size}
                },
                
                ]
    for hexcode in colorgradient1: 
        # for loops are used to create 30 different styles, each with a color from the colorgradient used.
        # the colorgradients have to be discrete in order to be used with this application
        all_styles.append({         
                    'selector': '.' + hexcode[1:], 
                    'style': {
                        'background-color': hexcode,
                        'width' : bus_size,
                        'height' : bus_size,
                        'border-width': bus_size*0.1,
                        'border-color': 'black',
                        } # this is the colorgradient for undervoltages
                },)
    for hexcode in colorgradient2: 
        # this is the colorgradient for overvoltages
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
    for hexcode in colorgradient1: 
        # this is the colorgradients for line loading
        all_styles.append({
                    'selector': '.' + hexcode[1:] + 'line',
                    'style': {
                        'line-color': hexcode,
                        'width': line_size}
                },)
    
    all_styles.append({ 
        # highlights a line when it is selected
                    'selector': ':selected',
                    'style': {
                        'line-color': 'blue',
                        'width': 2*line_size,}
                },)
    return all_styles

def generate_gradient_scale_line_loading(colorgradient): 
    # plots a graph of vertical lines. 
    # The result is a colorgradient with the correct scale on the x-axis
    fig, ax = matplotlib.pyplot.subplots(figsize=(10,0.25))
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    matplotlib.pyplot.xlabel('loading percentage of line')
    for x in range(0,100):
        if x == 0:
            ax.axvline(x, color='black', linewidth=10)
        else:
            color_index=int(np.floor(x/100*len(colorgradient))) # transformation that projects the range of loading values (0-100) onto the amount of colors in the colorgradient
            ax.axvline(x, color=colorgradient[color_index], linewidth=100)
    matplotlib.pyplot.savefig('assets/linegradient.png',bbox_inches='tight') # the plot is saved as a png. It is later displayed using an html.IMG component
    return 

def generate_gradient_scale_vlevel_undervoltage(colorgradient,cut_off_v_pu): 
    # plots a graph of vertical lines. 
    # The result is a colorgradient with the correct scale on the x-axis
    x_start = 1
    x_end = cut_off_v_pu # cut_off_v_pu in hardcoded in the main file, but can easily be changed there.
    step_size = (x_start - x_end)/len(colorgradient)
    fig, ax = matplotlib.pyplot.subplots(figsize=(10,0.25))
    ax.set_xlim(x_start, x_end)
    ax.set_yticks([])
    matplotlib.pyplot.xlabel('Undervoltage of Bus [pu]')
    for x in np.arange(x_start, x_end, -step_size):
        diff = (1-x)/(x_start - x_end)*len(colorgradient) # transformation that projects the range of undervoltage (v_cuttoff - 1) onto the amount of colors in the colorgradient
        colorindex = np.floor(diff)
        colorindex = colorindex.astype(int)
        ax.axvline(x, color=colorgradient[colorindex], linewidth=100)
    matplotlib.pyplot.savefig('assets/undervoltagegradient.png',bbox_inches='tight') # the plot is saved as a png. It is later displayed using an html.IMG component
    return

def generate_gradient_scale_vlevel_overvoltage(colorgradient,cut_off_v_pu): 
    # plots a graph of vertical lines.
    # The result is a colorgradient with the correct scale on the x-axis
    x_start = 1
    x_end = cut_off_v_pu # cut_off_v_pu in hardcoded in the main file, but can easily be changed there.
    step_size = (x_end - x_start)/len(colorgradient)
    fig, ax = matplotlib.pyplot.subplots(figsize=(10,0.25))
    ax.set_xlim(x_start, x_end)
    ax.set_yticks([])
    matplotlib.pyplot.xlabel('Overvoltage of Bus [pu]')
    for x in np.arange(x_start, x_end, step_size):
        diff = (x-1)/(x_end - x_start)*len(colorgradient) # transformation that projects the range of undervoltage (v_cuttoff - 1) onto the amount of colors in the colorgradient
        colorindex = np.floor(diff)
        colorindex = colorindex.astype(int)
        ax.axvline(x, color=colorgradient[colorindex], linewidth=100)
    matplotlib.pyplot.savefig('assets/overvoltagegradient.png',bbox_inches='tight') # the plot is saved as a png. It is later displayed using an html.IMG component
    return