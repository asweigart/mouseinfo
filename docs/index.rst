.. MouseInfo documentation master file, created by
   sphinx-quickstart on Mon Nov 12 14:17:27 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MouseInfo's documentation!
=======================================

MouseInfo is an app for displaying the XY coordinates of the mouse cursor, as well as RGB color information of the pixel under the mouse. This is useful for planning out GUI automation scripts where the mouse is directed to specific points on the screen. MouseInfo runs on Windows, macOS, and Linux for Python 3 and Python 2.7.

MouseInfo was made by Al Sweigart, and is also bundled with the PyAutoGUI package.

Install
-------

To install MouseInfo, run ``pip install mouseinfo`` (on Windows) or ``pip3 install mouseinfo`` (on macOS and Linux).

If you get a "command not found/recognized" type of error, try the following.

On Windows, use ``py.exe`` to run pip:

    ``py -m pip install mouseinfo``

If you have multiply versions of Python installed, you can select which one with a command line argument to ``py``. For example, for Python 3.8, run:

    ``py -3.8 -m pip install mouseinfo``

(This is the same as running ``pip install mouseinfo``.)

On macOS and Linux, you need to run ``python3``:

    ``python3 -m pip install mouseinfo``


Quickstart
----------

The app gives the XY coordinates of the mouse cursor's current position, as well as the RGB (red, green, blue) value of the pixel under the mouse cursor. This information can either by copied to the clipboard or logged to the app's log text field. The 0, 0 origin is in the top left of the screen (the primary monitor, in multi-monitor setups). The X coordinate increases going to the right (just as in mathematics), but the Y coordinate increases going down (the opposite of mathematics).


You can run MouseInfo by either running ``py -m mouseinfo`` (on Windows) or ``python3 -m mouseinfo`` (on macOS and Linux).

You can also run MouseInfo from the Python interactive shell:

.. code:: python

    >>> import mouseinfo
    >>> mouseinfo.MouseInfoWindow()

After the MouseInfo window appears, try the following:

#. Move the mouse cursor around. Notice how the information in the XY Position, RGB Color, and RGB As Hex text fields change, as well as the colored rectangle.

#. Move the mouse cursor to the top left corner of the screen (on the primary monitor, if you have multiple monitors connected). The XY Position will read 0, 0. This is the origin.

#. Slide the mouse cursor along the top edge of the screen to the right. Notice that the first number (the X coordinate) in XY Position text field increases while the second number (the Y coordinate) stays at 0. Move the mouse back to the origin at the top left corner.

#. Slide the mouse cursor down along the left edge of the screen. Notice that the second number (the Y coordinate) in the XY Position text field increases while the first number (the X coordinate) stays at 0.

#. Click on the *Copy XY* button. Notice that the button text changes to a 3 second countdown, and then the contents of the XY Position text field are copied to the clipboard. The status bar at the bottom will also change to say "Copied 618,1130" (or whatever the numbers were for you).

#. Pick a spot on the screen whose XY coordinates you'd like to record. Click the *Copy XY* button, and in the three seconds given, position the mouse cursor on that spot. The XY coordinates of that spot will be copied to the clipboard.

#. Click the *Log XY* button, and in the three seconds given, position the mouse cursor on that spot again. The XY coordinates of that spot will be written to the log text field.

#. Press the F2 key. Note that this does the same thing as clicking the *Copy XY* button. Look at the items under the *Copy* and *Log* menus for the hotkeys for the other buttons.

#. Change the *XY Origin* text field to ``100, 200``. Notice that the new 0, 0 origin (reported in the *XY Position* text field) is now 100 pixels right and 200 pixels down from the top right corner of the screen. You can use MouseInfo to find XY coordinates relative to any spot on the screen this way.

#. Click the *Save Log* button. Notice that the contents of the log text field have been saved to the filename in the text field to the left of the button.

#. Click the *Save Screenshot* button. Notice that a screenshot has been saved to the filename in the text field to the left of the button.

#. Uncheck the *3 Sec. Button Delay* checkbox, and click the Copy and Log buttons. Notice that they immediately record the position or color of the pixel under the mouse cursor. The mouse cursor is over the MouseInfo's own buttons in this case, but you can position the mouse cursor and then press the F1 through F8 hotkeys as well.


Buttons
-------

The app looks like this:

TODO: Screenshot.

* **mouseinfo.readthedocs.io Link** - A clickable link to this documentation.

* **3 Sec. Button Delay** - If checked, the copy and log buttons have a 3 second delay to let you position the mouse before the mouse information is copied or logged.

* **Copy All** - Copy the XY, RGB, and RGB hex information to the clipboard, e.g. ``2013,171 229,241,251 #E5F1FB``

* **Log All** - Log the XY, RGB, and RGB hex information to the log text field, e.g. ``2013,171 229,241,251 #E5F1FB``

* **XY Position** - The current XY coordinates of the mouse cursor, relative to the origin. The origin can be changed by typing in a new XY coordinates into the text field. The two numbers for X and Y should be separated by a comma.

* **Copy XY** - Copy the XY coordinates of the mouse cursor's current position, e.g. ``2013,171``. If the *3 Sec. Button Delay* checkbox is checked, the information will be copied after a 3 second delay.

* **Log XY** - Log the XY coordinates of the mouse cursor's current position, e.g. ``2013,171`` to the log text field. If the *3 Sec. Button Delay* checkbox is checked, the information will be logged after a 3 second delay.

* **Copy RGB** - Copy the RGB color values of the pixel under mouse cursor's current position, e.g. ``52,99,159``. If the *3 Sec. Button Delay* checkbox is checked, the information will be copied after a 3 second delay.

* **Log RGB** - Log the RGB color values of the pixel under mouse cursor's current position, e.g. ``52,99,159``. to the log text field If the *3 Sec. Button Delay* checkbox is checked, the information will be logged after a 3 second delay.

* **Copy RGB as Hex** - Copy the XY hex coordinates of the mouse cursor's current position, e.g. ``#34639F``. If the *3 Sec. Button Delay* checkbox is checked, the information will be copied after a 3 second delay.

* **Log RGB as Hex** - Log the RGB color hex values of the pixel under mouse cursor's current position, e.g. ``#34639F`` to the log text field. If the *3 Sec. Button Delay* checkbox is checked, the information will be logged after a 3 second delay.

* **Color** - A colored box that shows the current color in the *RGB Color* and *RGB as Hex* fields.

* **XY Origin** - An XY coordinate for the origin that the coordinate sin hte *XY Position* field is relative to.

* **Save Log** - Saves the contents of the log text field to the filename in the text field to the left. (This filename is *mouseInfoLog.txt* by default.)

* **Save Screenshot** - Takes a screenshot and saves it to the filename in the text field to the left. (This filename is *mouseInfoScreenshot.png* by default.)

.. toctree::
   :maxdepth: 2


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
