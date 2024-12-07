class MedianFinder:

    def __init__(self):
        self.output = []

    def addNum(self, num: int) -> None:
        self.output.append(num)

    def findMedian(self) -> float:
        self.output.sort()
        l = 0
        r = len(self.output) - 1
        m = l + (r-l)//2
        if(len(self.output) % 2 == 0):
            return (self.output[m] + self.output[m + 1]) / 2
        else:
            return self.output[m] 

# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()