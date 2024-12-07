class MedianFinder:

    def __init__(self):
        self.nums = []

    def addNum(self, num: int) -> None:
        self.nums.append(num)

    def findMedian(self) -> float:
        self.nums.sort()
        l= len(self.nums)-1
        m = l//2
        if l %2 == 0:
            return self.nums[m]
        else:
            return (self.nums[m] + self.nums[m+1])/2


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()