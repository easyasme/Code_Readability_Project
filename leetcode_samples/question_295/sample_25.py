from bisect import bisect_left
class MedianFinder:

    def __init__(self):
        self.data = []
        

    def addNum(self, num: int) -> None:
        # self.data.append(num)
        pos = bisect_left(self.data, num)
        self.data.insert(pos, num)
        

    def findMedian(self) -> float:
        n = len(self.data)
        if n == 0: return 0
        if n%2 == 1:
            return self.data[n//2] * 1.0
        else:
            return (self.data[n//2-1]+self.data[n//2]) /2 
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()