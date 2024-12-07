import bisect
class MedianFinder:

    def __init__(self):
        self.arr = []
        self.mid = -1
        self.add = True

    def addNum(self, num: int) -> None:
        bisect.insort(self.arr, num)
        if self.add:
            self.mid += 1
        self.add = not self.add

    def findMedian(self) -> float:
        if self.arr:
            if not self.add:
                return self.arr[self.mid]
            else:
                return (sum(self.arr[self.mid:self.mid+2])/2)
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()