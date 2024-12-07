class MedianFinder:

    def __init__(self):
        self.data = []
        self.length = 0
        

    def addNum(self, num: int) -> None:
        self.data.append(num)
        self.length += 1

    def findMedian(self) -> float:
        self.data.sort()
        return (self.data[self.length//2] + self.data[(self.length-1)//2])/2
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()