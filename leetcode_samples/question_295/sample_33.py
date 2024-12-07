class MedianFinder:

    def __init__(self):
        self.large = []
        self.small = []
        heapify(self.small)
        heapify(self.large)
        

    def addNum(self, num: int) -> None:
        if self.large and num > self.large[0]:
            heapq.heappush(self.large, num)
        else:
            heapq.heappush(self.small, -1 * num)
        
        if len(self.small) > len(self.large) + 1:
            heappush(self.large, -1 * heappop(self.small))
        elif len(self.large) > len(self.small):
            heappush(self.small, -1 * heappop(self.large))   


    def findMedian(self) -> float:
        if len(self.small) == len(self.large):
            return (-1 * heappop(self.small.copy()) + heappop(self.large.copy())) / 2
        elif len(self.small) > len(self.large):
            return -1 * heappop(self.small.copy())
        else:
            return heappop(self.large.copy())

        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()