# PyGISS: Misc. Python library
# Copyright (c) 2013-2016 by Elizabeth Fischer
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import numpy.ma as ma
import giss.plot
from icebin import ibplotter
from giss import memoize,xaccess

# ====================================================================


# Definitions of specific grids used in ModelE
#
_lons_4x5 = np.array([-177.5, -172.5, -167.5, -162.5, -157.5, -152.5, -147.5, -142.5,
       -137.5, -132.5, -127.5, -122.5, -117.5, -112.5, -107.5, -102.5,
        -97.5,  -92.5,  -87.5,  -82.5,  -77.5,  -72.5,  -67.5,  -62.5,
        -57.5,  -52.5,  -47.5,  -42.5,  -37.5,  -32.5,  -27.5,  -22.5,
        -17.5,  -12.5,   -7.5,   -2.5,    2.5,    7.5,   12.5,   17.5,
         22.5,   27.5,   32.5,   37.5,   42.5,   47.5,   52.5,   57.5,
         62.5,   67.5,   72.5,   77.5,   82.5,   87.5,   92.5,   97.5,
        102.5,  107.5,  112.5,  117.5,  122.5,  127.5,  132.5,  137.5,
        142.5,  147.5,  152.5,  157.5,  162.5,  167.5,  172.5,  177.5])

_lats_4x5 = np.array([-90., -86., -82., -78., -74., -70., -66., -62., -58., -54., -50.,
       -46., -42., -38., -34., -30., -26., -22., -18., -14., -10.,  -6.,
        -2.,   2.,   6.,  10.,  14.,  18.,  22.,  26.,  30.,  34.,  38.,
        42.,  46.,  50.,  54.,  58.,  62.,  66.,  70.,  74.,  78.,  82.,
        86.,  90.])


_lons_2x2_5 = np.array([-178.75, -176.25, -173.75, -171.25, -168.75, -166.25, -163.75, 
    -161.25, -158.75, -156.25, -153.75, -151.25, -148.75, -146.25, -143.75, 
    -141.25, -138.75, -136.25, -133.75, -131.25, -128.75, -126.25, -123.75, 
    -121.25, -118.75, -116.25, -113.75, -111.25, -108.75, -106.25, -103.75, 
    -101.25, -98.75, -96.25, -93.75, -91.25, -88.75, -86.25, -83.75, -81.25, 
    -78.75, -76.25, -73.75, -71.25, -68.75, -66.25, -63.75, -61.25, -58.75, 
    -56.25, -53.75, -51.25, -48.75, -46.25, -43.75, -41.25, -38.75, -36.25, 
    -33.75, -31.25, -28.75, -26.25, -23.75, -21.25, -18.75, -16.25, -13.75, 
    -11.25, -8.75, -6.25, -3.75, -1.25, 1.25, 3.75, 6.25, 8.75, 11.25, 13.75, 
    16.25, 18.75, 21.25, 23.75, 26.25, 28.75, 31.25, 33.75, 36.25, 38.75, 
    41.25, 43.75, 46.25, 48.75, 51.25, 53.75, 56.25, 58.75, 61.25, 63.75, 
    66.25, 68.75, 71.25, 73.75, 76.25, 78.75, 81.25, 83.75, 86.25, 88.75, 
    91.25, 93.75, 96.25, 98.75, 101.25, 103.75, 106.25, 108.75, 111.25, 
    113.75, 116.25, 118.75, 121.25, 123.75, 126.25, 128.75, 131.25, 133.75, 
    136.25, 138.75, 141.25, 143.75, 146.25, 148.75, 151.25, 153.75, 156.25, 
    158.75, 161.25, 163.75, 166.25, 168.75, 171.25, 173.75, 176.25, 178.75])

_lats_2x2_5 = np.array([
    -90., -87., -85., -83., -81., -79., -77., -75., -73., -71., -69., -67., -65., -63., 
    -61., -59., -57., -55., -53., -51., -49., -47., -45., -43., -41., -39., -37., -35., 
    -33., -31., -29., -27., -25., -23., -21., -19., -17., -15., -13., -11., -9., -7., -5., 
    -3., -1., 1., 3., 5., 7., 9., 11., 13., 15., 17., 19., 21., 23., 25., 27., 29., 31., 33., 
    35., 37., 39., 41., 43., 45., 47., 49., 51., 53., 55., 57., 59., 61., 63., 65., 67., 69., 
    71., 73., 75., 77., 79., 81., 83., 85., 87., 90.])


by_name = {
    '4x5' : (_lons_4x5, _lats_4x5),
    '2x2.5' : (_lons_2x2_5, _lats_2x2_5)
}

