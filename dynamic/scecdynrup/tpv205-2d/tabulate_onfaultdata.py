#!/usr/bin/env python
#
# ----------------------------------------------------------------------
#
#                           Brad T. Aagaard
#                        U.S. Geological Survey
#
# ----------------------------------------------------------------------
#

cell = "quad4"
dx = 50

inputRoot = "output/%s_%03dm_%s-fault" % (cell,dx,"gradient")
outdir = "scecfiles/%s_%03dm_%s/" % (cell,dx,"gradient")

# ----------------------------------------------------------------------
import h5py
import numpy
import time

# ----------------------------------------------------------------------
if dx == 200:
    targets = numpy.array([[0.0, -12000.0, 0.0],
                           [0.0,  -7600.0, 0.0],
                           [0.0,  -4400.0, 0.0],
                           [0.0,      0.0, 0.0],
                           [0.0,  +4400.0, 0.0],
                           [0.0,  +7600.0, 0.0],
                           [0.0, +12000.0, 0.0]])
elif dx == 100 or dx == 50:
    targets = numpy.array([[0.0, -12000.0, 0.0],
                           [0.0,  -7500.0, 0.0],
                           [0.0,  -4500.0, 0.0],
                           [0.0,      0.0, 0.0],
                           [0.0,  +4500.0, 0.0],
                           [0.0,  +7500.0, 0.0],
                           [0.0, +12000.0, 0.0]])
    

tolerance = 1.0e-6

h5 = h5py.File("%s.h5" % inputRoot, 'r', driver="sec2")
vertices = h5['geometry/vertices'][:]
ntargets = targets.shape[0]
indices = []
for target in targets:
    dist = ( (vertices[:,0]-target[0])**2 + 
             (vertices[:,1]-target[1])**2 )**0.5
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
    "# problem = TPV205-2D\n" + \
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
    "#\n" + \
    "# Data fields\n" + \
    "t h-slip h-slip-rate h-shear-stress v-slip v-slip-rate v-shear-stress\n" + \
    "#\n"

locHeader = "# location = on fault, %3.1f km along strike and %3.1f km depth\n"
locName = "st%+04ddp%03d"

lengthScale = 1000.0
dip = 7.5
strike = targets[:,1] / lengthScale

for iloc in xrange(ntargets):
    pt = locName % (round(10*strike[iloc]), 
                    round(10*dip))
    filename = "%sfault%s.dat" % (outdir,pt)
    fout = open(filename, 'w');
    fout.write(headerA)
    fout.write("# time_step = %14.6E\n" % dt)
    fout.write("# num_timesteps = %8d\n" % nsteps)
    fout.write(locHeader % (strike[iloc], dip))
    fout.write(headerB)
    # Vertical components hardwired to zero because they don't exist in 2-D.
    data = numpy.transpose((timeStamps, 
                            -slip[:,iloc,0],
                            -slip_rate[:,iloc,0],
                            -traction[:,iloc,0]/1e+6,
                            +slip[:,iloc,1]*0.0,
                            +slip_rate[:,iloc,1]*0.0,
                            +traction[:,iloc,1]*0.0/1e+6))
    numpy.savetxt(fout, data, fmt='%14.6e')
    fout.close()
