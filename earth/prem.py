'''
Density of the Earth.

Source: Preliminary Reference Earth Model (PREM) (Dziewonski & Anderson, 1981)
        http://geophysics.ou.edu/solid_earth/prem.html
'''

import numpy
import scipy.interpolate
import pylab

import gnosim.utils.constants
import gnosim.earth.ice

pylab.ion()
############################################################

prem_string = '''#http://geophysics.ou.edu/solid_earth/prem.html
#Preliminary Reference Earth Model (PREM) (Dziewonski & Anderson, 1981)
#Region         
#Radius              alpha beta rho           Ks        mu      nu      P       g
#(km)   (m/s)   (m/s)   (kg/m3)         (Gpa)   (Gpa)           (Gpa)   (m/s2)
#Inner Core     
0.0     11266.20        3667.80         13088.48        1425.3  176.1   0.4407  363.850         0.0000
200.0   11255.93        3663.42         13079.77        1423.1  175.5   0.4408  362.900         0.7311
400.0   11237.12        3650.27         13053.64        1416.4  173.9   0.4410  360.030         1.4604
600.0   11205.76        3628.35         13010.09        1405.3  171.3   0.4414  355.280         2.1862
800.0   11161.86        3597.67         12949.12        1389.8  167.6   0.4420  348.670         2.9068
1000.0  11105.42        3558.23         12870.73        1370.1  163.0   0.4428  340.240         3.6203
1200.0  11036.43        3510.02         12774.93        1346.2  157.4   0.4437  330.050         4.3251
1221.5  11028.27        3504.32         12763.60        1343.4  156.7   0.4438  328.850         4.4002
#Outer Core     
1221.5  10355.68        0.00    12166.34        1304.7  0.0     0.5000  328.850         4.4002
1400.0  10249.59        0.00    12069.24        1267.9  0.0     0.5000  318.750         4.9413
1600.0  10122.91        0.00    11946.82        1224.2  0.0     0.5000  306.150         5.5548
1800.0  9985.54         0.00    11809.00        1177.5  0.0     0.5000  292.220         6.1669
2000.0  9834.96         0.00    11654.78        1127.3  0.0     0.5000  277.040         6.7715
2200.0  9668.65         0.00    11483.11        1073.5  0.0     0.5000  260.680         7.3645
2400.0  9484.09         0.00    11292.98        1015.8  0.0     0.5000  243.250         7.9425
2600.0  9278.76         0.00    11083.35        954.2   0.0     0.5000  224.850         8.5023
2800.0  9050.15         0.00    10853.21        888.9   0.0     0.5000  205.600         9.0414
3000.0  8795.73         0.00    10601.52        820.2   0.0     0.5000  185.640         9.5570
3200.0  8512.98         0.00    10327.26        748.4   0.0     0.5000  165.120         10.0464
3400.0  8199.39         0.00    10029.40        674.3   0.0     0.5000  144.190         10.5065
3480.0  8064.82         0.00    9903.49         644.1   0.0     0.5000  135.750         10.6823
#D''    
3480.0  13716.60        7264.66         5566.45         655.6   293.8   0.3051  135.750         10.6823
3600.0  13687.53        7265.75         5506.42         644.0   290.7   0.3038  128.710         10.5204
3630.0  13680.41        7265.97         5491.45         641.2   289.9   0.3035  126.970         10.4844
#Lower mantle   
3630.0  13680.41        7265.97         5491.45         641.2   289.9   0.3035  126.970         10.4844
3800.0  13447.42        7188.92         5406.81         609.5   279.4   0.3012  117.350         10.3095
4000.0  13245.32        7099.74         5307.24         574.4   267.5   0.2984  106.390         10.1580
4200.0  13015.79        7010.53         5207.13         540.9   255.9   0.2957  95.760  10.0535
4400.0  12783.89        6919.57         5105.90         508.5   244.5   0.2928  85.430  9.9859
4600.0  12544.66        6825.12         5002.99         476.6   233.1   0.2898  75.360  9.9474
4800.0  12293.16        6725.48         4897.83         444.8   221.5   0.2864  65.520  9.9314
5000.0  12024.45        6618.91         4789.83         412.8   209.8   0.2826  55.900  9.9326
5200.0  11733.57        6563.70         4678.44         380.3   197.9   0.2783  46.490  9.9467
5400.0  11415.60        6378.13         4563.07         347.1   185.6   0.2731  37.290  9.9698
5600.0  11065.57        6240.46         4443.17         313.3   173.0   0.2668  28.290  9.9985
5600.0  11065.57        6240.46         4443.17         313.3   173.0   0.2668  28.290  9.9985
5701.0  10751.31        5945.08         4380.71         299.9   154.8   0.2798  23.830  10.0143
#Transition Zone        
5701.0  10266.22        5570.20         3992.14         255.6   123.9   0.2914  23.830  10.0143
5771.0  10157.82        5516.01         3975.84         248.9   121.0   0.2909  21.040  10.0038
5771.0  10157.82        5516.01         3975.84         248.9   121.0   0.2909  21.040  10.0038
5871.0  9645.88         5224.28         3849.80         218.1   105.1   0.2924  17.130  9.9883
5971.0  9133.97         4932.59         3723.78         189.9   90.6    0.2942  13.350  9.9686
5971.0  8905.22         4769.89         3543.25         173.5   80.6    0.2988  13.350  9.9686
6061.0  8732.09         4706.90         3489.51         163.0   77.3    0.2952  10.200  9.9361
6151.0  8558.96         4643.91         3435.78         152.9   74.1    0.2914  7.110   9.9048
#Low Velocity Zone      
6151.0  7989.70         4418.85         3359.50         127.0   65.6    0.2797  7.110   9.9048
6221.0  8033.70         4443.61         3367.10         128.7   66.5    0.2796  4.780   9.8783
6291.0  8076.88         4469.53         3374.71         130.3   67.4    0.2793  2.450   9.8553
#LID    
6291.0  8076.88         4469.53         3374.71         130.3   67.4    0.2793  2.450   9.8553
6346.6  8110.61         4490.94         3380.76         131.5   68.2    0.2789  0.604   9.8394
#Crust  
6346.6  6800.00         3900.00         2900.00         75.3    44.1    0.2549  0.604   9.8394
6356.0  6800.00         3900.00         2900.00         75.3    44.1    0.2549  0.337   9.8332
6356.0  5800.00         3200.00         2600.00         52.0    26.6    0.2812  0.337   9.8332
6368.0  5800.00         3200.00         2600.00         52.0    26.6    0.2812  0.300   9.8222
#Ocean  
6368.0  1450.00         0.00    1020.00         2.1     0.0     0.5000  0.300   9.8222
6371.0  1450.00         0.00    1020.00         2.1     0.0     0.5000  0.000   9.8156'''

