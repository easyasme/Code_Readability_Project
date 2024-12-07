class MedianFinder:

    def __init__(self):
        self.small = []
        self.large = []

    def addNum(self, num: int) -> None:
        i = bisect.bisect_right(self.small, num)
        if i == len(self.small):
            i = bisect.bisect_right(self.large, num)
            self.large.insert(i, num)
        else:
            self.small.insert(i, num)
        while self.large and len(self.small) < len(self.large):
            self.small.append(self.large.pop(0))
        while self.small and len(self.small) > len(self.large) + 1:
            self.large.insert(0, self.small.pop(-1))

    def findMedian(self) -> float:
        if len(self.small) == len(self.large):
            return (self.small[-1] + self.large[0]) / 2
        else:
            return self.small[-1]       


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()