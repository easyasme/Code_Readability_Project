class MedianFinder:

    def __init__(self):
        self.arr = []

    def addNum(self, num: int) -> None:
        #  the following can just be shortened to this — bisect.insort(self.arr, num)
        if not self.arr:
            self.arr.append(num)
            return
        l, r = 0, len(self.arr) - 1
        while l < r:
            m = (l + r)//2
            if self.arr[m] == num:
                self.arr.insert(m, num)
                return
            if num > self.arr[m]:
                l = m + 1
            else:
                r = m - 1
        if self.arr[l] < num:
            self.arr.insert(l + 1, num)
        else:
            self.arr.insert(l, num)

    def findMedian(self) -> float:
        if not self.arr:
            return 0
        half = len(self.arr) // 2
        if len(self.arr) % 2 == 0:
            return (self.arr[half - 1] + self.arr[half])/2
        else:
            return self.arr[half]


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()