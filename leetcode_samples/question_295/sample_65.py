class MedianFinder:
    def __init__(self):
        self.nums = []  # array to store numbers

    def addNum(self, num: int):
        self.nums.append(num) #add the num to the array

    def findMedian(self) -> float:
        self.nums.sort() #sort the array
        
        #calculate the median
        n = len(self.nums)
        if n % 2 == 1:
            return float(self.nums[n // 2]) #odd number of elements
        else:
            return (self.nums[(n // 2) - 1] + self.nums[n // 2]) / 2 #even number of elements

# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()