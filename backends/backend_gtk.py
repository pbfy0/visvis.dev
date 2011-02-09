""" The GTK backend.
"""

import os, sys

from visvis import BaseFigure, events, constants
from visvis.misc import getResourceDir

import gtk
import gtk.gtkgl
import gobject

import OpenGL.GL as gl

MOUSEMAP = {gtk.gdk.BUTTON_PRESS   : 'down',
            gtk.gdk.BUTTON_RELEASE : 'up',
            gtk.gdk._2BUTTON_PRESS : 'double'}

KEYMAP = {  gtk.keysyms.Shift_L: constants.KEY_SHIFT, 
            gtk.keysyms.Shift_R: constants.KEY_SHIFT,
            gtk.keysyms.Alt_L: constants.KEY_ALT,
            gtk.keysyms.Alt_R: constants.KEY_ALT,
            gtk.keysyms.Control_L: constants.KEY_CONTROL,
            gtk.keysyms.Control_R: constants.KEY_CONTROL,
            gtk.keysyms.Left: constants.KEY_LEFT,
            gtk.keysyms.Up: constants.KEY_UP,
            gtk.keysyms.Right: constants.KEY_RIGHT,
            gtk.keysyms.Down: constants.KEY_DOWN,
            gtk.keysyms.Page_Up: constants.KEY_PAGEUP,
            gtk.keysyms.Page_Down: constants.KEY_PAGEDOWN,
            gtk.keysyms.KP_Enter: constants.KEY_ENTER,
            gtk.keysyms.Return: constants.KEY_ENTER,
            gtk.keysyms.Escape: constants.KEY_ESCAPE,
            gtk.keysyms.Delete: constants.KEY_DELETE,
            }

class GlCanvas(gtk.gtkgl.DrawingArea):
    
    def __init__(self, figure, *args, **kw):
        gtk.gtkgl.DrawingArea.__init__(self)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK |
                        gtk.gdk.POINTER_MOTION_MASK |
                        gtk.gdk.POINTER_MOTION_HINT_MASK |
                        gtk.gdk.KEY_PRESS_MASK |
                        gtk.gdk.KEY_RELEASE_MASK |
                        gtk.gdk.ENTER_NOTIFY_MASK |
                        gtk.gdk.LEAVE_NOTIFY_MASK |
                        gtk.gdk.FOCUS_CHANGE_MASK)
        self.set_property('can-focus', True)
        
        self.figure = figure
         
        # Configure OpenGL framebuffer.
        # Try to get a double-buffered framebuffer configuration,
        # if not successful then try to get a single-buffered one.
        display_mode = (gtk.gdkgl.MODE_RGB    |
                        gtk.gdkgl.MODE_DEPTH  |
                        gtk.gdkgl.MODE_DOUBLE)
        try:
            glconfig = gtk.gdkgl.Config(mode=display_mode)
        except gtk.gdkgl.NoMatches:
            display_mode &= ~gtk.gdkgl.MODE_DOUBLE
            glconfig = gtk.gdkgl.Config(mode=display_mode)
        self.set_gl_capability(glconfig)
        
        # Connect the relevant signals.
        self.connect('configure_event', self._on_configure_event)
        self.connect('expose_event',    self._on_expose_event)
        self.connect('delete_event', self._on_delete_event)
        self.connect('motion_notify_event', self._on_motion_notify_event)
        self.connect('button_press_event', self._on_button_event)
        self.connect('button_release_event', self._on_button_event)
        self.connect('key_press_event', self._on_key_press_event)
        self.connect('key_release_event', self._on_key_release_event)
        self.connect('enter_notify_event', self._on_enter_notify_event)
        self.connect('leave_notify_event', self._on_leave_notify_event)
        self.connect('focus_in_event', self._on_focus_in_event)
        
    def _on_configure_event(self, *args):
        if self.figure:
            self.figure._OnResize()
        return False
        
    def _on_delete_event(self, *args):
        if self.figure:
            self.figure.Destroy()
        return True # Let figure.Destoy() call this destroy?
    
    def _on_motion_notify_event(self, widget, event):
        if event.is_hint:
            x, y, state = event.window.get_pointer()
        else:
            x, y, state = event.x, event.y, event.state
        self.figure._mousepos = x, y
        self.figure._GenerateMouseEvent('motion', x, y, 0)
    
    def _on_button_event(self, widget, event):
        button = {1:1, 3:2}.get(event.button, 0)
        self.figure._GenerateMouseEvent(MOUSEMAP[event.type], event.x, event.y, button)
    
    def _on_key_press_event(self, widget, event):
        ev = self.figure.eventKeyDown
        ev.Set(KEYMAP.get(event.keyval, event.keyval), event.string)
        ev.Fire()
    
    def _on_key_release_event(self, widget, event):
        ev = self.figure.eventKeyUp
        ev.Set(KEYMAP.get(event.keyval, event.keyval), event.string)
        ev.Fire()
    
    def _on_enter_notify_event(self, widget, event):
        if self.figure:
            ev = self.figure.eventEnter
            ev.Set(0,0,0)
            ev.Fire()
    
    def _on_leave_notify_event(self, widget, event):
        if self.figure:
            ev = self.figure.eventLeave
            ev.Set(0,0,0)
            ev.Fire()
    
    def _on_focus_in_event(self, widget, event):
        if self.figure:
            BaseFigure._currentNr = self.figure.nr
   
    def _on_expose_event(self, *args):
        # Obtain a reference to the OpenGL drawable
        # and rendering context.
        gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()

        # OpenGL begin
        if not gldrawable.gl_begin(glcontext):
            return False

        self.figure.OnDraw()

        # OpenGL end
        gldrawable.gl_end()
    
    def set_current(self):
        gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()
        
        gldrawable.make_current(glcontext)
    
    def swap_buffers(self):
        gldrawable = self.get_gl_drawable()
        glcontext = self.get_gl_context()

        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            glFlush()


