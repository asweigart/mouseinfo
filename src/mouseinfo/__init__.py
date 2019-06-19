# Mouse Info by Al Sweigart al@inventwithpython.com

__version__ = '0.0.1'


# =========================================================================
# This code make this application dependent on PyAutoGUI being installed:
#from pyautogui import position, screenshot, size
# =========================================================================
# Alternatively, this code makes this application not dependent on PyAutoGUI
# by copying the code for the position() and screenshot() functions into this
# source code file.
import sys, platform, datetime, subprocess, os
from PIL import Image, ImageGrab

if sys.platform == 'win32':
    import ctypes
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long),
                    ("y", ctypes.c_long)]

    def _winPosition():
        cursor = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
        return (cursor.x, cursor.y)
    position = _winPosition


    def _winScreenshot():
        # TODO - Use the winapi to get a screenshot, and compare performance with ImageGrab.grab()
        # https://stackoverflow.com/a/3586280/1893164
        try:
            im = ImageGrab.grab()
        except NameError:
            raise ImportError('Pillow module must be installed to use screenshot functions on Windows.')
        return im
    screenshot = _winScreenshot

    def _winSize():
        return (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
    size = _winSize

elif sys.platform == 'darwin':
    try:
        import Quartz
    except:
        assert False, "You must first install pyobjc-core and pyobjc: https://pyautogui.readthedocs.io/en/latest/install.html"
    import AppKit

    def _macPosition():
        loc = AppKit.NSEvent.mouseLocation()
        return int(loc.x), int(Quartz.CGDisplayPixelsHigh(0) - loc.y)
    position = _macPosition


    def _macScreenshot():
        tmpFilename = 'screenshot%s.png' % (datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))
        subprocess.call(['screencapture', '-x', tmpFilename])
        im = Image.open(tmpFilename)

        # force loading before unlinking, Image.open() is lazy
        im.load()

        os.unlink(tmpFilename)
        return im
    screenshot = _macScreenshot

    def _macSize():
        return Quartz.CGDisplayPixelsWide(Quartz.CGMainDisplayID()), Quartz.CGDisplayPixelsHigh(Quartz.CGMainDisplayID())
    size = _macSize

