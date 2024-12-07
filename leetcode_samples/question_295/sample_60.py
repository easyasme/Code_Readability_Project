class MedianFinder:

    def __init__(self):
        self.arr = []

    def addNum(self, num: int) -> None:
        self.arr.append(num)

    def findMedian(self) -> float:
        self.arr.sort()
        arr_length = len(self.arr)
        if arr_length % 2:
            return self.arr[int(arr_length/2)]
        else:
            floor = arr_length // 2 - 1
            ceil = arr_length // 2
            median = (self.arr[floor] + self.arr[ceil])/2
            return median

# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()