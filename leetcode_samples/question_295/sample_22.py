import bisect

class MedianFinder:

    def __init__(self):
        self.nums = []

    # O(n)
    def addNum(self, num: int) -> None:
        bisect.insort(self.nums, num)

    # O(1)
    def findMedian(self) -> float:
        l = len(self.nums)
        if l % 2 == 1:
            i = l // 2
            return self.nums[i]
        else:
            i, j = (l // 2) - 1, l // 2
            return (self.nums[i] + self.nums[j]) / 2

# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()