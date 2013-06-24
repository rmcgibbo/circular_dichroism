"""Parser for PCD files from the Protein Circular Dichroism Database
"""
##############################################################################
# Imports
##############################################################################

import os
import glob

import matplotlib.pyplot as pp
import numpy as np
import pandas as pd

##############################################################################
# Classes
##############################################################################

class PCDFile(object):
    """Parser for PCD files from the Protein Circular Dichroism Database"""
    def __init__(self, filename):
        self._fh = open(filename, 'r')
        
        try:
            self._read_header()
            self._read_data()
            self._read_calibration()
        finally:
            self._fh.close()
    

    @property
    def header(self):
        """dict containing the information at the top of the pcd file, which
        gives most of the experimental details"""
        return self._header
        
    @property
    def data(self):
        """pandas dataframe containing the data in six columns. i'm not sure
        what all of the columns mean, but 'final' looks pretty good"""
        return self._data
        
    @property
    def calibration(self):
        """pandas dataframe containing a calibration dataset"""
        return self._calibration
    
        
    def _read_header(self):
        self._header = {}
        for line in self._fh:
            line = line.strip()
            if line.startswith('DATA'):
                assert line == 'DATA (1. Wavelength. 2. Final. 3. HT. 4.Smoothed. 5. Avg. Sample. 6. Avg. Baseline.)'
                return 

            key = line[:60].strip()
            value = line[60:].strip()
            self.header[key] = value
    
    def _read_data(self):
        table = []
        for line in self._fh:
            line = line.strip()
            if line.startswith('CALIBRATION'):
                assert line == 'CALIBRATION (1. Wavelength. 2. Calibration Spectrum.)'
                break
                
            fields = line.split()
            assert len(fields) == 6, fields
            table.append(fields)
      
        table = np.array(table, dtype=float)
        wavelength = pd.Series(table[:, 0], name='wavelength')
        self._data = pd.DataFrame(table[:, 1:], index=wavelength,
            columns=['final', 'ht', 'smoothed', 'avg-sample', 'avg-baseline']).sort()

    def _read_calibration(self):
        table = []
        for line in self._fh:
            line = line.strip()
            if line == 'PCDDB-END':
                break

            fields = line.split()
            assert len(fields) == 2
            table.append(fields)

        table = np.array(table, dtype=float)
        wavelength = pd.Series(table[:, 0], name='wavelength')
        
        self._calibration = pd.DataFrame(table[:,1], index=wavelength,
                columns=['calibration']).sort()


if __name__ == '__main__':
    from collections import Counter
    pdbs = Counter()
    for i, pcdfn in enumerate(glob.glob('pcddb/*.pcd')):
        # print pcdfn
        f = PCDFile(pcdfn)
        pdbs[f.header['PDB ID']] += 1
        # name = os.path.split(pcdfn)[-1]
        # pngname = 'plots/' + os.path.splitext(name)[0] + '.png'
        # pp.clf()
        # f.data['avg-sample'].plot(title='%s, pdb=%s' % (name, f.header['PDB ID']))
        # pp.xlabel('wavelength')
        # pp.savefig(pngname)
        # print 'saving %s' % pngname

        
    unique = [k for k in pdbs.keys() if len(k) == 4]
    print unique, len(unique)
        

        