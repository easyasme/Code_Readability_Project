class MedianFinder:

    def __init__(self):
       self.arr = []
       self.size = 0 

    def addNum(self, num: int) -> None:
        self.arr.append(num)
        self.size += 1

    def findMedian(self) -> float:
        self.arr.sort()
        if self.size % 2 == 0:
            return (self.arr[(self.size - 1) //  2] + self.arr[self.size // 2]) / 2
        return self.arr[self.size//2]


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()