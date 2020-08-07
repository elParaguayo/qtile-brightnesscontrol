import os
import re
import subprocess

from libqtile.widget import base
from libqtile import bar, images
from libqtile.log_utils import logger

MODULE_NAME = "BrightnessControl"
ERROR_VALUE = -1


class BrightnessControl(object):
    """This module allows control of the screen brightness by writing to the
       relevant path in /sys/class/backlight

       The module can be initialised with the following parameters:

       device: path to the backlight device. Defaults to
               /sys/class/backlight/intel_backlight
       brightness_path: the name of the 'file' containing the brightness value
                        NB the user needs to have write access to this path
       max_brightness_path: the 'file' that stores the maximum brightness
                            value for the device. This can be overriden by the
                            user - see below.
       min_brightness: Define a lower limit for screen brightness to prevent
                       screen going completely dark.
       max_brightness: Define a maximum limit e.g. if you don't want to go to
                       full brightness. Use None to use system defined value.
       callback: accepts a function that will be called when user changes
                 brightness. Function should accept one parameter, the
                 brightness percentage.
    """

    def __init__(self, step=50,
                 device="/sys/class/backlight/intel_backlight",
                 brightness_path="brightness",
                 max_brightness_path="max_brightness",
                 min_brightness=100,
                 max_brightness=None,
                 callback=None):

        # Set useful values
        self.step = step
        self.device = device
        self.bright_path = os.path.join(device, brightness_path)
        self.min = min_brightness

        # Get max brightness levels and limit to lower of system add user value
        if max_brightness_path:
            self.max_path = os.path.join(device, max_brightness_path)
            self.max = self.get_max()

            if max_brightness:
                self.max = min(self.max, max_brightness)

        else:
            if max_brightness:
                self.max = max_brightness

            else:
                logger.warning("No maximum brightness defined. "
                               "Setting to default value of 500. "
                               "The script may behave unexpectedly.")
                self.max = 500

        # Get current brightness
        self.current = self.get_current()

        # Set up callbacks
        self.callback = callback
        self.widget_callback = None

        # Track previous value so we know if we need to send callbacks
        self.old = 0

    def change_brightness(self, step):

        # Get the current brightness level (we need to read this in case
        # the value has been changed elsewhere)
        self.current = self.get_current()

        # If we can read the value then let's process it
        if self.current and self.max:

            # Calculate the new value
            newval = self.current + step

            # Limit brightness so that min <= value <= max
            newval = max(min(newval, self.max), self.min)

            # Set the new value
            success = self.set_current(newval)

            # Do we need to trigger callbacks
            if newval != self.old:

                # If we couldn't set value, send the error value
                percentage = newval / self.max if success else ERROR_VALUE

                if self.callback:
                    self.callback(percentage)

                if self.widget_callback:
                    self.widget_callback(percentage)

            # Set the previous value
            self.old = newval

        # We should send callbacks if we couldn't read current or max value
        # e.g. to alert user to failure
        else:

            if self.callback:
                self.callback(ERROR_VALUE)

            if self.widget_callback:
                self.widget_callback(ERROR_VALUE)


    def _read(self, path):
        "Simple method to read value from given path"

        try:
            with open(path, "r") as b:
                value = int(b.read())
        except PermissionError:
            logger.error("Unable to read {}.".format(path))
            value = False
        except ValueError:
            logger.error("Unexpected value when reading {}.".format(path))
            value = False
        except Exception as e:
            logger.error("Unexpected error when reading {}: {}.".format(path, e))
            value = False

        return value

    def get_max(self):
        "Read the max brightness level for the device"

        maxval = self._read(self.max_path)
        if not maxval:
            logger.warning("Max value was not read. "
                           "Module may behave unexpectedly.")
        return maxval

    def get_current(self):
        "Read the current brightness level for the device"

        current = self._read(self.bright_path)
        if not current:
            logger.warning("Current value was not read. "
                           "Module may behave unexpectedly.")
        return current

    def set_current(self, newval):
        "Set the brightness level for the device"

        try:
            with open(self.bright_path, "w") as b:
                b.write(str(newval))
                success = True
        except PermissionError:
            logger.error("No write access to {}.".format(self.bright_path))
            success = False
        except Exception as e:
            logger.error("Unexpected error when writing birghtness value: {}.".format(e))
            success = False

        return success

    def brightness_up(self, *args, **kwargs):
        "Increase the brightness level"

        self.change_brightness(self.step)

    def brightness_down(self, *args, **kwargs):
        "Decrease the brightness level"

        self.change_brightness(self.step * -1)

    def Widget(self, **config):
        "Create an instance of the BrightnessControlWidget"

        # Create widget and define callback
        widget = BrightnessControlWidget(helper=self, **config)
        self.widget_callback = widget.status_change

        return widget


