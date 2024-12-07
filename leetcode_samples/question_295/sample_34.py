
class MedianFinder:

    def __init__(self):
        self.arr = []
        
    def binary_search(arr, target, start, end):
        if start == end:
            if arr[start] > target:
                return start
            else:
                return start + 1
        
        if start > end:
            return start

        mid = (start + end) // 2

        if arr[mid] < target:
            return MedianFinder.binary_search(arr, target, mid + 1, end)
        elif arr[mid] > target:
            return MedianFinder.binary_search(arr, target, start, mid - 1)
        else:
            return mid


    def addNum(self, num: int) -> None:
        insert = MedianFinder.binary_search(self.arr, num, 0, len(self.arr) - 1)

        self.arr.insert(insert, num)
        

    def findMedian(self) -> float:
        if len(self.arr) % 2 == 1:
            return self.arr[len(self.arr) // 2]
        else:
            return (self.arr[len(self.arr) // 2 - 1] + self.arr[len(self.arr) // 2]) / 2
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()