class MedianFinder:

    def __init__(self):
        # we use a minheap for larger half, and maxheap for lowerhalf
        # lower heap holds 0-1 more element than large half
        # if size of the structure is odd, return lower[-1]
        # if size of the structure is even , return lower[-1] + upper[-1] / 2
        self.lower = []
        self.upper = []

    def addNum(self, num: int) -> None:
        heappush(self.lower, -num)
        heappush(self.upper, -heappop(self.lower))

        if len(self.lower) < len(self.upper):
            heappush(self.lower, -heappop(self.upper))

    def findMedian(self) -> float:
        n = len(self.lower + self.upper)
        if n % 2 == 0:
            # even
            return (-self.lower[0] + self.upper[0]) / 2
        else:
            return float(-self.lower[0])


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()