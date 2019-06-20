# Mouse Info by Al Sweigart al@inventwithpython.com

# Note: how to specify where a tkintr window opens:
# https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens

__version__ = '0.0.1'
import pyperclip, sys, os, platform

# =========================================================================
# Originally, these functions were pulled in from PyAutoGUI. However, to
# make this module independent of PyAutoGUI, the code for these functions
# has been copy/pasted into the following section:
# NOTE: Any bug fixes for these functions in PyAutoGUI will have to be
# manually merged into MouseInfo.
#from pyautogui import position, screenshot, size
# =========================================================================
# Alternatively, this code makes this application not dependent on PyAutoGUI
# by copying the code for the position() and screenshot() functions into this
# source code file.
import datetime, subprocess
from PIL import Image

if sys.platform == 'win32':
    import ctypes
    from PIL import ImageGrab

    # Fixes the scaling issues where PyAutoGUI was reporting the wrong resolution:
    try:
       ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass # Windows XP doesn't support this, so just do nothing.


    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long),
                    ("y", ctypes.c_long)]

    def _winPosition():
        cursor = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
        return (cursor.x, cursor.y)
    position = _winPosition


    def _winScreenshot(filename=None):
        # TODO - Use the winapi to get a screenshot, and compare performance with ImageGrab.grab()
        # https://stackoverflow.com/a/3586280/1893164
        try:
            im = ImageGrab.grab()
            if filename is not None:
                im.save(filename)
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


    def _macScreenshot(filename=None):
        if filename is not None:
            tmpFilename = filename
        else:
            tmpFilename = 'screenshot%s.png' % (datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))
        subprocess.call(['screencapture', '-x', tmpFilename])
        im = Image.open(tmpFilename)

        # force loading before unlinking, Image.open() is lazy
        im.load()

        if filename is None:
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

    def _linuxScreenshot(filename=None):
        if not scrotExists:
            raise NotImplementedError('"scrot" must be installed to use screenshot functions in Linux. Run: sudo apt-get install scrot')

        if filename is not None:
            tmpFilename = filename
        else:
            tmpFilename = '.screenshot%s.png' % (datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))

        if scrotExists:
            subprocess.call(['scrot', tmpFilename])
            im = Image.open(tmpFilename)

            # force loading before unlinking, Image.open() is lazy
            im.load()

            if filename is None:
                os.unlink(tmpFilename)
            return im
        else:
            raise Exception('The scrot program must be installed to take a screenshot with PyScreeze on Linux. Run: sudo apt-get install scrot')
    screenshot = _linuxScreenshot

    def _linuxSize():
        return _display.screen().width_in_pixels, _display.screen().height_in_pixels
    size = _linuxSize
# =========================================================================

RUNNING_PYTHON_2 = sys.version_info[0] == 2

if platform.system() == 'Linux':
    if RUNNING_PYTHON_2:
        try:
            import Tkinter as tkinter
            ttk = tkinter
        except ImportError:
            sys.exit('NOTE: You must install tkinter on Linux to use Mouse Info. Run the following: sudo apt-get install python-tk python-dev')
    else:
        # Running Python 3+:
        try:
            import tkinter
            from tkinter import ttk
        except ImportError:
            sys.exit('NOTE: You must install tkinter on Linux to use Mouse Info. Run the following: sudo apt-get install python3-tk python3-dev')
