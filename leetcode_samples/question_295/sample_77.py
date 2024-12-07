class MedianFinder:

    def __init__(self):
        self.store = []

    def addNum(self, num: int) -> None:
        self.store.append(num)

    def findMedian(self) -> float:
        self.store.sort()
        n = len(self.store)
        if n % 2== 0:
            vals = n//2
            avg = float(sum(self.store[n//2 - 1: n//2 + 1])/2)
        else:
            avg = float(self.store[n//2])
        return avg
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()