class MedianFinder:

    def __init__(self):
        self.nums = None

    def addNum(self, num: int) -> None:
        if self.nums == None:
            self.nums = [num]
            return
        
        def recursiveInsert(num, start, end):
            if start == end:
                if self.nums[start] >= num:
                    self.nums.insert(start, num)
                    return
                else:
                    self.nums.insert(start+1, num)
                    return
            
            mid = start + ((end - start) // 2)
            if self.nums[mid] <= num:
                recursiveInsert(num, mid+1, end)
            else:
                recursiveInsert(num, start, mid)

        recursiveInsert(num, 0, len(self.nums)-1)

    def findMedian(self) -> float:
        mid = len(self.nums) // 2
        if len(self.nums) % 2 == 0:
            return (self.nums[mid-1] + self.nums[mid]) / 2
        else:
            return self.nums[mid]


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()