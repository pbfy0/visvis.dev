#   Copyright (c) 2010, Almar Klein
#   All rights reserved.
#
#   This code is subject to the (new) BSD license:
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY 
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Package vvmovie (visvis-movie)
All submodules have been designed to be work independant of each-other 
(except the AVI module, which requires the IMS module).

Provides the following functions:

  * readGif & writeGif  -> a movie stored as animated GIF
  * readSwf & writeSwf  -> a movie stored as shockwave flash
  * readAvi & writeAvi  -> a movie stored as compressed video
  * readIms & writeIms  -> a movie stored as a series of images

Two additional functions are provided for ease of use, that call
the right function depending on the used file extension:
  * movieRead
  * movieWrite

More information about compression and limitations:

  * GIF. Requires PIL. Animated GIF applies a color-table of maximal
    256 colors and applies poor compression. It's widely applicable though. 
  * SWF. Provides lossless storage of movie frames with good (ZLIB) 
    compression. Reading of SWF files is limited to images stored using ZLIB
    compression (no JPEG files). Requires no external libraries.
  * AVI. Requires ffmpeg. Most Linux can obtain it using their package
    manager. Windows users can use the installer at the visvis website.
    Provides excelent mpeg4 (or any other supported by ffmpeg) compression.
    Not intended for reading very large movies.
  * IMS. Requires PIL. Quality depends on the used image type. Use png for  
    lossless compression and jpg otherwise.

"""

import os, time

from images2gif import readGif, writeGif
from images2swf import readSwf, writeSwf
from images2avi import readAvi, writeAvi
from images2ims import readIms, writeIms

videoTypes = ['AVI', 'MPG', 'MPEG', 'MOV', 'FLV']
imageTypes = ['JPG', 'JPEG', 'PNG', 'TIF', 'TIFF', 'BMP']


def movieWrite(filename, images, duration=0.1, repeat=True, **kwargs):
    """ movieWrite(fname, images, duration=0.1, repeat=True, **kwargs)
    
    Write the movie specified in images to GIF, SWF, AVI/MPEG, or a series
    of images (PNG,JPG,TIF,BMP).
    
    General parameters
    ------------------
    filename : string
       The name of the file to write the image to.
    images : list
        Should be a list consisting of PIL images or numpy arrays. 
        The latter should be between 0 and 255 for integer types, 
        and between 0 and 1 for float types.
    duration : scalar
        The duration for all frames. For GIF and SWF this can also be a list
        that specifies the duration for each frame. (For swf the durations
        are rounded to integer amounts of the smallest duration.)
    repeat : bool or integer
        Can be used in GIF and SWF to indicate that the movie should
        loop. For GIF, an integer can be given to specify the number of loops.  
    
    Special GIF parameters
    ----------------------
    dither : bool
        Whether to apply dithering
    nq : integer
        If nonzero, applies the NeuQuant quantization algorithm to create
        the color palette. This algorithm is superior, but slower than
        the standard PIL algorithm. The value of nq is the quality 
        parameter. 1 represents the best quality. 10 is in general a
        good tradeoff between quality and speed.
    
    Special AVI/MPEG parameters
    ---------------------------
    encoding : {'mpeg4', 'msmpeg4v2', ...}
        The encoding to use. Hint for Windows users: the 'msmpeg4v2' codec 
        is natively supported on Windows.
    inputOptions : string
        See the documentation of ffmpeg
    outputOptions : string
        See the documentation of ffmpeg
    
    Notes for writing a series of images
    ------------------------------------
    If the filenenumber contains an asterix, a sequence number is introduced 
    at its location. Otherwise the sequence number is introduced right before
    the final dot. To enable easy creation of a new directory with image 
    files, it is made sure that the full path exists.
    
    Notes for writing AVI/MPEG
    --------------------------
    Writing AVI requires the "ffmpeg" application:
      * Most linux users can install it using their package manager.
      * There is a windows installer on the visvis website.
    
    """
    
    # Test images
    if not isinstance(images, (tuple, list)):
        raise ValueError("Images should be a tuple or list.")
    if not images:
        raise ValueError("List of images is empty.")
    
    # Get extension
    EXT = os.path.splitext(filename)[1]
    EXT = EXT[1:].upper()
    
    # Start timer
    t0 = time.time()
    
    # Write
    if EXT == 'GIF':
        writeGif(filename, images, duration, repeat, **kwargs)
    elif EXT == 'SWF':
        writeSwf(filename, images, duration, repeat, **kwargs)
    elif EXT in videoTypes:
        writeAvi(filename, images, duration, **kwargs)
    elif EXT in imageTypes:
        writeIms(filename, images, **kwargs)
    else:
        raise ValueError('Given file extension not valid: '+EXT)
    
    # Stop timer
    t1 = time.time()
    dt = t1-t0
    
    # Notify    
    print "Wrote %i frames to %s in %1.2f seconds (%1.0f ms/frame)" % (
                        len(images), EXT, dt, 1000*dt/len(images))


def movieRead(filename, asNumpy=True, **kwargs):
    """ movieRead(fname)
    
    Read the movie from GIF, SWF, AVI (or MPG), or a series of images (PNG,
    JPG,TIF,BMP). Returns a list of numpy arrays, or, if asNumpy is false, 
    a list if PIL images.
    
    Notice: reading AVI requires the "ffmpeg" application:
      * Most linux users can install it using their package manager
      * There is a windows installer on the visvis website
    
    """
    
    # Get extension
    EXT = os.path.splitext(filename)[1]
    EXT = EXT[1:].upper()
    
    # Start timer
    t0 = time.time()
    
    # Write
    if EXT == 'GIF':
        images = readGif(filename, asNumpy, **kwargs)
    elif EXT == 'SWF':
        images = readSwf(filename,  asNumpy, **kwargs)
    elif EXT in videoTypes:
        images = readAvi(filename,  asNumpy, **kwargs)
    elif EXT in imageTypes:
        images = readIms(filename,  asNumpy, **kwargs)
    else:
        raise ValueError('Given file extension not valid: '+EXT)
    
    # Stop timer
    t1 = time.time()
    dt = t1-t0
    
    # Notify 
    if images:
        print "Read %i frames from %s in %1.2f seconds (%1.0f ms/frame)" % (
                        len(images), EXT, dt, 1000*dt/len(images))
    else:
        print "Could not read any images."
    
    # Done
    return images

