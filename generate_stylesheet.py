def generate_stylesheet(bus_size,line_size,colorgradient):
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