else:
    # Running Windows or macOS:
    if RUNNING_PYTHON_2:
        import Tkinter as tkinter
        ttk = tkinter
    else:
        # Running Python 3+:
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
    if sys.platform == 'darwin':
        # TODO - Until I can get screenshots without the mouse cursor, this feature doesn't work on mac.
        G_MOUSE_INFO_RGB_INFO.set('NA_on_macOS')
    elif not (0 <= x < width and 0 <= y < height):
        G_MOUSE_INFO_RGB_INFO.set('NA_on_multimonitor_setups')
    else:
        # Get the RGB color value of the pixel currently under the mouse:
        # NOTE: On Windows & Linux, getpixel() returns a 3-integer tuple, but on macOS it returns a 4-integer tuple.
        rgbValue = screenshot().getpixel((x, y))
        r, g, b, = rgbValue[0], rgbValue[1], rgbValue[2]
        G_MOUSE_INFO_RGB_INFO.set('%s,%s,%s' % (r, g, b))

    if sys.platform == 'darwin':
        # TODO - Until I can get screenshots without the mouse cursor, this feature doesn't work on mac.
        G_MOUSE_INFO_RGB_HEX_INFO.set('NA_on_macOS')
    elif not (0 <= x < width and 0 <= y < height):
        G_MOUSE_INFO_RGB_HEX_INFO.set('NA_on_multimonitor_setups')
    else:
        # Convert this RGB value into a hex RGB value:
        rHex = hex(r)[2:].upper().rjust(2, '0')
        gHex = hex(g)[2:].upper().rjust(2, '0')
        bHex = hex(b)[2:].upper().rjust(2, '0')
        hexColor = '#%s%s%s' % (rHex, gHex, bHex)
        G_MOUSE_INFO_RGB_HEX_INFO.set(hexColor)

    if (sys.platform == 'darwin') or (not (0 <= x < width and 0 <= y < height)):
        G_MOUSE_INFO_COLOR_FRAME.configure(background='black')
    else:
        # Update the color panel:
        G_MOUSE_INFO_COLOR_FRAME.configure(background=hexColor)

    # As long as the global G_MOUSE_INFO_RUNNING variable is True,
    # schedule this function to be called again in 100 milliseconds.
    # NOTE: Previously this if-else code was at the top of the function
    # so that I could avoid the "invalid command name" message that
    # was popping up (this didn't work though), but it was also causing
    # a weird bug where the text fields weren't populated until I moved
    # the tkinter window. I have no idea why that behavior was happening.
    # You can reproduce it by moving this if-else code to the top of this
    # function.
    if G_MOUSE_INFO_RUNNING:
        G_MOUSE_INFO_ROOT.after(100, _updateMouseInfoTextFields)
    else:
        return # Mouse Info window has been closed, so return immediately.


def _copyText(textToCopy):
    try:
        pyperclip.copy(textToCopy)
        G_MOUSE_INFO_STATUSBAR_INFO.set('Copied ' + textToCopy)
    except pyperclip.PyperclipException as e:
        if platform.system() == 'Linux':
            G_MOUSE_INFO_STATUSBAR_INFO.set('Copy failed. Run "sudo apt-get install xsel".')
        else:
            G_MOUSE_INFO_STATUSBAR_INFO.set('Clipboard error: ' + str(e))


def _copyXyMouseInfo(*args):
    # Copy the contents of the XY coordinate text field in the Mouse Info
    # window to the clipboard.
    _copyText(G_MOUSE_INFO_XY_INFO.get())


def _copyRgbMouseInfo(*args):
    # Copy the contents of the RGB color text field in the Mouse Info
    # window to the clipboard.
    _copyText(G_MOUSE_INFO_RGB_INFO.get())


def _copyRgbHexMouseInfo(*args):
    # Copy the contents of the RGB hex color text field in the Mouse Info
    # window to the clipboard.
    _copyText(G_MOUSE_INFO_RGB_HEX_INFO.get())


def _copyAllMouseInfo(*args):
    # Copy the contents of the XY coordinate and RGB color text fields in the
    # Mouse Info window to the log text field.
    textFieldContents = '%s %s %s' % (G_MOUSE_INFO_XY_INFO.get(),
                                      G_MOUSE_INFO_RGB_INFO.get(),
                                      G_MOUSE_INFO_RGB_HEX_INFO.get())
    _copyText(textFieldContents)


def _logXyMouseInfo(*args):
    # Log the contents of the XY coordinate text field in the Mouse Info
    # window to the log text field.
    logContents = G_MOUSE_INFO_LOG_INFO.get() + '%s\n' % (G_MOUSE_INFO_XY_INFO.get())
    G_MOUSE_INFO_LOG_INFO.set(logContents)
    _setLogTextAreaContents(logContents)
    G_MOUSE_INFO_STATUSBAR_INFO.set('Logged ' + G_MOUSE_INFO_XY_INFO.get())


def _logRgbMouseInfo(*args):
    # Log the contents of the RGB color text field in the Mouse Info
    # window to the log text field.
    logContents = G_MOUSE_INFO_LOG_INFO.get() + '%s\n' % (G_MOUSE_INFO_RGB_INFO.get())
    G_MOUSE_INFO_LOG_INFO.set(logContents)
    _setLogTextAreaContents(logContents)
    G_MOUSE_INFO_STATUSBAR_INFO.set('Logged ' + G_MOUSE_INFO_RGB_INFO.get())


def _logRgbHexMouseInfo(*args):
    # Log the contents of the RGB hex color text field in the Mouse Info
    # window to the log text field.
    logContents = G_MOUSE_INFO_LOG_INFO.get() + '%s\n' % (G_MOUSE_INFO_RGB_HEX_INFO.get())
    G_MOUSE_INFO_LOG_INFO.set(logContents)
    _setLogTextAreaContents(logContents)
    G_MOUSE_INFO_STATUSBAR_INFO.set('Logged ' + G_MOUSE_INFO_RGB_HEX_INFO.get())


