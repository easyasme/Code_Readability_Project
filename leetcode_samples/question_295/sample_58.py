class MedianFinder:

    def __init__(self):
        self.median=[]

    def addNum(self, num: int) -> None:
        self.median.append(num)

    def findMedian(self) -> float:
        self.median.sort()
        if len(self.median)%2==0:
            mid = len(self.median)//2
            return (self.median[mid]+self.median[mid-1])/2
        else:
            return self.median[len(self.median)//2]


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()