#!python
import os
import subprocess
from datetime import datetime
import Quartz

from os.path import expanduser

window_title_to_capture = 'Zoom Meeting'

image_save_location = "{}/Documents/screencapture_{}.png".format(expanduser("~"),
                                                                 datetime.now().strftime("%h_%d_%Y-%I_%M_%S_%p"))

windows_list = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionAll,
                                                 Quartz.kCGNullWindowID)

captured = False

for window in windows_list:
    if window.valueForKey_('kCGWindowName') is not None and \
            window_title_to_capture in window.valueForKey_('kCGWindowName'):
        print('Capturing window with title: <{}> and id: <{}>'.format(window_title_to_capture,
                                                                      window.valueForKey_('kCGWindowNumber')))
        capture_process = subprocess.run(["/usr/sbin/screencapture",
                                          "-o",
                                          "-x",                                          
                                          "-l{}".format(window.valueForKey_('kCGWindowNumber')),
                                          image_save_location])
        if capture_process.returncode == 0:
            captured = True
            print('Screenshot successfully saved at: <{}>'.format(image_save_location))
        else:
            print('Could not save the screenshot. Please take a screenshot using cmd+shit+5')

if not captured:
    print('Unable to find a window titled: <{}>'.format(window_title_to_capture))