elif platform.system() == 'Linux':
    from Xlib.display import Display
    import errno

    scrotExists = False
    try:
            whichProc = subprocess.Popen(
                ['which', 'scrot'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            scrotExists = whichProc.wait() == 0
    except OSError as ex:
        if ex.errno == errno.ENOENT:
            # if there is no "which" program to find scrot, then assume there
            # is no scrot.
            pass
        else:
            raise

    _display = Display(os.environ['DISPLAY'])

    def _linuxPosition():
        coord = _display.screen().root.query_pointer()._data
        return coord["root_x"], coord["root_y"]
    position = _linuxPosition

    def _linuxScreenshot():
        if not scrotExists:
            raise NotImplementedError('"scrot" must be installed to use screenshot functions in Linux. Run: sudo apt-get install scrot')

        tmpFilename = '.screenshot%s.png' % (datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))

        if scrotExists:
            subprocess.call(['scrot', tmpFilename])
            im = Image.open(tmpFilename)

            # force loading before unlinking, Image.open() is lazy
            im.load()

            os.unlink(tmpFilename)
            return im
        else:
            raise Exception('The scrot program must be installed to take a screenshot with PyScreeze on Linux. Run: sudo apt-get install scrot')
    screenshot = _linuxScreenshot

    def _linuxSize():
        return _display.screen().width_in_pixels, _display.screen().height_in_pixels
    size = _linuxSize
# =========================================================================

import sys, pyperclip
RUNNING_PYTHON_2 = sys.version_info[0] == 2

if RUNNING_PYTHON_2:
    import Tkinter as tkinter
    #from Tkinter import Tk as ttk
    ttk = tkinter
else:
    import tkinter
    from tkinter import ttk

MOUSE_INFO_BUTTON_WIDTH = 14 # A standard width for the buttons in the Mouse Info window.

# While G_MOUSE_INFO_RUNNING is True, the text fields in the Mouse Info
# window will be updated:
G_MOUSE_INFO_RUNNING = False

def _updateMouseInfoTextFields():
    # Update the XY and RGB text fields in the Mouse Info window.

    # Get the XY coordinates of the current mouse position:
    x, y = position()
    G_MOUSE_INFO_XY_INFO.set('%s,%s' % (x, y))

    # Mouse Info currently only works on the primary monitor, and doesn't
    # support multi-monitor setups. The color information isn't reliable
    # when the mouse is not on the primary monitor, so display an error instead.
    width, height = size()
    if not (0 <= x < width and 0 <= y < height):
        G_MOUSE_INFO_RGB_INFO.set('NA_on_multimonitor_setups')
    else:
        # Get the RGB color value of the pixel currently under the mouse:
        r, g, b = screenshot().getpixel((x, y))
        G_MOUSE_INFO_RGB_INFO.set('%s,%s,%s' % (r, g, b))

    if not (0 <= x < width and 0 <= y < height):
        G_MOUSE_INFO_RGB_HEX_INFO.set('NA_on_multimonitor_setups')
    else:
        # Convert this RGB value into a hex RGB value:
        rHex = hex(r)[2:].upper().rjust(2, '0')
        gHex = hex(g)[2:].upper().rjust(2, '0')
        bHex = hex(b)[2:].upper().rjust(2, '0')
        hexColor = '#%s%s%s' % (rHex, gHex, bHex)
        G_MOUSE_INFO_RGB_HEX_INFO.set(hexColor)

    if not (0 <= x < width and 0 <= y < height):
        G_MOUSE_INFO_COLOR_FRAME.configure(background='black')
    else:
        # Update the color panel:
        G_MOUSE_INFO_COLOR_FRAME.configure(background=hexColor)

    # As long as the global G_MOUSE_INFO_RUNNING variable is True,
    # schedule this function to be called again in 20 milliseconds.
    # NOTE: Previously this if-else code was at the top of the function
    # so that I could avoid the "invalid command name" message that
    # was popping up (this didn't work though), but it was also causing
    # a weird bug where the text fields weren't populated until I moved
    # the tkinter window. I have no idea why that behavior was happening.
    # You can reproduce it by moving this if-else code to the top of this
    # function.
    if G_MOUSE_INFO_RUNNING:
        G_MOUSE_INFO_ROOT.after(20, _updateMouseInfoTextFields)
    else:
        return # Mouse Info window has been closed, so return immediately.


def _copyXyMouseInfo(*args):
    # Copy the contents of the XY coordinate text field in the Mouse Info
    # window to the clipboard.
    pyperclip.copy(G_MOUSE_INFO_XY_INFO.get())


def _copyRgbMouseInfo(*args):
    # Copy the contents of the RGB color text field in the Mouse Info
    # window to the clipboard.
    pyperclip.copy(G_MOUSE_INFO_RGB_INFO.get())


def _copyRgbHexMouseInfo(*args):
    # Copy the contents of the RGB hex color text field in the Mouse Info
    # window to the clipboard.
    pyperclip.copy(G_MOUSE_INFO_RGB_HEX_INFO.get())


def _copyAllMouseInfo(*args):
    # Copy the contents of the XY coordinate and RGB color text fields in the
    # Mouse Info window to the log text field.
    textFieldContents = '%s %s %s' % (G_MOUSE_INFO_XY_INFO.get(),
                                      G_MOUSE_INFO_RGB_INFO.get(),
                                      G_MOUSE_INFO_RGB_HEX_INFO.get())
    pyperclip.copy(textFieldContents)

def _logXyMouseInfo(*args):
    # Log the contents of the XY coordinate text field in the Mouse Info
    # window to the log text field.
    pass


def _logRgbMouseInfo(*args):
    # Log the contents of the RGB color text field in the Mouse Info
    # window to the log text field.
    pass


def _logRgbHexMouseInfo(*args):
    # Log the contents of the RGB hex color text field in the Mouse Info
    # window to the log text field.
    pass


def _logAllMouseInfo(*args):
    # Log the contents of the XY coordinate and RGB color text fields in the
    # Mouse Info window to the log text field.
    textFieldContents = '%s %s %s' % (G_MOUSE_INFO_XY_INFO.get(),
                                  G_MOUSE_INFO_RGB_INFO.get(),
                                  G_MOUSE_INFO_RGB_HEX_INFO.get())



def mouseInfo():
    """Launches the Mouse Info window, which displays XY coordinate and RGB
    color information for the mouse's current position.

    Returns None.

    Technical note: This function is not thread-safe and uses global variables.
    It's meant to be called once at a time."""

    global G_MOUSE_INFO_RUNNING, G_MOUSE_INFO_ROOT, G_MOUSE_INFO_XY_INFO, G_MOUSE_INFO_RGB_INFO, G_MOUSE_INFO_RGB_HEX_INFO, G_MOUSE_INFO_COLOR_FRAME

    G_MOUSE_INFO_RUNNING = True # While True, the text fields will update.

    # Create the Mouse Info window:
    G_MOUSE_INFO_ROOT = tkinter.Tk()
    G_MOUSE_INFO_ROOT.title("Mouse Info")
    G_MOUSE_INFO_ROOT.minsize(400, 100)

    # Create the main frame in the Mouse Info window:
    if RUNNING_PYTHON_2:
        mainframe = tkinter.Frame(G_MOUSE_INFO_ROOT)
    else:
        mainframe = ttk.Frame(G_MOUSE_INFO_ROOT, padding='3 3 12 12')

    # Set up the grid for the Mouse Info window's widgets:
    mainframe.grid(column=0, row=0, sticky=(tkinter.N, tkinter.W, tkinter.E, tkinter.S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    # Set up the instructional text label:
    ttk.Label(mainframe, text="(TODO instructional\ntext here)").grid(column=1, row=1, sticky=tkinter.W)

    # Set up the button to copy the XY coordinates to the clipboard:
    xyCopyButton = ttk.Button(mainframe, text="Copy All", width=MOUSE_INFO_BUTTON_WIDTH, command=_copyAllMouseInfo)
    xyCopyButton.grid(column=3, row=1, sticky=tkinter.W)
    xyCopyButton.bind('<Return>', _copyAllMouseInfo)

    # Set up the button to copy the XY coordinates to the clipboard:
    xyCopyButton = ttk.Button(mainframe, text="Log All", width=MOUSE_INFO_BUTTON_WIDTH, command=_logAllMouseInfo)
    xyCopyButton.grid(column=4, row=1, sticky=tkinter.W)
    xyCopyButton.bind('<Return>', _logAllMouseInfo)

    # Set up the variables for the content of the Mouse Info window's text fields:
    G_MOUSE_INFO_XY_INFO = tkinter.StringVar()
    G_MOUSE_INFO_RGB_INFO = tkinter.StringVar()
    G_MOUSE_INFO_RGB_HEX_INFO = tkinter.StringVar()

    # Set up the XY coordinate text field and label:
    G_MOUSE_INFO_XY_INFO_entry = ttk.Entry(mainframe, width=16, textvariable=G_MOUSE_INFO_XY_INFO)
    G_MOUSE_INFO_XY_INFO_entry.grid(column=2, row=2, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text="XY Position").grid(column=1, row=2, sticky=tkinter.W)

    # Set up the button to copy the XY coordinates to the clipboard:
    xyCopyButton = ttk.Button(mainframe, text="Copy XY", width=MOUSE_INFO_BUTTON_WIDTH, command=_copyXyMouseInfo)
    xyCopyButton.grid(column=3, row=2, sticky=tkinter.W)
    xyCopyButton.bind('<Return>', _copyXyMouseInfo)

    # Set up the button to log the XY coordinates:
    xyLogButton = ttk.Button(mainframe, text="Log XY", width=MOUSE_INFO_BUTTON_WIDTH, command=_logXyMouseInfo)
    xyLogButton.grid(column=4, row=2, sticky=tkinter.W)
    xyLogButton.bind('<Return>', _logXyMouseInfo)

    # Set up the RGB color text field and label:
    G_MOUSE_INFO_RGB_INFO_entry = ttk.Entry(mainframe, width=16, textvariable=G_MOUSE_INFO_RGB_INFO)
    G_MOUSE_INFO_RGB_INFO_entry.grid(column=2, row=3, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text="RGB Color").grid(column=1, row=3, sticky=tkinter.W)

    # Set up the button to copy the RGB color to the clipboard:
    rgbCopyButton = ttk.Button(mainframe, text="Copy RGB", width=MOUSE_INFO_BUTTON_WIDTH, command=_copyRgbMouseInfo)
    rgbCopyButton.grid(column=3, row=3, sticky=tkinter.W)
    rgbCopyButton.bind('<Return>', _copyRgbMouseInfo)

    # Set up the button to log the XY coordinates:
    rgbLogButton = ttk.Button(mainframe, text="Log RGB", width=MOUSE_INFO_BUTTON_WIDTH, command=_logRgbMouseInfo)
    rgbLogButton.grid(column=4, row=3, sticky=tkinter.W)
    rgbLogButton.bind('<Return>', _logRgbMouseInfo)

    # Set up the RGB hex color text field and label:
    G_MOUSE_INFO_RGB_HEX_INFO_entry = ttk.Entry(mainframe, width=16, textvariable=G_MOUSE_INFO_RGB_HEX_INFO)
    G_MOUSE_INFO_RGB_HEX_INFO_entry.grid(column=2, row=4, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text="RGB As Hex").grid(column=1, row=4, sticky=tkinter.W)

    # Set up the button to copy the RGB hex color to the clipboard:
    rgbHexCopyButton = ttk.Button(mainframe, text="Copy RGB Hex", width=MOUSE_INFO_BUTTON_WIDTH, command=_copyRgbHexMouseInfo)
    rgbHexCopyButton.grid(column=3, row=4, sticky=tkinter.W)
    rgbHexCopyButton.bind('<Return>', _copyRgbHexMouseInfo)

    # Set up the button to log the XY coordinates:
    rgbHexLogButton = ttk.Button(mainframe, text="Log RGB Hex", width=MOUSE_INFO_BUTTON_WIDTH, command=_logRgbHexMouseInfo)
    rgbHexLogButton.grid(column=4, row=4, sticky=tkinter.W)
    rgbHexLogButton.bind('<Return>', _logRgbHexMouseInfo)

    # Set up the frame that displays the color of the pixel currently under the mouse cursor:
    G_MOUSE_INFO_COLOR_FRAME = tkinter.Frame(mainframe, width=50, height = 50)
    G_MOUSE_INFO_COLOR_FRAME.grid(column=2, row=5, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text="Color").grid(column=1, row=5, sticky=tkinter.W)

    # Add padding to all of the widgets:
    for child in mainframe.winfo_children():
        child.grid_configure(padx=3, pady=3)

    G_MOUSE_INFO_XY_INFO_entry.focus() # Put the focus on the XY coordinate text field to start.

    G_MOUSE_INFO_ROOT.after(100, _updateMouseInfoTextFields) # Begin updating the text fields.

    # Make the mouse info window "always on top".
    G_MOUSE_INFO_ROOT.attributes('-topmost', True)
    G_MOUSE_INFO_ROOT.update()

    # Start the application:
    G_MOUSE_INFO_ROOT.mainloop()

    # Application has closed, set this to False:
    G_MOUSE_INFO_RUNNING = False

    # Destroy the tkinter root widget:
    try:
        G_MOUSE_INFO_ROOT.destroy()
    except tkinter.TclError:
        pass

if __name__ == '__main__':
    mouseInfo()
