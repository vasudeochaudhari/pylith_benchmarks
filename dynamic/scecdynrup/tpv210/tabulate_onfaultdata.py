#!/usr/bin/env python
#
# ----------------------------------------------------------------------
#
#                           Brad T. Aagaard
#                        U.S. Geological Survey
#
# ----------------------------------------------------------------------
#

sim = "tpv13"
cell = "tet4"
dx = 100

inputRoot = "output/%s_%s_%03dm-fault" % (sim,cell,dx)
outdir = "scecfiles/%s_%s_%03dm/" % (sim,cell,dx)

# ----------------------------------------------------------------------
import h5py
import numpy
import time

# ----------------------------------------------------------------------
targets = numpy.array([[     0.0,     0.0,      0.0      ],
                       [  -750.0,     0.0,  -1299.0381057],
                       [ -1500.0,     0.0,  -2598.0762114],
                       [ -2250.0,     0.0,  -3897.1143170],
                       [ -3750.0,     0.0,  -6495.1905284],
                       [ -6000.0,     0.0, -10392.3048454],
                       [     0.0,  4500.0,      0.0      ],
                       [ -3750.0,  4500.0,  -6495.1905284],
                       [     0.0, 12000.0,      0.0      ],
                       [ -3750.0, 12000.0,  -6495.1905284],
                       ])
    

tolerance = 1.0e-6

h5 = h5py.File("%s.h5" % inputRoot, 'r', driver="sec2")
vertices = h5['geometry/vertices'][:]
ntargets = targets.shape[0]
indices = []
for target in targets:
    dist = ( (vertices[:,0]-target[0])**2 + 
             (vertices[:,1]-target[1])**2 +
             (vertices[:,2]-target[2])**2 )**0.5
    min = numpy.min(dist)
    indices.append(numpy.where(dist <= min+tolerance)[0][0])

print "Indices: ", indices
print "Coordinates of selected points:\n",vertices[indices,:]


# Get datasets
slip = h5['vertex_fields/slip'][:]
slip_rate = h5['vertex_fields/slip_rate'][:]
traction = h5['vertex_fields/traction'][:]
timeStamps =  h5['time'][:].ravel()
nsteps = timeStamps.shape[0]
dt = timeStamps[1] - timeStamps[0]

h5.close()

# Extract locations
slip = slip[:,indices,:]
slip_rate = slip_rate[:,indices,:]
traction = traction[:,indices,:]

# Write data
headerA = \
    "# problem = %s\n" % sim.upper() + \
    "# author = Brad Aagaard\n" + \
    "# date = %s\n" % (time.asctime()) + \
    "# code = PyLith\n" + \
    "# code_version = 1.7.0a (scecdynrup branch)\n" + \
    "# element_size = %s m\n" % dx
headerB = \
    "# Time series in 7 columns of E14.6:\n" + \
    "# Column #1 = time (s)\n" + \
    "# Column #2 = horizontal right-lateral slip (m)\n" + \
    "# Column #3 = horizontal right-lateral slip rate (m/s)\n" + \
    "# Column #4 = horizontal right-lateral shear stress (MPa)\n" + \
    "# Column #5 = vertical up-dip slip (m)\n" + \
    "# Column #6 = vertical up-dip slip-rate (m/s)\n" + \
    "# Column #7 = vertical up-dip shear stress (MPa)\n" + \
    "# Column #8 = normal stress (MPa)\n" + \
    "#\n" + \
    "# Data fields\n" + \
    "t h-slip h-slip-rate h-shear-stress v-slip v-slip-rate v-shear-stress n-stress\n" + \
    "#\n"

locHeader = "# location = on fault, %3.1f km along strike and %3.1f km depth\n"
locName = "st%+04ddp%03d"

lengthScale = 1.0e+3
dip = -2*targets[:,0] / lengthScale
strike = targets[:,1] / lengthScale


for iloc in xrange(ntargets):
    pt = locName % (round(10*strike[iloc]), 
                    round(10*dip[iloc]))
    filename = "%sfault%s.dat" % (outdir,pt)
    fout = open(filename, 'w');
    fout.write(headerA)
    fout.write("# time_step = %14.6E\n" % dt)
    fout.write("# num_timesteps = %8d\n" % nsteps)
    fout.write(locHeader % (strike[iloc], dip[iloc]))
    fout.write(headerB)
    data = numpy.transpose((timeStamps, 
                            -slip[:,iloc,0],
                            -slip_rate[:,iloc,0],
                            -traction[:,iloc,0]/1e+6,
                            -slip[:,iloc,1],
                            -slip_rate[:,iloc,1],
                            -traction[:,iloc,1]/1e+6,
                            traction[:,iloc,2]/1e+6))
    numpy.savetxt(fout, data, fmt='%14.6e')
    fout.close()
