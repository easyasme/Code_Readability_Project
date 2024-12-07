class MedianFinder:

    def __init__(self):
        self.arr = []
        

    def addNum(self, num: int) -> None:
        self.arr.append(num)
        

    def findMedian(self) -> float:
        self.arr.sort()

        len_arr = len(self.arr)
        
        if len_arr % 2 == 0:
            median = (self.arr[(len_arr // 2) - 1] + self.arr[(len_arr // 2) ]) / 2
            return median
        else:
            return self.arr[(len_arr // 2)]
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()