class BrightnessControlWidget(base._Widget):

    orientations = base.ORIENTATION_HORIZONTAL

    defaults = [
        ("font", "sans", "Default font"),
        ("fontsize", None, "Font size"),
        ("font_colour", "ffffff", "Colour of text."),
        ("text_format", "{percentage}%", "Text to display."),
        ("bar_colour", "008888", "Colour of bar displaying brightness level."),
        ("error_colour", "880000", "Colour of bar when displaying an error"),
        ("timeout_interval", 5, "Time before widet is hidden."),
        ("widget_width", 75, "Width of bar when widget displayed"),

    ]


    def __init__(self, helper, **config):
        base._Widget.__init__(self, bar.CALCULATED, **config)
        self.add_defaults(BrightnessControlWidget.defaults)

        # Provide a reference back to the BrightnessControl instance
        # May be useful for future enhancements
        self.helper = helper

        # We'll use a timer to hide the widget after a defined period
        self.update_timer = None

        # Set an initial brightness level
        self.percentage = -1

        # Hide the widget by default
        self.hidden = True

    def _configure(self, qtile, bar):
        base._Widget._configure(self, qtile, bar)
        # Calculate how much space we need to show text
        self.text_width = self.max_text_width()
        self.update()

    def max_text_width(self):

        # Calculate max width of text given defined layout
        width, _ = self.drawer.max_layout_size(
            [self.text_format.format(percentage=100)],
            self.font,
            self.fontsize
        )

        return width

    def status_change(self, percentage):

        # The brightness has changed so we need to show the widget
        self.hidden = False

        # Set the value and update the display
        self.percentage = percentage
        self.update()

        # Start the timer to hide the widget
        self.set_timer()

    def update(self):

        # Clear the widget backgrouns
        self.drawer.clear(self.background or self.bar.background)

        # If the value is positive then we've succcessully set the brightness
        if self.percentage >= 0:

            # Set colour and text to show current value
            bar_colour = self.bar_colour
            percentage = int(self.percentage * 100)
            text = self.text_format.format(percentage=percentage)
        else:

            # There's been an error so display accordingly
            bar_colour = self.error_colour
            text = "!"

        # Draw the bar
        self.drawer.set_source_rgb(bar_colour)
        self.drawer.fillrect(0,
                             0,
                             self.length * (abs(self.percentage)),
                             self.height,
                             1)

        # Create a text box
        layout = self.drawer.textlayout(text,
                                        self.font_colour,
                                        self.font,
                                        self.fontsize,
                                        None,
                                        wrap=False)

        # We want to centre this vertically
        y_offset = (self.bar.height - layout.height) / 2

        # Set the layout as wide as the widget so text is centred
        layout.width = self.length

        # Add the text to our drawer
        layout.draw(0, y_offset)

        # Redraw the bar
        self.bar.draw()


    def set_timer(self):

        # Cancel old timer
        if self.update_timer:
            self.update_timer.cancel()

        # Set new timer
        self.update_timer = self.timeout_add(self.timeout_interval, self.hide)

    def hide(self):

        # Hide the widget
        self.hidden = True
        self.update()

    def calculate_length(self):

        # If widget is hidden then width should be xero
        if self.hidden:
            return 0

        # Otherwise widget is the greater of the minimum size needed to
        # display 100% and the user defined max
        else:
            return max(self.text_width, self.widget_width)

    def draw(self):
        self.drawer.draw(offsetx=self.offset, width=self.length)
