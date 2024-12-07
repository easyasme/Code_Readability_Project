class MedianFinder:

    def __init__(self):
        self.data = []
        self.length = 0

    def addNum(self, num: int) -> None:
        index = bisect.bisect_left(self.data, num)
        self.data.insert(index, num)
        self.length += 1

    def findMedian(self) -> float:
        if self.length % 2 == 0:
            return (self.data[self.length//2-1] + self.data[self.length//2]) / 2
        else:
            return self.data[self.length//2]


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()