# -*- coding: utf-8 -*-
# Copyright (c) 2014, imageio contributors
# imageio is distributed under the terms of the (new) BSD License.

""" Storage of image data in npz format. Not a great format, but at least
it supports volumetric data. And its less than 100 lines.
"""

from __future__ import absolute_import, print_function, division

import numpy as np

from imageio import formats
from imageio.core import Format


class NpzFormat(Format):
    """ NPZ is a file format by numpy that provides storage of array
    data using gzip compression. This imageio plugin supports data of any
    shape, and also supports multiple images per file. 
    
    However, the npz format does not provide streaming; all data is
    read/saved at once. Further, there is no support for meta data.

    Beware that the numpy npz format has a bug on a certain combination
    of Python 2.7 and numpy, which can cause the resulting files to
    become unreadable on Python 3.
    
    Parameters for reading
    ----------------------
    None
    
    Parameters for saving
    ---------------------
    None
    """
    
    def _can_read(self, request):
        if request.filename.lower().endswith('.npz'):
            return True  # We support any kind of image data
        else:
            return False
    
    def _can_save(self, request):
        if request.filename.lower().endswith('.npz'):
            return True  # We support any kind of image data
        else:
            return False
    
    # -- reader
    
    class Reader(Format.Reader):
    
        def _open(self):
            # Load npz file, which provides another file like object
            self._npz = np.load(self.request.get_file())
            assert isinstance(self._npz, np.lib.npyio.NpzFile)
            # Get list of names, ordered by name, but smarter
            sorter = lambda x: x.split('_')[-1]
            self._names = sorted(self._npz.files, key=sorter)
        
        def _close(self):
            self._npz.close()
        
        def _get_length(self):
            return len(self._names)
        
        def _get_data(self, index):
            # Get data
            if index < 0 or index >= len(self._names):
                raise IndexError('Index out of range while reading from nzp')
            im = self._npz[self._names[index]]
            # Return array and empty meta data
            return im, {}
        
        def _get_meta_data(self, index):
            # Get the meta data for the given index
            raise RuntimeError('The npz format does not support meta data.')
    
    # -- writer
    
    class Writer(Format.Writer):
        
        def _open(self):
            # Npz is not such a great format. We cannot stream to the file.
            # So we remember all images and write them to file at the end.
            self._images = []
        
        def _close(self):
            # Write everything
            np.savez_compressed(self.request.get_file(), *self._images)
        
        def _append_data(self, im, meta):
            self._images.append(im)  # discart meta data
        
        def set_meta_data(self, meta):
            raise RuntimeError('The npz format does not support meta data.')


# Register
format = NpzFormat('npz', "Numpy's compressed array format", 'npz')
formats.add_format(format)
