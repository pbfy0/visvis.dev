# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def processEvents():
    """ processEvents()
    
    Processes all GUI events (and thereby all visvis events).
    Users can periodically call this function during running 
    an algorithm to keep the figures responsove.
    
    Note that IEP and IPython can integrate the GUI event loop to 
    periodically update the GUI events when idle.
    
    Also see Figure.DrawNow()
    
    """
    
    app = vv.backends.currentBackend.app
    if app:
        app.ProcessEvents()
