class MedianFinder:
    arr = []
    def __init__(self):
        self.arr = []

    def addNum(self, num: int) -> None:
        if len(self.arr)==0:
            self.arr.append(num)
        else:
            left = 0
            right = len(self.arr)-1
            insertIndex = len(self.arr)
            while left<=right:
                mid = (left+right)//2
                if self.arr[mid]==num:
                    insertIndex = mid
                    break
                elif self.arr[mid]<num:
                    left = mid+1
                elif self.arr[mid]>num:
                    insertIndex = mid
                    right = mid-1
            #print("self.ar=",self.arr)
            self.arr.insert(insertIndex,num)

    def findMedian(self) -> float:
        mid = len(self.arr)//2
        if len(self.arr)%2==1:
            return self.arr[mid]
        a = self.arr[mid-1]
        b = self.arr[mid]
        return (a+b)/2


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()