############################################################

#def prem(infile='prem.dat', plot=False):
def prem(ice):
    '''
    Returns an scipy.interpolate.interp1d function representing the density of the Earth in nucleons m^-3 as a function of radius.
    
    Source: Preliminary Reference Earth Model (PREM) (Dziewonski & Anderson, 1981)
        http://geophysics.ou.edu/solid_earth/prem.html

    Parameters
    ----------
    ice : gnosim.earth.ice.Ice
        The ice object containing the appropriate ice model.  This will be put on the surface of the PREM model.

    Returns
    -------
    f : scipy.interpolate.interp1d
        A function representing the density of the Earth in nucleons m^-3 as a function of radius.
    '''
    lines = prem_string.split('\n')

    radius = [] # km
    density = [] # kg m^-3
    for line in lines:
        if '#' in line:
            continue
    
        parts = line.split()
        if len(parts) != 9:
            continue

        radius.append(float(parts[0]))
        density.append(float(parts[3]))
    
    radius = numpy.array(radius) * gnosim.utils.constants.km_to_m # convert from km to m
    density = numpy.array(density) / gnosim.utils.constants.mass_proton # convert from kg m^-3 to nucleons m^-3
    
    # Overlay ice on the model for the Earth density profile 
    z = numpy.linspace(-1. * ice.ice_thickness, 0., 100.) # m
    radius_ice = gnosim.utils.constants.radius_earth + z # m
    density_ice = ice.density(z) # nucleons m^-3  
    radius = numpy.concatenate([radius, radius_ice]) # Now merge
    density = numpy.concatenate([density, density_ice])

    f = scipy.interpolate.interp1d(radius, density, bounds_error=False, fill_value=0.)
    return f

############################################################

if __name__ == '__main__':
    ice_model = 'antarctica'
    ice = gnosim.earth.ice.Ice(antarctica)
    f = prem(ice) # Earth density interpolation function object
    r = numpy.linspace(0., gnosim.utils.constants.radius_earth, 100000) # Array of radii values (m) 

    pylab.figure()
    pylab.plot(r / gnosim.utils.constants.km_to_m, f(r) * gnosim.utils.constants.mass_proton) # Convert from km to m, nucleons m^-3 to kg m^-3
    pylab.title('Density of the Earth')
    pylab.xlabel('Radius (km)')
    pylab.ylabel('Density (kg m$^{-3}$)')

############################################################
