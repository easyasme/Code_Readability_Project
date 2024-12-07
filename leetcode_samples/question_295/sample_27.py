class MedianFinder:

    def __init__(self):
        self.storage = []

    def addNum(self, num: int) -> None:
        # Step 1: Find the insertion point using binary search
        left, right = 0, len(self.storage)
        while left < right:
            mid = (left + right) // 2
            if self.storage[mid] < num:
                left = mid + 1
            else:
                right = mid
        
        # Step 2: Insert x at the found position
        self.storage.insert(left, num)

    # def addNum(self, num: int) -> None:
        
    #     def find_closest_index(arr,num):
    #         left = 0
    #         right = len(arr)-1
    #         while left <= right:
    #             mid = (left+right)//2
    #             if arr[mid] == num:
    #                 return mid
    #             elif num < arr[mid]:
    #                 right = mid - 1
    #             else:
    #                 left = mid + 1
    #         return left
        
    #     def binary_search_insert(arr,num):

    #         insert_index = find_closest_index(arr,num)
    #         arr.append(0)
    #         for i in reversed(range(insert_index,len(arr)-1)):
    #             arr[i+1] = arr[i]
    #         arr[insert_index] = num
        
    #     binary_search_insert(self.storage,num)
    #     #self.storage.append(num)
    #     #self.storage = sorted(self.storage)
        

    def findMedian(self) -> float:

        mid = len(self.storage) // 2
        
        if len(self.storage) == 0:
            return 0
        elif len(self.storage) == 1:
            return self.storage[0]
        elif len(self.storage) % 2 == 0:
            return (self.storage[mid-1]+self.storage[mid])/2
        else:
            return self.storage[mid]

    # ### 2 heaps
    # def __init__(self):
    #     self.lo = []  # max heap (inverted min heap)
    #     self.hi = []  # min heap

    # def addNum(self, num: int) -> None:
        
    #     heapq.heappush(self.lo, -num)  # add to max heap (invert num to simulate max heap)
        
    #     #print('insert',num)
        
    #     heapq.heappush(self.hi, -heapq.heappop(self.lo))  # balancing step
        
    #     #print(self.lo)
    #     #print(self.hi)

    #     if len(self.lo) < len(self.hi):  # maintain size property
    #         heapq.heappush(self.lo, -heapq.heappop(self.hi))
        
    #     #print('balancing',self.lo,self.hi)

    # def findMedian(self) -> float:
    #     if len(self.lo) > len(self.hi):
    #         return -self.lo[0]
    #     else:
    #         return (-self.lo[0] + self.hi[0]) / 2.0

    ### using binary search insertion

    # import bisect

    # def __init__(self):
    #     self.store = []

    # def addNum(self, num: int) -> None:       
        
    #     if not self.store:
    #         self.store.append(num)
    #     else:
    #         bisect.insort(self.store, num)

    # def findMedian(self) -> float:
    #     n = len(self.store)
    #     if n % 2 == 1:  # Odd number of elements
    #         return self.store[n // 2]
    #     else:  # Even number of elements
    #         return (self.store[n // 2 - 1] + self.store[n // 2]) / 2.0


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()