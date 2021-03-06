#!/usr/bin/env python
#
# ----------------------------------------------------------------------
#
#                           Brad T. Aagaard
#                        U.S. Geological Survey
#
# <LicenseText>
#
# ----------------------------------------------------------------------
#

sim = "tpv14"
cell = "tet4"
dx = 200
dt = 0.05

inputRoot = "output/%s_%s_%03dm" % (sim, cell,dx)
outputRoot = "scecfiles/%s_%s_%03dm" % (sim, cell,dx)

# ----------------------------------------------------------------------
import tables
import numpy
import time

# ----------------------------------------------------------------------
def extract(fault, targets):
    tolerance = 1.0e-6

    h5 = tables.openFile("%s-%s.h5" % (inputRoot, fault), 'r')
    vertices = h5.root.geometry.vertices[:]
    ntargets = targets.shape[0]
    indices = []
    for target in targets:
        dist = ( (vertices[:,0]-target[0])**2 + 
                 (vertices[:,1]-target[1])**2 + 
                 (vertices[:,2]-target[2])**2 )**0.5
        min = numpy.min(dist)
        indices.append(numpy.where(dist <= min+tolerance)[0][0])
    vertices = vertices[indices,:]

    print "Indices: ", indices
    print "Coordinates of selected points:\n",vertices


    # Get datasets
    slip = h5.root.vertex_fields.slip[:]
    slip_rate = h5.root.vertex_fields.slip_rate[:]
    traction = h5.root.vertex_fields.traction[:]

    # BEGIN TEMPORARY
    #timeStamps =  h5.root.vertex_fields.time (not yet available)
    ntimesteps = slip.shape[0]
    timeStamps = numpy.linspace(dt, dt*ntimesteps, ntimesteps-1, endpoint=True)
    # END TEMPORARY

    slip = slip[1:,indices,:]
    slip_rate = slip_rate[1:,indices,:]
    traction = traction[1:,indices,:]

    h5.close()

    headerA = \
        "# problem = %s-2D\n" % sim.upper() + \
        "# author = Brad Aagaard\n" + \
        "# date = %s\n" % (time.asctime()) + \
        "# code = PyLith\n" + \
        "# code_version = 1.5.2a (scecdynrup branch)\n" + \
        "# element_size = %s\n" % dx
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

    lengthScale = 1000.0
    timeScale = 1000.0
    dip = -vertices[:,2] / lengthScale
    if fault == "main_fault":
        strike = (vertices[:,1] - 2000) / lengthScale
    elif fault == "branch_fault":
        strike = 2.0 * vertices[:,0] / lengthScale

    print timeStamps.shape, ntimesteps, slip.shape

    zero = numpy.zeros( (ntimesteps-1, 1), dtype=numpy.float64)
    for iloc in xrange(ntargets):
        pt = locName % (round(10*strike[iloc]), 
                        round(10*dip[iloc]))
        filename = "%s-%s-%s.dat" % (outputRoot, fault, pt)
        fout = open(filename, 'w');
        fout.write(headerA)
        fout.write("# time_step = %14.6E\n" % dt)
        fout.write("# num_timesteps = %8d\n" % (ntimesteps-1))
        fout.write(locHeader % (strike[iloc], dip[iloc]))
        fout.write(headerB)
        data = numpy.transpose((timeStamps, 
                                -slip[:,iloc,0],
                                -slip_rate[:,iloc,0],
                                -traction[:,iloc,0]/1e+6,
                                -slip[:,iloc,1],
                                -slip_rate[:,iloc,1],
                                -traction[:,iloc,1]/1e+6,
                                +traction[:,iloc,2]/1e+6))
        numpy.savetxt(fout, data, fmt='%14.6e')
        fout.close()

    return

# ----------------------------------------------------------------------
# MAIN FAULT

# Target coordinates are relative to faults intersection.
targets = numpy.array([[0.0,  -2000.0,     0.0],
                       [0.0,  +2000.0,     0.0],
                       [0.0,  +5000.0,     0.0],
                       [0.0,  +9000.0,     0.0],
                       [0.0,  -2000.0, -7500.0],
                       [0.0,  +2000.0, -7500.0],
                       [0.0,  +5000.0, -7500.0],
                       [0.0,  +9000.0, -7500.0],
                       ])
# Origin of coordinate system is at center of main fault
targets[:,1] += 2000.0

extract("main_fault", targets)

# ----------------------------------------------------------------------
# BRANCH FAULT

# Target coordinates are relative to faults intersection.
targets = numpy.array([[1000.0,  1732.0508,     0.0],
                       [2500.0,  4330.1270,     0.0],
                       [4500.0,  7794.2286,     0.0],
                       [1000.0,  1732.0508, -7500.0],
                       [2500.0,  4330.1270, -7500.0],
                       [4500.0,  7794.2286, -7500.0],
                       ])
# Origin of coordinate system is at center of main fault
targets[:,1] += 2000.0

extract("branch_fault", targets)


# End of file
