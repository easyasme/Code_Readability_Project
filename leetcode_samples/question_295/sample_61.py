class MedianFinder:

    def __init__(self):
        self.res = []


    def addNum(self, num: int) -> None:
        self.res.append(num)
        

    def findMedian(self) -> float:
        n = len(self.res)
        self.res.sort()
        if n%2==0:
            x = (n//2) -1
            y = (n//2)
            return (self.res[x]+self.res[y])/2
        else:
            return self.res[n//2]

        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()