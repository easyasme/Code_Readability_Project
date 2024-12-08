#!/usr/bin/env python3
# Traverses a directory, calculates file size and SHA256 hash, and writes the information to an Excel file.
# I guess I named it "tl" because I had tree list in mind? Not sure.

import os
import csv
import hashlib
import openpyxl
from openpyxl.utils import get_column_letter

def get_file_info(path):
    """
    Returns the size and sha256 hash of a file
    """
    with open(path, 'rb') as f:
        data = f.read()
        size = len(data)
        sha256 = hashlib.sha256(data).hexdigest()
    return size, sha256

def tree_format_path(path, root_dir):
    """
    Returns the tree-like formatted path
    """
    relative_path = os.path.relpath(path, root_dir)
    depth = relative_path.count(os.sep)
    tree_format = "│   " * (depth - 1) + "├── " + os.path.basename(path)
    return tree_format

def write_file_info_to_excel(path, size, sha256, worksheet, row, root_dir):
    """
    Writes the file info to an Excel worksheet
    """
    tree_path = tree_format_path(path, root_dir)
    worksheet.cell(row=row, column=1, value=tree_path)
    worksheet.cell(row=row, column=2, value=size)
    worksheet.cell(row=row, column=3, value=sha256)

def traverse_directory(directory_path, output_filename):
    """
    Traverses a directory and writes file info to an Excel file
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'File Info'
    ws['A1'] = 'Path'
    ws['B1'] = 'Size'
    ws['C1'] = 'SHA256'
    row = 2
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            path = os.path.join(root, file_name)
            size, sha256 = get_file_info(path)
            write_file_info_to_excel(path, size, sha256, ws, row, directory_path)
            row += 1
    for column_letter in ['A', 'B', 'C']:
        column = ws.column_dimensions[column_letter]
        column.width = max(len(str(cell.value)) for row in ws.iter_rows(min_row=1, max_col=1, max_row=ws.max_row) for cell in row) + 2
    wb.save(output_filename)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Get recursive tree list of files and subdirectories and output their file size and sha256 hash to an Excel file.')
    parser.add_argument('directory_path', help='the path to the directory to traverse')
    parser.add_argument('output_filename', help='the name of the output Excel file')
    args = parser.parse_args()
    traverse_directory(args.directory_path, args.output_filename)
