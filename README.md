# Brightness controls and Widget

This module provides basic screen brightness controls and a simple widget showing the brightness level for Qtile.

## About

Brightness control is handled by writing to the appropriate /sys/class/backlight device. The widget is updated instantly when the brightness is changed via this code and will autohide after a user-defined timeout.

## Demo

Here is an animated gif from my HTPC showing the widget in the bar.

![Demo](images/brightnesscontrol-demo.gif?raw=true)

## Installation

You can clone the repository and run:

```
python setup.py install
```
or, for Arch users, just copy the PKGBUILD file to your machine and build.

## Write access to backlight device

This script will not work unless the user has write access to the relevant backlight device.

This can be achieved via a udev rule which modifies the group and write permissions.

This repository includes an example rule which should work for "intel_backlight" devices. This is installed automatically by the PKGBUILD file or can be installed manually by copying it to /etc/udev/rules.d

You should then ensure that your user is a member of the "video" group.

## Configuration

Add the code to your config (`~/.config/qtile/config.py`):

```python
from brightnesscontrol import BrightnessControl
...
bc = BrightnessControl()
...
keys = [
...
Key([], "XF86MonBrightnessUp", lazy.function(bc.brightness_up)),
Key([], "XF86MonBrightnessDown", lazy.function(bc.brightness_down)),
...
]
...
screens = [
    Screen(
        top=bar.Bar(
            [
                widget.CurrentLayout(),
                widget.GroupBox(),
                widget.Prompt(),
                widget.WindowName(),
                bc.Widget(),
                widget.Clock(format='%Y-%m-%d %a %I:%M %p'),
                widget.QuickExit(),
            ],
            24,
        ),
    ),
]
```

## Customising

Both the BrightnessControl and widget allow for significant customisation.

The BrightnessControl class can accept the following parameters:

<table>
    <tr>
        <td>device</td>
        <td>path to the backlight device. Defaults to /sys/class/backlight/intel_backlight</td>
    </tr>
    <tr>
        <td>brightness_path</td>
        <td>the name of the 'file' containing the brightness value NB the user needs to have write access to this path</td>
    </tr>
    <tr>
        <td>max_brightness_path</td>
        <td>the 'file' that stores the maximum brightness value for the device. This can be overriden by the user - see below.</td>
    </tr>
    <tr>
        <td>min_brightness</td>
        <td>define a lower limit for screen brightness to prevent screen going completely dark.</td>
    </tr>
    <tr>
        <td>max_brightness</td>
        <td>define a maximum limit e.g. if you don't want to go to full brightness. Use None to use system defined value.</td>
    </tr>
    <tr>
        <td>callback</td>
        <td>accepts a function that will be called when user changes brightness. Function should accept one parameter, the brightness percentage.</td>
    </tr>
</table>




The widget can be customised with the following arguments:

<table>
    <tr>
            <td>font</td>
            <td>Default font</td>
    </tr>
    <tr>
            <td>fontsize</td>
            <td>Font size</td>
    </tr>
    <tr>
            <td>font_colour</td>
            <td>Colour of text.</td>
    </tr>
    <tr>
            <td>text_format</td>
            <td>Text to display.</td>
    </tr>
    <tr>
            <td>bar_colour</td>
            <td>Colour of bar displaying brightness level.</td>
    </tr>
    <tr>
            <td>error_colour</td>
            <td>Colour of bar when displaying an error</td>
    </tr>
    <tr>
            <td>timeout_interval</td>
            <td>Time before widget is hidden.</td>
    </tr>
    <tr>
            <td>widget_width</td>
            <td>Width of bar when widget displayed</td>
    </tr>
    <tr>
            <td>enable_power_saving</td>
            <td>Automatically set brightness depending on status (mains or battery)</td>
    </tr>
    <tr>
            <td>brightness_on_mains</td>
            <td>Brightness level on mains power (accepts integer value or percentage as string)</td>
    </tr>
    <tr>
            <td>brightness_on_battery</td>
            <td>Brightness level on battery power (accepts integer value or percentage as string)</td>
    </tr>
</table>

## Contributing

If you've used this (great, and thank you) you will find bugs so please [file an issue](https://github.com/elParaguayo/qtile-brightnesscontrol/issues/new).
