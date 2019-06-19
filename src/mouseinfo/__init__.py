# Mouse Info by Al Sweigart al@inventwithpython.com

__version__ = '0.0.1'


# =========================================================================
# This code make this application dependent on PyAutoGUI being installed:
#from pyautogui import position, screenshot
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

# While G_MOUSE_INFO_RUNNING is True, the text fields in the Mouse Info
# window will be updated:
G_MOUSE_INFO_RUNNING = False

def _updateMouseInfoTextFields():
    # Update the XY and RGB text fields in the Mouse Info window.

    # As long as the global G_MOUSE_INFO_RUNNING variable is True,
    # schedule this function to be called again in 20 milliseconds.
    if G_MOUSE_INFO_RUNNING:
        G_MOUSE_INFO_ROOT.after(20, _updateMouseInfoTextFields)
    else:
        return # Mouse Info window has been closed, so return immediately.

    # Get the XY coordinates of the current mouse position:
    x, y = position()
    G_MOUSE_INFO_XY_INFO.set('%s, %s' % (x, y))

    # Get the RGB color value of the pixel currently undr the mouse:
    r, g, b = screenshot().getpixel((x, y))
    G_MOUSE_INFO_RGB_INFO.set('%s, %s, %s' % (r, g, b))

    # Convert this RGB value into a hex RGB value:
    rHex = hex(r)[2:].upper().rjust(2, '0')
    gHex = hex(g)[2:].upper().rjust(2, '0')
    bHex = hex(b)[2:].upper().rjust(2, '0')
    hexColor = '#%s%s%s' % (rHex, gHex, bHex)
    G_MOUSE_INFO_RGB_HEX_INFO.set(hexColor)

    # Update the color panel:
    G_MOUSE_INFO_COLOR_FRAME.configure(background=hexColor)


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

    # Set up the variables for the content of the Mouse Info window's text fields:
    G_MOUSE_INFO_XY_INFO = tkinter.StringVar()
    G_MOUSE_INFO_RGB_INFO = tkinter.StringVar()
    G_MOUSE_INFO_RGB_HEX_INFO = tkinter.StringVar()

    # Set up the XY coordinate text field and label:
    G_MOUSE_INFO_XY_INFO_entry = ttk.Entry(mainframe, width=16, textvariable=G_MOUSE_INFO_XY_INFO)
    G_MOUSE_INFO_XY_INFO_entry.grid(column=2, row=1, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text="XY Position").grid(column=1, row=1, sticky=tkinter.W)

    # Set up the button to copy the XY coordinates to the clipboard:
    xyButton = ttk.Button(mainframe, text="Copy XY", width=14, command=_copyXyMouseInfo)
    xyButton.grid(column=3, row=1, sticky=tkinter.W)
    xyButton.bind('<Return>', _copyXyMouseInfo)

    # Set up the RGB color text field and label:
    G_MOUSE_INFO_RGB_INFO_entry = ttk.Entry(mainframe, width=16, textvariable=G_MOUSE_INFO_RGB_INFO)
    G_MOUSE_INFO_RGB_INFO_entry.grid(column=2, row=2, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text="RGB Color").grid(column=1, row=2, sticky=tkinter.W)

    # Set up the button to copy the RGB color to the clipboard:
    rgbButton = ttk.Button(mainframe, text="Copy RGB", width=14, command=_copyRgbMouseInfo)
    rgbButton.grid(column=3, row=2, sticky=tkinter.W)
    rgbButton.bind('<Return>', _copyRgbMouseInfo)

    # Set up the RGB hex color text field and label:
    G_MOUSE_INFO_RGB_HEX_INFO_entry = ttk.Entry(mainframe, width=16, textvariable=G_MOUSE_INFO_RGB_HEX_INFO)
    G_MOUSE_INFO_RGB_HEX_INFO_entry.grid(column=2, row=3, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text="RGB As Hex").grid(column=1, row=3, sticky=tkinter.W)

    # Set up the button to copy the RGB hex color to the clipboard:
    rgbHexButton = ttk.Button(mainframe, text="Copy RGB Hex", width=14, command=_copyRgbHexMouseInfo)
    rgbHexButton.grid(column=3, row=3, sticky=tkinter.W)
    rgbHexButton.bind('<Return>', _copyRgbHexMouseInfo)

    # Set up the frame that displays the color of the pixel currently under the mouse cursor:
    G_MOUSE_INFO_COLOR_FRAME = tkinter.Frame(mainframe, width=50, height = 50)
    G_MOUSE_INFO_COLOR_FRAME.grid(column=2, row=4, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text="Color").grid(column=1, row=4, sticky=tkinter.W)

    # Add padding to all of the widgets:
    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)

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