class Figure(BaseFigure):
    
    def __init__(self, *args, **kw):
        # todo: Allow docking the canvas in another gtk widget, need parent for that?
        
        # Make sure there is a native app and the timer is started 
        # (also when embedded)
        app.Create()
        
        # Create gl widget
        self._widget = GlCanvas(self, *args, **kw)
        BaseFigure.__init__(self)
    
    def _SetCurrent(self):
        """Make figure the current OpenGL context."""
        if not self._destroyed:
            self._widget.set_current()
    
    def _SwapBuffers(self):
        """Swap the memory and screen buffers."""
        if not self._destroyed:
            self._widget.swap_buffers()
    
    def _RedrawGui(self):
        """???"""
        if self._widget:
            # Should we actually draw, or just mark everything dirty?
            self._widget.queue_draw()
    
#    def _PostDrawRequest(self):
#        """Called to request a redraw."""
#        pass
    
    def _ProcessGuiEvents(self):
        """Process all events in queue."""
        app.ProcessEvents()
    
    def _SetTitle(self, title):
        """Set the title, when not used in application."""
        if not self._destroyed:
            window = self._widget.parent
            if isinstance(window, gtk.Window):
                window.set_title(title)
    
    def _SetPosition(self, x, y, w, h):
        """Set the position of the widget."""
        if not self._destroyed:
            #print "Set Position"
            self._widget.set_size_request(w, h)
            # todo: also specify position
            self._widget.queue_resize()
    
    def _GetPosition(self):
        """Get the widget's position."""
        if not self._destroyed:
            alloc = self._widget.allocation
            return alloc.x, alloc.y, alloc.width, alloc.height
    
    def _Close(self, widget):
        """Close the widget."""
        if widget is None:
            widget = self._widget
        window = widget.parent
        if isinstance(window, gtk.Window):
            window.destroy()
        else:
            widget.destroy()
        # If only this window remains, then quit as we close it.
        #if len(gtk.window_list_toplevels()) == 1:
        #    gtk.main_quit()
        
        # If no more figures, quit
        if len(BaseFigure._figures) == 0:
            app.Quit()


def newFigure():
    """Create a figure and put it in a window."""
    
    figure = Figure()
    window = gtk.Window()
    
    # Set icon
    try:
        iconfile = os.path.join(getResourceDir(), 'visvis_icon_gtk.png')
        window.set_icon_from_file(iconfile)
    except Exception as e:
        pass
    
    # From GTKGL example
    if sys.platform != 'win32':
        window.set_resize_mode(gtk.RESIZE_IMMEDIATE)
    window.set_reallocate_redraws(True)
    
    window.add(figure._widget)
    figure._widget.set_size_request(560, 420)
    window.show_all()
    
    window.connect('delete-event', figure._widget._on_delete_event)
    
    # Initialize OpenGl
    #figure.DrawNow() # DrawNow causes hang in IPython
    figure._widget._on_expose_event()
    return figure


class VisvisEventsTimer:
    """ Timer that can be started and stopped.
    """
    def __init__(self):
        self._running = False
    def Start(self):
        if not self._running:
            self._running = True
            self._PostTimeout()
    def Stop(self):
        self._running = False
    def _PostTimeout(self):
        gobject.timeout_add(10, self._Fire)
    def _Fire(self):
        if self._running:
            events.processVisvisEvents()
            return True # So called again.


class App(events.App):
    """App()
    
    Application class to wrap the GUI applications in a class
    with a simple interface that is the same for all backends.
    
    This is the GTK implementation.
    
    """
    
    def __init__(self):
        # Create timer
        self._timer = VisvisEventsTimer()
    
    def _GetNativeApp(self):
        """Ensure the GTK app exists."""
        
        # Start timer
        self._timer.Start()
        
        # Prevent quiting when used interactively
        # todo: this is what it does right?
        if not hasattr(gtk, 'vv_do_quit'):
            gtk.vv_do_quit = False
        
        # Return singleton gtk object, which represents the gtk application
        return gtk
    
    def _ProcessEvents(self):
        """Process GTK events."""
        while gtk.events_pending():
            gtk.main_iteration(False)

    def _Run(self):
        """Enter GTK mainloop."""
        self._GetNativeApp()
        
        if gtk.main_level() > 0:
            pass # Already in mainloop.
        else:
            gtk.vv_do_quit = True
            gtk.main()
    
    # todo: doesn't gtk do this automatically when there are no more
    # top level windows, like the other toolkits?
    def Quit(self):
        if gtk.vv_do_quit:
            gtk.main_quit()

app = App()