from sortedcontainers import SortedList

class MedianFinder:

    def __init__(self):
        self.list = SortedList()

    def addNum(self, num: int) -> None:
        self.list.add(num)

    def findMedian(self) -> float:
        len_ = len(self.list)
        if len_%2:
            return self.list[len_//2]
        else:
            return (self.list[len_//2]+self.list[len_//2-1])/2


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()