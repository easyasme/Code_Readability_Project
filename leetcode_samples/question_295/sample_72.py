class MedianFinder:

    def __init__(self):
        self.nums = []
       

    def addNum(self, num: int) -> None:
        self.nums.append(num)

    def findMedian(self) -> float:
        if self.nums:
            self.nums.sort()
            if len(self.nums) % 2 != 0:
                med_ind = len(self.nums) // 2
                return self.nums[med_ind]
            else:
                med_1 = len(self.nums) // 2
                med_2 = (len(self.nums) // 2) - 1
                return (self.nums[med_1] + self.nums[med_2]) / 2



# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()