def _logAllMouseInfo(*args):
    # Log the contents of the XY coordinate and RGB color text fields in the
    # Mouse Info window to the log text field.
    textFieldContents = '%s %s %s' % (G_MOUSE_INFO_XY_INFO.get(),
                                      G_MOUSE_INFO_RGB_INFO.get(),
                                      G_MOUSE_INFO_RGB_HEX_INFO.get())
    logContents = G_MOUSE_INFO_LOG_INFO.get() + '%s\n' % (textFieldContents)
    G_MOUSE_INFO_LOG_INFO.set(logContents)
    _setLogTextAreaContents(logContents)
    G_MOUSE_INFO_STATUSBAR_INFO.set('Logged ' + textFieldContents)


def _setLogTextAreaContents(logContents):
    if RUNNING_PYTHON_2:
        G_MOUSE_INFO_LOG_TEXT_AREA.delete('1.0', tkinter.END)
        G_MOUSE_INFO_LOG_TEXT_AREA.insert(tkinter.END, logContents)
    else:
        G_MOUSE_INFO_LOG_TEXT_AREA.replace('1.0', tkinter.END, logContents)

    # Scroll to the bottom of the text area:
    topOfTextArea, bottomOfTextArea = G_MOUSE_INFO_LOG_TEXT_AREA.yview()
    G_MOUSE_INFO_LOG_TEXT_AREA.yview_moveto(bottomOfTextArea)


def _saveLogFile(*args):
    # Save the current contents of the log file text field. Automatically
    # overwrites the file if it exists. Displays an error message in the
    # status bar if there is a problem.
    try:
        with open(G_MOUSE_INFO_LOG_FILENAME_INFO.get(), 'w') as fo:
            fo.write(G_MOUSE_INFO_LOG_INFO.get())
    except Exception as e:
        G_MOUSE_INFO_STATUSBAR_INFO.set('ERROR: ' + str(e))
    else:
        G_MOUSE_INFO_STATUSBAR_INFO.set('Log file saved to ' + G_MOUSE_INFO_LOG_FILENAME_INFO.get())


def _saveScreenshotFile(*args):
    # Saves a screenshot. Automatically overwrites the file if it exists.
    # Displays an error message in the status bar if there is a problem.
    try:
        screenshot(G_MOUSE_INFO_SCREENSHOT_FILENAME_INFO.get())
    except Exception as e:
        G_MOUSE_INFO_STATUSBAR_INFO.set('ERROR: ' + str(e))
    else:
        G_MOUSE_INFO_STATUSBAR_INFO.set('Screenshot file saved to ' + G_MOUSE_INFO_SCREENSHOT_FILENAME_INFO.get())


