class MedianFinder:

    def __init__(self):
        self.array = []

    def addNum(self, num: int) -> None:
        self.array.append(num)

    def findMedian(self) -> float:
        self.array.sort()
        mid = len(self.array)//2
        if len(self.array) % 2 == 0:
            return (self.array[mid] + self.array[mid - 1]) / 2
        else:
            return float(self.array[mid])


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()
