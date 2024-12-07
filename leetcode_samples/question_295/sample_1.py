import heapq as hq
class MedianFinder:

    def __init__(self):
        self.small = [] # max heap
        hq.heapify(self.small)
        self.large = [] # min heap
        hq.heapify(self.large)
        

    def addNum(self, num: int) -> None:
        if len(self.small) == len(self.large):
            hq.heappush(self.large, -hq.heappushpop(self.small, -num))
        else:
            hq.heappush(self.small, -hq.heappushpop(self.large, num))
        

    def findMedian(self) -> float:
        if len(self.small) == len(self.large):
            return (self.large[0]-self.small[0])/2.0
        else:
            return self.large[0] * 1.0
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()