class MedianFinder:

    def __init__(self):
        self.lst = []
        self.length = 0

    def addNum(self, num: int) -> None:
        self.lst.append(num)
        self.length += 1
        
    def findMedian(self) -> float:
        self.lst.sort()
        mid = self.length // 2
        if self.length % 2:
            return self.lst[mid]
        return sum(self.lst[mid - 1:mid + 1]) / 2
                          


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()