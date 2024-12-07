class MedianFinder:

    def __init__(self):
        self.sorted_nums = []
        

    def addNum(self, num: int) -> None:
        self.sorted_nums.append(num)        
        

    def findMedian(self) -> float:
        # sorted_nums = sorted(self.num_list)
        self.sorted_nums.sort()
        arr_len = len(self.sorted_nums)

        if arr_len % 2 == 0:
            return (self.sorted_nums[int(arr_len / 2)] + self.sorted_nums[int(arr_len / 2)-1]) / 2
        else:
            return self.sorted_nums[floor(arr_len / 2)]


        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()