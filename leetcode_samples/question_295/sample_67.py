"""
class MedianFinder
- hold an array A
- addNum
    - append to array... O(1)
- findMedian
    - sort array  ... O(nlogn)
    - if even
        - m = len(A) // m 
        - return avg(A[m], A[m+1])
    - else return A[m]

"""
class MedianFinder:

    def __init__(self):
        self.A = []
        
    def addNum(self, num: int) -> None:
        self.A.append(num)
        
    def findMedian(self) -> float:
        self.A.sort()
        m = len(self.A) // 2
        if len(self.A) % 2 == 0:
            return (self.A[m] + self.A[m-1]) / 2
        return self.A[m]
            
        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()