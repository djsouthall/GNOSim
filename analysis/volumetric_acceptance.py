'''
This file will eventually load in the various configuration types and other information
to calculate and plot volumetric acceptance of various configuration types as a
function of neutrino energy.

Run in python command line:
exec(open('./gnosim/sim/volumetric_acceptance_dsouthall.py').read())


'''
import glob
import sys
import os
import numpy
import h5py
import pylab
import yaml
import pickle
import types
from matplotlib.colors import LogNorm
sys.path.append('/home/dsouthall/Projects/GNOSim/')
import gnosim.utils.constants
import gnosim.utils.bayesian_efficiency
import gnosim.earth.antarctic
import gnosim.trace.refraction_library
from matplotlib.colors import LogNorm
pylab.ion()


def volumetricAcceptance(reader,verbose = True):
    '''
    Calculates the volumetric acceptance of a run in # km^3 sr
    '''
    if numpy.isin('config_0',list(reader.attrs)):
        config = yaml.load(open(reader.attrs['config_0']))
    elif numpy.isin('config',list(reader.attrs)):
        config = yaml.load(open(reader.attrs['config']))
    else:
        print('Config file not found...')
        pass
        
    if numpy.isin('geometric_factor_0',list(reader.attrs)):
        geometric_factor = reader.attrs['geometric_factor_0']
    elif numpy.isin('geometric_factor',list(reader.attrs)):
        geometric_factor = reader.attrs['geometric_factor_0']
    else:
        print('geometric_factor file not found...')
        pass
    
    if verbose == True:
        print('Loading relevant parts of info')
    info = numpy.unique(reader['info']['eventid','triggered'])
    
    n_events = len(info)
    
    if verbose == True:
        print('Loading z_0')
    z_0 = reader['z_0'][...]
    
    if verbose == True:
        print('Loading p_earth')
    p_earth = reader['p_earth'][...]
    '''
    if verbose == True:
        print('Loading p_interact')
    p_interact = reader['p_interact'][...]
    '''
    
    if verbose == True:
        print('Calculating VA_sum')
    
    VA_sum = numpy.sum(p_earth * (gnosim.earth.antarctic.density(z_0) / gnosim.utils.constants.density_water) * (info['triggered']) )
    VA  = ((geometric_factor / gnosim.utils.constants.km_to_m**3)/n_events) * VA_sum # km^3 sr
    error = VA/numpy.sqrt(VA_sum)
    energy_neutrino = reader['energy_neutrino'][0]
    
    if verbose == True:
        print( 'E = %0.3g GeV'%energy_neutrino)
        print( 'VA = %0.4g km^3 sr +/- %0.4g km^3 sr'%(VA, error))
        print( 'VA = %0.4g km^3 sr +/- %0.4g percent'%(VA, 100.0 * error/VA))
    return VA, error, energy_neutrino

############################
if __name__ == "__main__":
    #Calculation Parameters
    calculate_data = False
    config = 'real_config'
    outdir = '/home/dsouthall/scratch-midway2/'
    outname = outdir +'volumetric_acceptance_data_%s.h5'%(config)
    
    #Plotting Parameters
    plot_data = True
    dataname = '/home/dsouthall/scratch-midway2/real_config_10deg_pretrigger_Feb2019/volumetric_acceptance_data_real_config.h5'
    plot_comparison = True
    comparison_file = '/home/dsouthall/Projects/GNOSim/gnosim/analysis/DesignPerformancePaperData.py'
    
    if calculate_data == True:
        ######
        infiles = glob.glob('./*merged*.h5')
        print('Attempting to calculate volumetric acceptance for the following files:')
        for infile in infiles:
            print(infile)

        if os.path.exists(outname):
            print('Output file with name %s already exists, saving appending \'_new\' if necessary'%(outname))
            while os.path.exists(outname):
                outname = outname.replace('.h5','_new.h5')
        print('Saving as %s'%outname)
        writer = h5py.File(outname , 'w')

        writer.create_dataset('volumetric_acceptance', (len(infiles),), dtype='f', compression='gzip', compression_opts=9, shuffle=True)
        writer.create_dataset('error', (len(infiles),), dtype='f', compression='gzip', compression_opts=9, shuffle=True)
        writer.create_dataset('energy_neutrino', (len(infiles),), dtype='f', compression='gzip', compression_opts=9, shuffle=True)

        for index, infile in enumerate(infiles):
            print('Loading reader:\n%s'%infile)
            reader = h5py.File(infile , 'r')
            VA, error, energy_neutrino = volumetricAcceptance(reader,verbose = True)
            reader.close()
            writer[index] = VA
            writer['error'][index] = error
            writer['energy_neutrino'][index] = energy_neutrino
         
        writer.close()
    
    if plot_data:
    
    
        markersize = 10
        linewidth = 5
        reader = h5py.File(dataname , 'r')
        energy_neutrino = reader['energy_neutrino'][...]
        
        VA = reader['volumetric_acceptance'][...]
        error = reader['error'][...]
        
        cut = VA != 0 
        label='GNOSim'
        sorted_cut = numpy.argsort(energy_neutrino)[numpy.isin(numpy.argsort(energy_neutrino),numpy.where(cut)[0])]
        fig = pylab.figure(figsize=(16.,11.2))
        pylab.errorbar(energy_neutrino[sorted_cut]/1e6, VA[sorted_cut], yerr=error[sorted_cut],fmt='go-',label=label,capsize=5,markersize=markersize,linewidth=linewidth)
            
        if plot_comparison == True:
            plot_comparison = True
            compare_data = yaml.load(open(comparison_file))
            for key in compare_data.keys():
                x = numpy.array(compare_data[key]['x'])
                y = numpy.array(compare_data[key]['y'])
                pylab.errorbar(x,y, yerr=None,fmt=compare_data[key]['style'],label=compare_data[key]['label'],capsize=5,markersize=markersize,linewidth=linewidth)
            
            
        pylab.legend(loc = 'lower right',fontsize = 24)
        #pylab.ylim(8e-7,1.5e2)
        #pylab.xlim(8e5,2e10)
        ax = pylab.gca()
        ax.minorticks_on()
        ax.set_xscale('log')
        ax.set_yscale('log')
        pylab.tick_params(labelsize=16)
        pylab.xlabel('Neutrino Energy (PeV)',fontsize = 20)
        pylab.ylabel('V$\Omega$ (km$^3$ sr)',fontsize = 20)
        pylab.grid(b=True, which='major', color='k', linestyle='-')
        pylab.grid(b=True, which='minor', color='tab:gray', linestyle='--',alpha=0.5)
        #ax.patch.set_alpha(0.)
        #fig.patch.set_alpha(0.)
        #pylab.legend(loc = 'lower left',fontsize = 16)
        #pylab.xlim(8e5,2e10)
        #pylab.ylim(5e-3,5e1)
        #ax = pylab.gca()
        #ax.minorticks_on()
            
            
            
            
            
            
            
            
            
            
