import numpy as np

def map_array(input_array, output_range):
    """ Map an array of values to a desired range """
    
    # numpify
    if not isinstance(input_array, np.ndarray): 
        input_array = np.array(input_array)
        
    # get ranges
    input_min, input_max = np.min(input_array), np.max(input_array)
    output_min, output_max = output_range
    
    return (output_max - output_min) * (input_array - input_min)/(input_max - input_min) + output_min

def resize_array(input_array, output_size=10):
    """ 
    Rescale an array to be within a set size (range). If origin within the range of array,
    preserve sign relationships. Otherwise map to (0,size)
    """
    
    # numpify
    if not isinstance(input_array, np.ndarray):
        input_array = np.array(input_array)

    input_min, input_max = input_array.min(), input_array.max()
    input_size = input_max - input_min

    if 0 >= input_min and 0 <= input_max:

        output_min = input_min/input_size*output_size
        output_max = input_max/input_size*output_size
        return map_array(input_array, (output_min, output_max))

    else:
        return map_array(input_array, (0, output_size))

def rescale_xyz(x,y,z, scale=10):
    
    xrange = max(x)-min(x)
    yrange = max(y)-min(y)
    zrange = max(z)-min(z)

    xr = resize_array(x, output_size=scale)
    yr = resize_array(y, output_size=scale*yrange/xrange)
    zr = resize_array(z, output_size=scale*zrange/xrange)
    
    return xr, yr, zr