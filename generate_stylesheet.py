import matplotlib.pyplot
import numpy as np


def generate_stylesheet(bus_size,line_size,colorgradient,colorgradient2):
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
                        'line-color': 'grey',
                        'line-style': 'dotted',
                        'width': line_size}
                },
                {
                    'selector': '.line-nan',
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
                    'selector': '.buswhite',
                    'style': {
                        'background-color': '#98DEDE',
                        'width' : bus_size,
                        'height' : bus_size,
                        'border-width': bus_size*0.1,
                        'border-color': 'black',}
                },
                
                ]
    for hexcode in colorgradient:
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
    for hexcode in colorgradient2:
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
    for hexcode in colorgradient:
        all_styles.append({
                    'selector': '.' + hexcode[1:] + 'line',
                    'style': {
                        'line-color': hexcode,
                        'width': line_size}
                },)
    
    all_styles.append({
                    'selector': ':selected',
                    'style': {
                        'line-color': 'blue',
                        'width': 2*line_size,}
                },)
    return all_styles

def generate_gradient_scale_line_loading(colorgradient):
    fig, ax = matplotlib.pyplot.subplots(figsize=(10,0.3))
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    matplotlib.pyplot.xlabel('loading percentage of line')
    for x in range(0,100):
        if x == 0:
            ax.axvline(x, color='black', linewidth=10)
        else:
            color_index=int(np.floor(x/100*len(colorgradient)))
            ax.axvline(x, color=colorgradient[color_index], linewidth=100)
    matplotlib.pyplot.savefig('assets/linegradient.png',bbox_inches='tight')
    return 

def generate_gradient_scale_vlevel_undervoltage(colorgradient,cut_off_v_pu):
    x_start = 1
    x_end = cut_off_v_pu
    step_size = (x_start - x_end)/len(colorgradient)
    fig, ax = matplotlib.pyplot.subplots(figsize=(10,0.3))
    ax.set_xlim(x_start, x_end)
    ax.set_yticks([])
    matplotlib.pyplot.xlabel('Undervoltage of Busses [pu]')
    for x in np.arange(x_start, x_end, -step_size):
        diff = (1-x)/(x_start - x_end)*len(colorgradient)
        colorindex = np.floor(diff)
        colorindex = colorindex.astype(int)
        ax.axvline(x, color=colorgradient[colorindex], linewidth=100)
    matplotlib.pyplot.savefig('assets/undervoltagegradient.png',bbox_inches='tight')
    return

def generate_gradient_scale_vlevel_overvoltage(colorgradient,cut_off_v_pu):
    x_start = 1
    x_end = cut_off_v_pu
    step_size = (x_end - x_start)/len(colorgradient)
    fig, ax = matplotlib.pyplot.subplots(figsize=(10,0.3))
    ax.set_xlim(x_start, x_end)
    ax.set_yticks([])
    matplotlib.pyplot.xlabel('Overvoltage of Busses [pu]')
    for x in np.arange(x_start, x_end, step_size):
        diff = (x-1)/(x_end - x_start)*len(colorgradient)
        colorindex = np.floor(diff)
        colorindex = colorindex.astype(int)
        ax.axvline(x, color=colorgradient[colorindex], linewidth=100)
    matplotlib.pyplot.savefig('assets/overvoltagegradient.png',bbox_inches='tight')
    return