_lon_lat_lookup = {
    (len(_lats_4x5), len(_lons_4x5)) : (_lons_4x5, _lats_4x5),
    (len(_lats_2x2_5), len(_lons_2x2_5)) : (_lons_2x2_5, _lats_2x2_5),

    (len(_lats_4x5) * len(_lons_4x5),) : (_lons_4x5, _lats_4x5),
    (len(_lats_2x2_5) * len(_lons_2x2_5),) : (_lons_2x2_5, _lats_2x2_5)
}


def get_byname(name) :
    lons, lats = by_name[name]
    return giss.plot.LonLatPlotter(lons, lats)

# Memoize so we can compare plotters by ID
@memoize.local()
def guess_plotter(shape) :
    """Guesses on a plotter to use, based on the dimension of a data
    array from ModelE output.
    Args:
        shape : Either
            (a) A Tuple of integers, representing the shape of an array
            (b) The np.array itself

    Returns (Plotter):
        A plotter appropriate to the data, and resolution of the model."""

    # Work just as well on shape tuple or np.array
    if not isinstance(shape, tuple) :
        shape = shape.shape

    # Infer the grid from the size of the input array
    lons, lats = _lon_lat_lookup[shape]
    return giss.plot.LonLatPlotter(lons, lats)

# ===========================================================
_zero_centered = {'impm', 'evap_lndice', 'evap', 'imph_lndice', 'impm_lndice', 'netht_lndice', 'trht_lndice'}#, 'sensht_lndice'} #, 'trht_lndice'}

_reverse_scale = {'impm', 'impm_lndice'}

# TODO: Make this _change_units instead, use a lambda function
# This way, we can do C <--> K conversion as well
#_rescale_factors = {'impm_lndice' : (86400., 'kg/day*m^2')}

#_change_units = {
#   'impm_lndice' : ('kg/day*m^2', lambda x : x * 86400.)
#}


def _default_plot_boundaries(basemap) :
    """Default function for 'plot_boundaries' output of plot_params()"""

    # ---------- Draw other stuff on the map
    # draw line around map projection limb.
    # color background of map projection region.
    # missing values over land will show up this color.
    basemap.drawmapboundary(fill_color='0.5')
    basemap.drawcoastlines()

    # draw parallels and meridians, but don't bother labelling them.
    basemap.drawparallels(np.arange(-90.,120.,30.))
    basemap.drawmeridians(np.arange(0.,420.,60.))

# ------------------------------------------------
# --- Support for io.py
# ----------------------------------------------------------
# Args: icebin_config, ice_sheet, IvE=None):
PlotterE = memoize.local()(ibplotter.PlotterE)
#guess_plotter = memoize.local()(guess_plotter)

def get_plotter(attrs, region=None):
    """Produces a plotter based on the meta-data that came with a variable.
    region:
        Parameter required if getting a local-area plotter"""

    grid = attrs[('fetch', 'grid')]
    if grid == 'atmosphere':
        plotter = modele.plotters.guess_plotter(attrs[('fetch', 'shape')])
    elif grid == 'elevation':
        correctA = attrs[('fetch', 'grid', 'correctA')]
        icebin_in = attrs[('param', '_file_icebin_in')]
        plotter = PlotterE(icebin_in, region)
    else:
        raise ValueError('Unknown grid type: %s' % grid)

    return plotter

_zero_centered = {'impm', 'evap_lndice', 'evap', 'imph_lndice', 'impm_lndice', 'netht_lndice', 'trht_lndice'}#, 'sensht_lndice'} #, 'trht_lndice'}

_reverse_scale = {'impm', 'impm_lndice'}

def plot_params(attrs, data):
    """Adds some ModelE-specific stuff to xaccess.plot_params()"""

    pp = xaccess.plot_params(attrs, data)
 
    var_name = pp.get('var_name', None)
    plot_args = pp['plot_args']
    cb_args = pp['cb_args']

    # Convert result to double precision if needed;
    # Plot functions don't work with single precision
    if attrs[('fetch', 'dtype')] != np.float:
        pp['val'] = pp['val'].astype(np.float)

    if var_name in _zero_centered :

        plot_args['norm'] = giss.plot.AsymmetricNormalize()
        reverse = (var_name in _reverse_scale)
        plot_args['cmap'] = giss.plot.cpt('giss-cpt/BlRe.cpt', reverse=reverse).cmap
        plot_args['vmin'] = np.nanmin(pp['val'])
        plot_args['vmax'] = np.nanmax(pp['val'])
        cb_args['ticks'] = [plot_args['vmin'], 0, plot_args['vmax']]
        cb_args['format'] = '%0.2f'

    year,month = attrs[('fetch', 'date')][:2]
    pp['title'] = pp['title'] + (' %04d-%02d' % (year, month))

    return pp
   