def mouseInfo():
    """Launches the Mouse Info window, which displays XY coordinate and RGB
    color information for the mouse's current position.

    Returns None.

    Technical note: This function is not thread-safe and uses global variables.
    It's meant to be called once at a time."""

    # TODO - we use too many globals, convert this program to use OOP.
    global G_MOUSE_INFO_RUNNING, G_MOUSE_INFO_ROOT, G_MOUSE_INFO_XY_INFO, G_MOUSE_INFO_RGB_INFO, G_MOUSE_INFO_RGB_HEX_INFO, G_MOUSE_INFO_COLOR_FRAME, G_MOUSE_INFO_LOG_TEXT_AREA, G_MOUSE_INFO_LOG_INFO, G_MOUSE_INFO_LOG_FILENAME_INFO, G_MOUSE_INFO_SCREENSHOT_FILENAME_INFO, G_MOUSE_INFO_STATUSBAR_INFO

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

    # WIDGETS ON ROW 1:

    # Set up the instructional text label:
    ttk.Label(mainframe, text='Tab over the buttons and press Enter to\n"click" them as you move the mouse around.').grid(column=1, row=1, columnspan=2, sticky=tkinter.W)

    # Set up the button to copy the XY coordinates to the clipboard:
    xyCopyButton = ttk.Button(mainframe, text='Copy All', width=MOUSE_INFO_BUTTON_WIDTH, command=_copyAllMouseInfo)
    xyCopyButton.grid(column=3, row=1, sticky=tkinter.W)
    xyCopyButton.bind('<Return>', _copyAllMouseInfo)

    # Set up the button to copy the XY coordinates to the clipboard:
    xyCopyButton = ttk.Button(mainframe, text='Log All', width=MOUSE_INFO_BUTTON_WIDTH, command=_logAllMouseInfo)
    xyCopyButton.grid(column=4, row=1, sticky=tkinter.W)
    xyCopyButton.bind('<Return>', _logAllMouseInfo)

    # Set up the variables for the content of the Mouse Info window's text fields:
    G_MOUSE_INFO_XY_INFO                  = tkinter.StringVar() # The str contents of the xy text field.
    G_MOUSE_INFO_RGB_INFO                 = tkinter.StringVar() # The str contents of the rgb text field.
    G_MOUSE_INFO_RGB_HEX_INFO             = tkinter.StringVar() # The str contents of the rgb hex text field.
    G_MOUSE_INFO_LOG_INFO                 = tkinter.StringVar() # The str contents of the log text area.
    G_MOUSE_INFO_LOG_FILENAME_INFO        = tkinter.StringVar() # The str contents of the log filename text field.
    G_MOUSE_INFO_SCREENSHOT_FILENAME_INFO = tkinter.StringVar() # The str contents of the screenshot filename text field.
    G_MOUSE_INFO_STATUSBAR_INFO           = tkinter.StringVar() # The str contents of the status bar at the bottom of the window.

    # WIDGETS ON ROW 2:

    # Set up the XY coordinate text field and label:
    G_MOUSE_INFO_XY_INFO_entry = ttk.Entry(mainframe, width=16, textvariable=G_MOUSE_INFO_XY_INFO)
    G_MOUSE_INFO_XY_INFO_entry.grid(column=2, row=2, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text='XY Position').grid(column=1, row=2, sticky=tkinter.W)

    # Set up the button to copy the XY coordinates to the clipboard:
    xyCopyButton = ttk.Button(mainframe, text='Copy XY', width=MOUSE_INFO_BUTTON_WIDTH, command=_copyXyMouseInfo)
    xyCopyButton.grid(column=3, row=2, sticky=tkinter.W)
    xyCopyButton.bind('<Return>', _copyXyMouseInfo)

    # Set up the button to log the XY coordinates:
    xyLogButton = ttk.Button(mainframe, text='Log XY', width=MOUSE_INFO_BUTTON_WIDTH, command=_logXyMouseInfo)
    xyLogButton.grid(column=4, row=2, sticky=tkinter.W)
    xyLogButton.bind('<Return>', _logXyMouseInfo)

    # WIDGETS ON ROW 3:

    # Set up the RGB color text field and label:
    G_MOUSE_INFO_RGB_INFO_entry = ttk.Entry(mainframe, width=16, textvariable=G_MOUSE_INFO_RGB_INFO)
    G_MOUSE_INFO_RGB_INFO_entry.grid(column=2, row=3, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text='RGB Color').grid(column=1, row=3, sticky=tkinter.W)

    # Set up the button to copy the RGB color to the clipboard:
    rgbCopyButton = ttk.Button(mainframe, text='Copy RGB', width=MOUSE_INFO_BUTTON_WIDTH, command=_copyRgbMouseInfo)
    rgbCopyButton.grid(column=3, row=3, sticky=tkinter.W)
    rgbCopyButton.bind('<Return>', _copyRgbMouseInfo)

    # Set up the button to log the XY coordinates:
    rgbLogButton = ttk.Button(mainframe, text='Log RGB', width=MOUSE_INFO_BUTTON_WIDTH, command=_logRgbMouseInfo)
    rgbLogButton.grid(column=4, row=3, sticky=tkinter.W)
    rgbLogButton.bind('<Return>', _logRgbMouseInfo)

    # WIDGETS ON ROW 4:

    # Set up the RGB hex color text field and label:
    G_MOUSE_INFO_RGB_HEX_INFO_entry = ttk.Entry(mainframe, width=16, textvariable=G_MOUSE_INFO_RGB_HEX_INFO)
    G_MOUSE_INFO_RGB_HEX_INFO_entry.grid(column=2, row=4, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text='RGB As Hex').grid(column=1, row=4, sticky=tkinter.W)

    # Set up the button to copy the RGB hex color to the clipboard:
    rgbHexCopyButton = ttk.Button(mainframe, text='Copy RGB Hex', width=MOUSE_INFO_BUTTON_WIDTH, command=_copyRgbHexMouseInfo)
    rgbHexCopyButton.grid(column=3, row=4, sticky=tkinter.W)
    rgbHexCopyButton.bind('<Return>', _copyRgbHexMouseInfo)

    # Set up the button to log the XY coordinates:
    rgbHexLogButton = ttk.Button(mainframe, text='Log RGB Hex', width=MOUSE_INFO_BUTTON_WIDTH, command=_logRgbHexMouseInfo)
    rgbHexLogButton.grid(column=4, row=4, sticky=tkinter.W)
    rgbHexLogButton.bind('<Return>', _logRgbHexMouseInfo)

    # WIDGETS ON ROW 5:

    # Set up the frame that displays the color of the pixel currently under the mouse cursor:
    G_MOUSE_INFO_COLOR_FRAME = tkinter.Frame(mainframe, width=50, height=50)
    G_MOUSE_INFO_COLOR_FRAME.grid(column=2, row=5, sticky=(tkinter.W, tkinter.E))
    ttk.Label(mainframe, text='Color').grid(column=1, row=5, sticky=tkinter.W)

    # WIDGETS ON ROW 6:

    # Set up the multiline text widget where the log info appears:
    G_MOUSE_INFO_LOG_TEXT_AREA = tkinter.Text(mainframe, width=20, height=6)
    G_MOUSE_INFO_LOG_TEXT_AREA.grid(column=1, row=6, columnspan=4, sticky=(tkinter.W, tkinter.E, tkinter.N, tkinter.S))
    G_MOUSE_INFO_LOG_TEXT_AREA_SCROLLBAR = ttk.Scrollbar(mainframe, orient=tkinter.VERTICAL, command=G_MOUSE_INFO_LOG_TEXT_AREA.yview)
    G_MOUSE_INFO_LOG_TEXT_AREA_SCROLLBAR.grid(column=5, row=6, sticky=(tkinter.N, tkinter.S))
    G_MOUSE_INFO_LOG_TEXT_AREA['yscrollcommand'] = G_MOUSE_INFO_LOG_TEXT_AREA_SCROLLBAR.set

    # WIDGETS ON ROW 7:
    G_MOUSE_INFO_LOG_FILENAME_entry = ttk.Entry(mainframe, width=16, textvariable=G_MOUSE_INFO_LOG_FILENAME_INFO)
    G_MOUSE_INFO_LOG_FILENAME_entry.grid(column=1, row=7, columnspan=3, sticky=(tkinter.W, tkinter.E))
    saveLogButton = ttk.Button(mainframe, text='Save Log', width=MOUSE_INFO_BUTTON_WIDTH, command=_saveLogFile)
    saveLogButton.grid(column=4, row=7, sticky=tkinter.W)
    saveLogButton.bind('<Return>', _saveLogFile)
    G_MOUSE_INFO_LOG_FILENAME_INFO.set(os.path.join(os.getcwd(), 'mouseInfoLog.txt'))

    # WIDGETS ON ROW 8:
    G_MOUSE_INFO_SCREENSHOT_FILENAME_entry = ttk.Entry(mainframe, width=16, textvariable=G_MOUSE_INFO_SCREENSHOT_FILENAME_INFO)
    G_MOUSE_INFO_SCREENSHOT_FILENAME_entry.grid(column=1, row=8, columnspan=3, sticky=(tkinter.W, tkinter.E))
    saveScreenshotButton = ttk.Button(mainframe, text='Save Screenshot', width=MOUSE_INFO_BUTTON_WIDTH, command=_saveScreenshotFile)
    saveScreenshotButton.grid(column=4, row=8, sticky=tkinter.W)
    saveScreenshotButton.bind('<Return>', _saveScreenshotFile)
    G_MOUSE_INFO_SCREENSHOT_FILENAME_INFO.set(os.path.join(os.getcwd(), 'mouseInfoScreenshot.png'))

    # WIDGETS ON ROW 9:
    G_MOUSE_INFO_STATUSBAR = ttk.Label(mainframe, relief=tkinter.SUNKEN, textvariable=G_MOUSE_INFO_STATUSBAR_INFO)
    G_MOUSE_INFO_STATUSBAR.grid(column=1, row=9, columnspan=5, sticky=(tkinter.W, tkinter.E))

    # Add padding to all of the widgets:
    for child in mainframe.winfo_children():
        # Ensure the scrollbar and text area don't have padding in between them:
        if child == G_MOUSE_INFO_LOG_TEXT_AREA_SCROLLBAR:
            child.grid_configure(padx=0, pady=3)
        elif child == G_MOUSE_INFO_LOG_TEXT_AREA:
            child.grid_configure(padx=(3, 0), pady=3)
        elif child == G_MOUSE_INFO_STATUSBAR:
            child.grid_configure(padx=0, pady=(3, 0))
        else:
            # All other widgets have a standard padding of 3:
            child.grid_configure(padx=3, pady=3)

    G_MOUSE_INFO_ROOT.resizable(False, False) # Prevent the window from being resized.

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
