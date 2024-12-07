class MedianFinder:

    def __init__(self):
        # self.min_h = [] # stores the smaller half of numbers
        # self.max_h = [] # stores the larger half of numbers
        self.stream = []

    def addNum(self, num: int) -> None:
        self.stream.append(num)

    def findMedian(self) -> float:
        self.stream.sort()
        n = len(self.stream)
        if n % 2 == 0:
            return (self.stream[n // 2] + self.stream[(n // 2) - 1]) / 2.0
        else:
            return self.stream[n // 2]


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()