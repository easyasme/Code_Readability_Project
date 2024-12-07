class MedianFinder:
    def __init__(self):
        self.data = []
        

    def addNum(self, num: int) -> None:
        l = 0
        r = len(self.data) - 1
        while l <= r:
            mid = int((l + r) / 2)
            if self.data[mid] < num:
                l = mid + 1
            else:
                r = mid - 1

        self.data.insert(l, num)

    def findMedian(self) -> float:
        data_len = len(self.data)
        return (self.data[int((data_len - 1) / 2)] + self.data[int(data_len / 2)]) / 2
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian() 


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()