class MedianFinder:

    # NOTE: try using dual min heaps to manage the numbers.
    # - one minheap stores values smaller than the median.  other minheap stores values larger than median
    # - compute median:
    #   - grab top values from each heap, then compute mean (even sized array)
    #   - grab top value from larger heap when heap sizes do not match (odd sized array)

    def __init__( self ):
        self.count = 0
        self.values = []

    def addNum( self, num: int ) -> None:
        # print( "--- addNum(", num, ") ---" )

        if self.count == 0:
            # empty array
            self.values.append(num)
        else:
            # N-item array
            # binary search for insertion location
            lo = 0
            hi = self.count - 1

            while lo <= hi:
                index = int( lo + hi ) >> 1
                v = self.values[index]
                if v == num:
                    break
                elif v <= num:
                    lo = index + 1
                else:
                    hi = index - 1

            # check index to see if it found correct location
            if num > v:
                index += 1

            self.values.insert( index, num )
            # print( "  index: %d [%d]" %( index, v ) )

        # print( "  values:", self.values )
        self.count += 1
        return

    def findMedian( self ) -> float:
        # print( "--- findMedian( count=", self.count, ") ---")

        if self.count & 1:
            return self.values[ self.count >> 1 ]

        n = self.count >> 1
        return ( self.values[ n ] + self.values[n-1] ) * 0.5

        # print( "  median", self.values, "=", v )


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()