#!/usr/bin/env python
#
# ======================================================================
#
#                           Brad T. Aagaard
#                        U.S. Geological Survey
#
# {LicenseText}
#
# ======================================================================
#

fileSuffix = "eps"

import pylab
from mypylab.Figure import Figure

from runstats import data_v1_3 as data

# ----------------------------------------------------------------------
class PlotSummary(Figure):

    def __init__(self):
        Figure.__init__(self, fontsize=12)
        return

    def main(self):

        width = 9.25
        height = 8.5
        self.open(width, height, margins=[[0.45, 0.6, 0.1],
                                          [0.25, 0.65, 0.30]])
        self.nrows = 3
        self.ncols = 3

        self.resolutions = [1000, 500, 250]
        self.shapes = ["Tet4", "Hex8"]

        self.width = 1.0/(len(self.shapes)+1)
        self.locs = pylab.arange(len(self.resolutions))
        self.loc0 = self.locs - 0.5*len(self.shapes)*self.width

        self.colorShapes = {'Tet4': 'orange',
                            'Hex8': 'blue'}
        
        plots = [{'value': "nvertices",
                  'title': "# Vertices",
                  'log': True,
                  'range': None},
                 {'value': "ncells",
                  'title': "# Cells",
                  'log': True,
                  'range': None},
                 {'value': "memory",
                  'title': "Peak Memory Usage (MB)",
                  'log': True,
                  'range': (1e+1, 2e+4)},
                 {'value': "niterations",
                  'title': "# Iterations in Solve",
                  'log': False,
                  'range': None},
                 {'value': "run_time",
                  'title': "Run Time (s)",
                  'log': True,
                  'range': (1e+1, 3e+3)},
                 {'value': "nflops",
                  'title': "# FLOPS",
                  'log': True,
                  'range': (1e+8, 3e+11)},
                 {'value': "error",
                  'title': "Average Error (m)",
                  'log': True,
                  'range': (1e-5, 1e-2)}]
        irow = 0
        icol = 0
        for plot in plots:
            self.axes(self.nrows, self.ncols, irow+1, icol+1)

            offset = 0
            handles = []
            for shape in self.shapes:
                format = shape + " " + "%dm"
                keys = [format % res for res in self.resolutions]
                d = [data[key][plot['value']] for key in keys]
                h = pylab.bar(self.loc0+offset*self.width, d,
                              self.width,
                              log=plot['log'],
                              color=self.colorShapes[shape])
                handles.append(h)
                offset += 1
            pylab.title(plot['title'])
            pylab.xticks(self.locs, ["%sm" % res for res in self.resolutions])
            if not plot['range'] is None:
                pylab.ylim(plot['range'])
            icol += 1
            if icol >= self.ncols:
                icol = 0
                irow += 1

        self.subplot(self.nrows, self.ncols, irow+1, icol+1)
        pylab.axis('off')
        pylab.legend((handles[0][0], handles[1][0]), self.shapes,
                     shadow=True,
                     loc='center')

        pylab.show()
        pylab.savefig('benchmark_summary.%s' % fileSuffix)
        return


# ----------------------------------------------------------------------
if __name__ == "__main__":
  app = PlotSummary()
  app.main()


# End of file

