import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.cm import cool
def normalize(data,max,min):

    return (data-min)/(max-min)
def get_cmap_color_str(data,cmap):
    '''从正则后的颜色值，获取指定cmap中的颜色，并转化为echarts需要的“rgba(255,255,255,1)”形式'''
    c=cmap(data)
    colors=(c[0]*255,c[1]*255,c[2]*255,1)
    return(f'rgba{colors}')
cdict = {'red':   [[0.0,  91/255, 91/255],
                   [0.5,  200/255, 200/255],
                   [1.0,  255/255, 255/255]],
         'green': [[0.0,  218/255, 218/255],
                   [0.5, 200/255, 200/255],
                   [1, 94/255, 94/255]],

         'blue':  [[0.0,  146/255, 146/255],
                   [0.5,  121.5/255, 121.5/255],
                   [1.0,  97/255, 97/255]]}

cdict = {'red':   [[0.0,  121/255, 121/255],
                   
                   [1.0,  241/255, 241/255]],
         'green': [[0.0,  240/255, 240/255],
                   
                   [1, 70/255, 70/255]],

         'blue':  [[0.0,  120/255, 120/255],
                   
                   [1.0,  103/255, 103/255]]}

regrcmp = LinearSegmentedColormap('testCmap', segmentdata=cdict, N=256)
rgba = regrcmp(np.linspace(0, 1, 256))