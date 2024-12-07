#!/usr/bin/env python

# Copyright (c) 2017 Adam Olsen <arolsen@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import re

swap_color, with_color = sys.argv[1:]

h = open('jbeans-theme.el', 'r')
data = h.read()
h.close()

data = re.sub(r'%s([ \)])' % swap_color, r'wakkawakka\1', data)
data = re.sub(r'%s([ \)])' % with_color, r'%s\1' % swap_color, data)
data = re.sub(r'wakkawakka([ \)])', r'%s\1' % with_color, data)

h = open("jbeans-theme.el", "w")
h.write(data)
h.close()
