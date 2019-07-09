# Mouse Info by Al Sweigart al@inventwithpython.com

# Note: how to specify where a tkintr window opens:
# https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens

"""
Features we should consider adding:
* Register a global hotkey for copying/logging info. (Should this hotkey be configurable?)

Features that have been considered and rejected:

* The Save Log/Save Screenshot buttons should open a file dialog box.
* The Save Log button should append text, instead of overwrite it.
* The log text area should prepopulate itself with the contents of the given filename.
* The button delay should be configurable instead of just set to 3 seconds.
"""

__version__ = '0.0.2'
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
        _fields_ = [('x', ctypes.c_long),
                    ('y', ctypes.c_long)]

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
            subprocess.call(['scrot', '-z', tmpFilename])
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

class MouseInfoWindow:
    def _updateMouseInfoTextFields(self):
        # Update the XY and RGB text fields in the Mouse Info window.

        # Get the XY coordinates of the current mouse position:
        x, y = position()
        self.xyTextboxSV.set('%s,%s' % (x - self.xOrigin, y - self.yOrigin))

        # Mouse Info currently only works on the primary monitor, and doesn't
        # support multi-monitor setups. The color information isn't reliable
        # when the mouse is not on the primary monitor, so display an error instead.
        width, height = size()
        if sys.platform == 'darwin':
            # TODO - Until I can get screenshots without the mouse cursor, this feature doesn't work on mac.
            self.rgbSV.set('NA_on_macOS')
        elif not (0 <= x < width and 0 <= y < height):
            self.rgbSV.set('NA_on_multimonitor_setups')
        else:
            # Get the RGB color value of the pixel currently under the mouse:
            # NOTE: On Windows & Linux, getpixel() returns a 3-integer tuple, but on macOS it returns a 4-integer tuple.
            rgbValue = screenshot().getpixel((x, y))
            r, g, b, = rgbValue[0], rgbValue[1], rgbValue[2]
            self.rgbSV.set('%s,%s,%s' % (r, g, b))

        if sys.platform == 'darwin':
            # TODO - Until I can get screenshots without the mouse cursor, this feature doesn't work on mac.
            self.rgbHexSV.set('NA_on_macOS')
        elif not (0 <= x < width and 0 <= y < height):
            self.rgbHexSV.set('NA_on_multimonitor_setups')
        else:
            # Convert this RGB value into a hex RGB value:
            rHex = hex(r)[2:].upper().rjust(2, '0')
            gHex = hex(g)[2:].upper().rjust(2, '0')
            bHex = hex(b)[2:].upper().rjust(2, '0')
            hexColor = '#%s%s%s' % (rHex, gHex, bHex)
            self.rgbHexSV.set(hexColor)

        if (sys.platform == 'darwin') or (not (0 <= x < width and 0 <= y < height)):
            self.colorFrame.configure(background='black')
        else:
            # Update the color panel:
            self.colorFrame.configure(background=hexColor)

        # As long as the self.isRunning variable is True,
        # schedule this function to be called again in 100 milliseconds.
        # NOTE: Previously this if-else code was at the top of the function
        # so that I could avoid the "invalid command name" message that
        # was popping up (this didn't work though), but it was also causing
        # a weird bug where the text fields weren't populated until I moved
        # the tkinter window. I have no idea why that behavior was happening.
        # You can reproduce it by moving this if-else code to the top of this
        # function.
        if self.isRunning:
            self.root.after(100, self._updateMouseInfoTextFields)
        else:
            return # Mouse Info window has been closed, so return immediately.


    def _copyText(self, textToCopy):
        try:
            pyperclip.copy(textToCopy)
            self.statusbarSV.set('Copied ' + textToCopy)
        except pyperclip.PyperclipException as e:
            if platform.system() == 'Linux':
                self.statusbarSV.set('Copy failed. Run "sudo apt-get install xsel".')
            else:
                self.statusbarSV.set('Clipboard error: ' + str(e))


    def _copyXyMouseInfo(self, *args):
        # Copy the contents of the XY coordinate text field in the Mouse Info
        # window to the clipboard.
        if self.delayEnabledSV.get() == 'on' and len(args) == 0:
            # Start countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyXyMouseInfo, 2)
            self.xyCopyButtonSV.set('Copy in 3')
        elif len(args) == 1 and args[0] == 2:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyXyMouseInfo, 1)
            self.xyCopyButtonSV.set('Copy in 2')
        elif len(args) == 1 and args[0] == 1:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyXyMouseInfo, 0)
            self.xyCopyButtonSV.set('Copy in 1')
        else:
            # Delay disabled or countdown has finished:
            self._copyText(self.xyTextboxSV.get())
            self.xyCopyButtonSV.set('Copy XY')


    def _copyRgbMouseInfo(self, *args):
        # Copy the contents of the RGB color text field in the Mouse Info
        # window to the clipboard.
        if self.delayEnabledSV.get() == 'on' and len(args) == 0:
            # Start countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyRgbMouseInfo, 2)
            self.rgbCopyButtonSV.set('Copy in 3')
        elif len(args) == 1 and args[0] == 2:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyRgbMouseInfo, 1)
            self.rgbCopyButtonSV.set('Copy in 2')
        elif len(args) == 1 and args[0] == 1:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyRgbMouseInfo, 0)
            self.rgbCopyButtonSV.set('Copy in 1')
        else:
            # Delay disabled or countdown has finished:
            self._copyText(self.rgbSV.get())
            self.rgbCopyButtonSV.set('Copy RGB')


    def _copyRgbHexMouseInfo(self, *args):
        # Copy the contents of the RGB hex color text field in the Mouse Info
        # window to the clipboard.
        if self.delayEnabledSV.get() == 'on' and len(args) == 0:
            # Start countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyRgbHexMouseInfo, 2)
            self.rgbHexCopyButtonSV.set('Copy in 3')
        elif len(args) == 1 and args[0] == 2:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyRgbHexMouseInfo, 1)
            self.rgbHexCopyButtonSV.set('Copy in 2')
        elif len(args) == 1 and args[0] == 1:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyRgbHexMouseInfo, 0)
            self.rgbHexCopyButtonSV.set('Copy in 1')
        else:
            # Delay disabled or countdown has finished:
            self._copyText(self.rgbHexSV.get())
            self.rgbHexCopyButtonSV.set('Copy RGB Hex')


    def _copyAllMouseInfo(self, *args):
        # Copy the contents of the XY coordinate and RGB color text fields in the
        # Mouse Info window to the log text field.
        textFieldContents = '%s %s %s' % (self.xyTextboxSV.get(),
                                          self.rgbSV.get(),
                                          self.rgbHexSV.get())
        #self._copyText(textFieldContents)
        if self.delayEnabledSV.get() == 'on' and len(args) == 0:
            # Start countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyAllMouseInfo, 2)
            self.allCopyButtonSV.set('Copy in 3')
        elif len(args) == 1 and args[0] == 2:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyAllMouseInfo, 1)
            self.allCopyButtonSV.set('Copy in 2')
        elif len(args) == 1 and args[0] == 1:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._copyAllMouseInfo, 0)
            self.allCopyButtonSV.set('Copy in 1')
        else:
            # Delay disabled or countdown has finished:
            textFieldContents = '%s %s %s' % (self.xyTextboxSV.get(),
                                              self.rgbSV.get(),
                                              self.rgbHexSV.get())
            self._copyText(textFieldContents)
            self.allCopyButtonSV.set('Copy All')


    def _logXyMouseInfo(self, *args):
        # Log the contents of the XY coordinate text field in the Mouse Info
        # window to the log text field.
        if self.delayEnabledSV.get() == 'on' and len(args) == 0:
            # Start countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logXyMouseInfo, 2)
            self.xyLogButtonSV.set('Log in 3')
        elif len(args) == 1 and args[0] == 2:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logXyMouseInfo, 1)
            self.xyLogButtonSV.set('Log in 2')
        elif len(args) == 1 and args[0] == 1:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logXyMouseInfo, 0)
            self.xyLogButtonSV.set('Log in 1')
        else:
            # Delay disabled or countdown has finished:
            logContents = self.logTextarea.get('1.0', 'end-1c') + '%s\n' % (self.xyTextboxSV.get()) # 'end-1c' doesn't include the final newline
            self.logTextboxSV.set(logContents)
            self._setLogTextAreaContents(logContents)
            self.statusbarSV.set('Logged ' + self.xyTextboxSV.get())
            self.xyLogButtonSV.set('Log XY')


    def _logRgbMouseInfo(self, *args):
        # Log the contents of the RGB color text field in the Mouse Info
        # window to the log text field.
        if self.delayEnabledSV.get() == 'on' and len(args) == 0:
            # Start countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logRgbMouseInfo, 2)
            self.rgbLogButtonSV.set('Log in 3')
        elif len(args) == 1 and args[0] == 2:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logRgbMouseInfo, 1)
            self.rgbLogButtonSV.set('Log in 2')
        elif len(args) == 1 and args[0] == 1:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logRgbMouseInfo, 0)
            self.rgbLogButtonSV.set('Log in 1')
        else:
            # Delay disabled or countdown has finished:
            logContents = self.logTextarea.get('1.0', 'end-1c') + '%s\n' % (self.rgbSV.get()) # 'end-1c' doesn't include the final newline
            self.logTextboxSV.set(logContents)
            self._setLogTextAreaContents(logContents)
            self.statusbarSV.set('Logged ' + self.rgbSV.get())
            self.rgbLogButtonSV.set('Log RGB')


    def _logRgbHexMouseInfo(self, *args):
        # Log the contents of the RGB hex color text field in the Mouse Info
        # window to the log text field.
        if self.delayEnabledSV.get() == 'on' and len(args) == 0:
            # Start countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logRgbHexMouseInfo, 2)
            self.rgbHexLogButtonSV.set('Log in 3')
        elif len(args) == 1 and args[0] == 2:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logRgbHexMouseInfo, 1)
            self.rgbHexLogButtonSV.set('Log in 2')
        elif len(args) == 1 and args[0] == 1:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logRgbHexMouseInfo, 0)
            self.rgbHexLogButtonSV.set('Log in 1')
        else:
            # Delay disabled or countdown has finished:
            logContents = self.logTextarea.get('1.0', 'end-1c') + '%s\n' % (self.rgbHexSV.get()) # 'end-1c' doesn't include the final newline
            self.logTextboxSV.set(logContents)
            self._setLogTextAreaContents(logContents)
            self.statusbarSV.set('Logged ' + self.rgbHexSV.get())
            self.rgbHexLogButtonSV.set('Log RGB Hex')


    def _logAllMouseInfo(self, *args):
        # Log the contents of the XY coordinate and RGB color text fields in the
        # Mouse Info window to the log text field.
        if self.delayEnabledSV.get() == 'on' and len(args) == 0:
            # Start countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logAllMouseInfo, 2)
            self.allLogButtonSV.set('Log in 3')
        elif len(args) == 1 and args[0] == 2:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logAllMouseInfo, 1)
            self.allLogButtonSV.set('Log in 2')
        elif len(args) == 1 and args[0] == 1:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._logAllMouseInfo, 0)
            self.allLogButtonSV.set('Log in 1')
        else:
            # Delay disabled or countdown has finished:
            textFieldContents = '%s %s %s' % (self.xyTextboxSV.get(),
                                              self.rgbSV.get(),
                                              self.rgbHexSV.get())
            logContents = self.logTextarea.get('1.0', 'end-1c') + '%s\n' % (textFieldContents) # 'end-1c' doesn't include the final newline
            self.logTextboxSV.set(logContents)
            self._setLogTextAreaContents(logContents)
            self.statusbarSV.set('Logged ' + textFieldContents)
            self.allLogButtonSV.set('Log All')

    def _setXyOrigin(self, *args):
        if self.delayEnabledSV.get() == 'on' and len(args) == 0:
            # Start countdown by having after() call this function in 1 second:
            self.root.after(1000, self._setXyOrigin, 2)
            self.xyOriginSetButtonSV.set('Setting in 3')
        elif len(args) == 1 and args[0] == 2:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._setXyOrigin, 1)
            self.xyOriginSetButtonSV.set('Setting in 2')
        elif len(args) == 1 and args[0] == 1:
            # Continue countdown by having after() call this function in 1 second:
            self.root.after(1000, self._setXyOrigin, 0)
            self.xyOriginSetButtonSV.set('Setting in 1')
        else:
            # Delay disabled or countdown has finished:
            x, y = position()
            self.xyOriginSV.set(str(x) + ', ' + str(y))
            self.xOrigin = x
            self.yOrigin = y

            self.statusbarSV.set('Set XY Origin to ' + str(x) + ', ' + str(y))
            self.xyOriginSetButtonSV.set('Set XY Origin')

    def _resetXyOrigin(self, *args):
        self.xOrigin = 0
        self.yOrigin = 0
        self.xyOriginSV.set('0, 0')
        self.statusbarSV.set('Reset XY Origin to 0, 0')

    def _xyOriginChanged(self, sv):
        contents = sv.get()
        if len(contents.split(',')) != 2:
            return # Do nothing if the text is invalid
        x, y = contents.split(',')
        x = x.strip()
        y = y.strip()
        if not x.isdecimal() or not y.isdecimal():
            return # Do nothing.
        self.xOrigin = int(x)
        self.yOrigin = int(y)
        self.statusbarSV.set('Set XY Origin to ' + x + ', ' + y)

    def _setLogTextAreaContents(self, logContents):
        if RUNNING_PYTHON_2:
            self.logTextarea.delete('1.0', tkinter.END)
            self.logTextarea.insert(tkinter.END, logContents)
        else:
            self.logTextarea.replace('1.0', tkinter.END, logContents)

        # Scroll to the bottom of the text area:
        topOfTextArea, bottomOfTextArea = self.logTextarea.yview()
        self.logTextarea.yview_moveto(bottomOfTextArea)


    def _saveLogFile(self, *args):
        # Save the current contents of the log file text field. Automatically
        # overwrites the file if it exists. Displays an error message in the
        # status bar if there is a problem.
        try:
            with open(self.logFilenameSV.get(), 'w') as fo:
                fo.write(self.logTextboxSV.get())
        except Exception as e:
            self.statusbarSV.set('ERROR: ' + str(e))
        else:
            self.statusbarSV.set('Log file saved to ' + self.logFilenameSV.get())


    def _saveScreenshotFile(self, *args):
        # Saves a screenshot. Automatically overwrites the file if it exists.
        # Displays an error message in the status bar if there is a problem.
        try:
            screenshot(self.screenshotFilenameSV.get())
        except Exception as e:
            self.statusbarSV.set('ERROR: ' + str(e))
        else:
            self.statusbarSV.set('Screenshot file saved to ' + self.screenshotFilenameSV.get())


    def __init__(self):
        """Launches the Mouse Info window, which displays XY coordinate and RGB
        color information for the mouse's current position."""

        self.isRunning = True # While True, the text fields will update.

        # Create the Mouse Info window:
        self.root = tkinter.Tk()
        self.root.title('Mouse Info ' + __version__)
        self.root.minsize(400, 100)

        # Create the main frame in the Mouse Info window:
        if RUNNING_PYTHON_2:
            mainframe = tkinter.Frame(self.root)
        else:
            mainframe = ttk.Frame(self.root, padding='3 3 12 12')

        # Set up the grid for the Mouse Info window's widgets:
        mainframe.grid(column=0, row=0, sticky=(tkinter.N, tkinter.W, tkinter.E, tkinter.S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        # WIDGETS ON ROW 1:

        # Set up the instructional text label:
        #ttk.Label(mainframe, text='Tab over the buttons and press Enter to\n"click" them as you move the mouse around.').grid(column=1, row=1, columnspan=2, sticky=tkinter.W)
        self.delayEnabledSV = tkinter.StringVar()
        self.delayEnabledSV.set('on')
        delayCheckbox = ttk.Checkbutton(mainframe, text='3 Sec. Button Delay', variable=self.delayEnabledSV, onvalue='on', offvalue='off')
        delayCheckbox.grid(column=1, row=1, columnspan=2, sticky=tkinter.W)


        # Set up the button to copy the XY coordinates to the clipboard:
        self.allCopyButtonSV = tkinter.StringVar()
        self.allCopyButtonSV.set('Copy All')
        self.allCopyButton = ttk.Button(mainframe, textvariable=self.allCopyButtonSV, width=MOUSE_INFO_BUTTON_WIDTH, command=self._copyAllMouseInfo)
        self.allCopyButton.grid(column=3, row=1, sticky=tkinter.W)
        self.allCopyButton.bind('<Return>', self._copyAllMouseInfo)

        # Set up the button to copy the XY coordinates to the clipboard:
        self.allLogButtonSV = tkinter.StringVar()
        self.allLogButtonSV.set('Log All')
        self.allLogButton = ttk.Button(mainframe, textvariable=self.allLogButtonSV, width=MOUSE_INFO_BUTTON_WIDTH, command=self._logAllMouseInfo)
        self.allLogButton.grid(column=4, row=1, sticky=tkinter.W)
        self.allLogButton.bind('<Return>', self._logAllMouseInfo)

        # Set up the variables for the content of the Mouse Info window's text fields:
        self.xyTextboxSV          = tkinter.StringVar() # The str contents of the xy text field.
        self.rgbSV                = tkinter.StringVar() # The str contents of the rgb text field.
        self.rgbHexSV             = tkinter.StringVar() # The str contents of the rgb hex text field.
        self.xyOriginSV           = tkinter.StringVar() # The str contents of the xy origin field.
        self.logTextboxSV         = tkinter.StringVar() # The str contents of the log text area.
        self.logFilenameSV        = tkinter.StringVar() # The str contents of the log filename text field.
        self.screenshotFilenameSV = tkinter.StringVar() # The str contents of the screenshot filename text field.
        self.statusbarSV          = tkinter.StringVar() # The str contents of the status bar at the bottom of the window.

        # WIDGETS ON ROW 2:

        # Set up the XY coordinate text field and label:
        self.xyInfoTextbox = ttk.Entry(mainframe, width=16, textvariable=self.xyTextboxSV)
        self.xyInfoTextbox.grid(column=2, row=2, sticky=(tkinter.W, tkinter.E))
        ttk.Label(mainframe, text='XY Position').grid(column=1, row=2, sticky=tkinter.W)

        # Set up the button to copy the XY coordinates to the clipboard:
        self.xyCopyButtonSV = tkinter.StringVar()
        self.xyCopyButtonSV.set('Copy XY')
        self.xyCopyButton = ttk.Button(mainframe, textvariable=self.xyCopyButtonSV, width=MOUSE_INFO_BUTTON_WIDTH, command=self._copyXyMouseInfo)
        self.xyCopyButton.grid(column=3, row=2, sticky=tkinter.W)
        self.xyCopyButton.bind('<Return>', self._copyXyMouseInfo)

        # Set up the button to log the XY coordinates:
        self.xyLogButtonSV = tkinter.StringVar()
        self.xyLogButtonSV.set('Log XY')
        self.xyLogButton = ttk.Button(mainframe, textvariable=self.xyLogButtonSV, width=MOUSE_INFO_BUTTON_WIDTH, command=self._logXyMouseInfo)
        self.xyLogButton.grid(column=4, row=2, sticky=tkinter.W)
        self.xyLogButton.bind('<Return>', self._logXyMouseInfo)

        # WIDGETS ON ROW 3:

        # Set up the RGB color text field and label:
        self.rgbSV_entry = ttk.Entry(mainframe, width=16, textvariable=self.rgbSV)
        self.rgbSV_entry.grid(column=2, row=3, sticky=(tkinter.W, tkinter.E))
        ttk.Label(mainframe, text='RGB Color').grid(column=1, row=3, sticky=tkinter.W)

        # Set up the button to copy the RGB color to the clipboard:
        self.rgbCopyButtonSV = tkinter.StringVar()
        self.rgbCopyButtonSV.set('Copy RGB')
        self.rgbCopyButton = ttk.Button(mainframe, textvariable=self.rgbCopyButtonSV, width=MOUSE_INFO_BUTTON_WIDTH, command=self._copyRgbMouseInfo)
        self.rgbCopyButton.grid(column=3, row=3, sticky=tkinter.W)
        self.rgbCopyButton.bind('<Return>', self._copyRgbMouseInfo)

        # Set up the button to log the XY coordinates:
        self.rgbLogButtonSV = tkinter.StringVar()
        self.rgbLogButtonSV.set('Log RGB')
        self.rgbLogButton = ttk.Button(mainframe, textvariable=self.rgbLogButtonSV, width=MOUSE_INFO_BUTTON_WIDTH, command=self._logRgbMouseInfo)
        self.rgbLogButton.grid(column=4, row=3, sticky=tkinter.W)
        self.rgbLogButton.bind('<Return>', self._logRgbMouseInfo)

        # WIDGETS ON ROW 4:

        # Set up the RGB hex color text field and label:
        self.rgbHexSV_entry = ttk.Entry(mainframe, width=16, textvariable=self.rgbHexSV)
        self.rgbHexSV_entry.grid(column=2, row=4, sticky=(tkinter.W, tkinter.E))
        ttk.Label(mainframe, text='RGB As Hex').grid(column=1, row=4, sticky=tkinter.W)

        # Set up the button to copy the RGB hex color to the clipboard:
        self.rgbHexCopyButtonSV = tkinter.StringVar()
        self.rgbHexCopyButtonSV.set('Copy RGB Hex')
        self.rgbHexCopyButton = ttk.Button(mainframe, textvariable=self.rgbHexCopyButtonSV, width=MOUSE_INFO_BUTTON_WIDTH, command=self._copyRgbHexMouseInfo)
        self.rgbHexCopyButton.grid(column=3, row=4, sticky=tkinter.W)
        self.rgbHexCopyButton.bind('<Return>', self._copyRgbHexMouseInfo)

        # Set up the button to log the XY coordinates:
        self.rgbHexLogButtonSV = tkinter.StringVar()
        self.rgbHexLogButtonSV.set('Log RGB Hex')
        self.rgbHexLogButton = ttk.Button(mainframe, textvariable=self.rgbHexLogButtonSV, width=MOUSE_INFO_BUTTON_WIDTH, command=self._logRgbHexMouseInfo)
        self.rgbHexLogButton.grid(column=4, row=4, sticky=tkinter.W)
        self.rgbHexLogButton.bind('<Return>', self._logRgbHexMouseInfo)

        # WIDGETS ON ROW 5:

        # Set up the frame that displays the color of the pixel currently under the mouse cursor:
        self.colorFrame = tkinter.Frame(mainframe, width=50, height=50)
        self.colorFrame.grid(column=2, row=5, sticky=(tkinter.W, tkinter.E))
        ttk.Label(mainframe, text='Color').grid(column=1, row=5, sticky=tkinter.W)

        # WIDGETS ON ROW 6:

        # Set up the XY origin text field and label:
        self.xOrigin = 0
        self.yOrigin = 0
        self.xyOriginSV.set('0, 0')
        ttk.Label(mainframe, text='XY Origin').grid(column=1, row=6, sticky=tkinter.W)
        self.xyOriginSV.trace("w", lambda name, index, mode, sv=self.xyOriginSV: self._xyOriginChanged(sv))
        self.xyOriginSV_entry = ttk.Entry(mainframe, width=16, textvariable=self.xyOriginSV)
        self.xyOriginSV_entry.grid(column=2, row=6, sticky=(tkinter.W, tkinter.E))

        # Set up the button to set the XY origin:
        self.xyOriginSetButtonSV = tkinter.StringVar()
        self.xyOriginSetButtonSV.set('Set XY Origin')
        self.xyOriginSetButton = ttk.Button(mainframe, textvariable=self.xyOriginSetButtonSV, width=MOUSE_INFO_BUTTON_WIDTH, command=self._setXyOrigin)
        self.xyOriginSetButton.grid(column=3, row=6, sticky=tkinter.W)
        self.xyOriginSetButton.bind('<Return>', self._setXyOrigin)

        # Set up the button to reset the XY origin to 0, 0:
        self.xyOriginResetButton = ttk.Button(mainframe, text='Reset XY Origin', width=MOUSE_INFO_BUTTON_WIDTH, command=self._resetXyOrigin)
        self.xyOriginResetButton.grid(column=4, row=6, sticky=tkinter.W)
        self.xyOriginResetButton.bind('<Return>', self._resetXyOrigin)

        # WIDGETS ON ROW 7:

        # Set up the multiline text widget where the log info appears:
        self.logTextarea = tkinter.Text(mainframe, width=20, height=6)
        self.logTextarea.grid(column=1, row=7, columnspan=4, sticky=(tkinter.W, tkinter.E, tkinter.N, tkinter.S))
        self.logTextareaScrollbar = ttk.Scrollbar(mainframe, orient=tkinter.VERTICAL, command=self.logTextarea.yview)
        self.logTextareaScrollbar.grid(column=5, row=7, sticky=(tkinter.N, tkinter.S))
        self.logTextarea['yscrollcommand'] = self.logTextareaScrollbar.set

        # WIDGETS ON ROW 8:
        self.logFilenameTextbox = ttk.Entry(mainframe, width=16, textvariable=self.logFilenameSV)
        self.logFilenameTextbox.grid(column=1, row=8, columnspan=3, sticky=(tkinter.W, tkinter.E))
        self.saveLogButton = ttk.Button(mainframe, text='Save Log', width=MOUSE_INFO_BUTTON_WIDTH, command=self._saveLogFile)
        self.saveLogButton.grid(column=4, row=8, sticky=tkinter.W)
        self.saveLogButton.bind('<Return>', self._saveLogFile)
        self.logFilenameSV.set(os.path.join(os.getcwd(), 'mouseInfoLog.txt'))

        # WIDGETS ON ROW 9:
        G_MOUSE_INFO_SCREENSHOT_FILENAME_entry = ttk.Entry(mainframe, width=16, textvariable=self.screenshotFilenameSV)
        G_MOUSE_INFO_SCREENSHOT_FILENAME_entry.grid(column=1, row=9, columnspan=3, sticky=(tkinter.W, tkinter.E))
        self.saveScreenshotButton = ttk.Button(mainframe, text='Save Screenshot', width=MOUSE_INFO_BUTTON_WIDTH, command=self._saveScreenshotFile)
        self.saveScreenshotButton.grid(column=4, row=9, sticky=tkinter.W)
        self.saveScreenshotButton.bind('<Return>', self._saveScreenshotFile)
        self.screenshotFilenameSV.set(os.path.join(os.getcwd(), 'mouseInfoScreenshot.png'))

        # WIDGETS ON ROW 10:
        statusbar = ttk.Label(mainframe, relief=tkinter.SUNKEN, textvariable=self.statusbarSV)
        statusbar.grid(column=1, row=10, columnspan=5, sticky=(tkinter.W, tkinter.E))

        # Add padding to all of the widgets:
        for child in mainframe.winfo_children():
            # Ensure the scrollbar and text area don't have padding in between them:
            if child == self.logTextareaScrollbar:
                child.grid_configure(padx=0, pady=3)
            elif child == self.logTextarea:
                child.grid_configure(padx=(3, 0), pady=3)
            elif child == statusbar:
                child.grid_configure(padx=0, pady=(3, 0))
            else:
                # All other widgets have a standard padding of 3:
                child.grid_configure(padx=3, pady=3)

        self.root.resizable(False, False) # Prevent the window from being resized.

        self.xyInfoTextbox.focus() # Put the focus on the XY coordinate text field to start.

        self.root.after(100, self._updateMouseInfoTextFields) # Begin updating the text fields.

        # Make the mouse info window "always on top".
        self.root.attributes('-topmost', True)
        self.root.update()

        # Start the application:
        self.root.mainloop()

        # Application has closed, set this to False:
        self.isRunning = False

        # Destroy the tkinter root widget:
        try:
            self.root.destroy()
        except tkinter.TclError:
            pass

if __name__ == '__main__':
    MouseInfoWindow()
