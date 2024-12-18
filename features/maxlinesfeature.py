# -*- coding: utf-8 -*-
"""MaxLinesFeature.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vGU9PXGfMmkAf-7ZKvk-2QUP5Ot3RKoc
"""

def max_lines(filename):
  max_line_len = 0
  with open(filename, 'r') as open_file:
    lines = open_file.readlines()
    for line in lines:
      if len(line) > max_line_len:
        max_line_len = len(line)
  return max_line_len