#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  domes21b.py
#  
#  Copyright 2022 Thodoris Evangelakos <tevangelakos@isc.tuc.gr>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

#https://qvault.io/python/binary-search-tree-in-python

N = 10**6
n = 10**2
insertComparisons = 0
deleteComparisons = 0

class BSTNode: #class to create Node objects
    def __innit__(self, val=None):
        self.left= None
        self.right = None
        self.val = val
    
    def insComp(self):
        global insertComparisons
        insertComparisons += 1
    
    def delComp(self):
        global deleteComparisons
        deleteComparisons += 1
    
    def insert(self, val):
        self.insComp()
        if not self.val: #If the node doesn’t yet have a value, we can just set the given value and return
            self.val = val
            return
        
        self.insComp()
        if self.val == val: #If we ever try to insert a value that also exists, we can also simply return as this can be considered a noop
            return
        
        #If the given value is less than our node’s value and we already have a left child then we recursively call insert on our left child. If we don’t have a left child yet then we just make the given value our new left child.
        self.insComp()
        if val < self.val: 
            self.left.insert(val)
            return
        self.left = BSTNode(val)
        return
        
        #We can do the same (but inverted) for our right side.
        self.insComp()
        if self.right:
            self.right.insert(val)
            return
        self.right = BSTNode(val)
        
    def search(self, root, key):
        
    
    #The delete operation is one of the more complex ones. It is a recursive function as well, but it also returns the new state of the given node after performing the delete operation. This allows a parent whose child has been deleted to properly set it’s left or right data member to None.
    def delete(self, val):
        self.delComp()
        if self == None:
            return self
        self.delComp()
        if val < self.val:
            self.delComp()
            if self.left:
                self.left = self.left.delete(val)
            return self
        self.delComp()
        if val > self.val:
            self.delComp()
            if self.right:
                self.right = self.right.delete(val)
            return self
        self.delComp()
        if self.right = None:
            return self.left
        self.delComp()
        if self.left = None:
            return self.right
        min_larger_node = self.right
        self.delComp()
        while min_larger_node.left:
            self.delComp()
            min_larger_node = min_larger_node.left
        self.val = min_larger_node.val
        self.right = self.right.delete(min_larger_node.val)
        return self
        
    def search(self, val):
        if val == self.val:
            return True
        
        
def readBytes(file, position): #reads 4 bytes
    file.seek(position)
    byte_array = bytearray(file.read(4))
    return byte_array

def toIntArray(bytes):
    result = [0]
    result[0] = int.from_bytes(bytes[0:4], 'big')
    return result[0]
    
def readInt(file, position):
    #pass a simple position to this method
    intFromFile = toIntArray(readBytes(file, position*4)) #position 0 reads at 0, position 1 reads at 4 and so on (TAKEN CARE OF HERE XXX)
    return intFromFile    

def main():
    return 0

if __name__ == '__main__':
    #imports
    import os
    import timeit
    import time
    import numpy as np
    import array
    import random
    
    main()
