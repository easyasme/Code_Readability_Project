class MedianFinder:


    def __init__(self):
        self.small = []
        self.large = []
        

    def addNum(self, num: int) -> None:

        if self.large and num > self.large[0]:
            self.insert(num, self.large)
        else:
            self.insert(-1 * num, self.small)   
        if len(self.small) > len(self.large) + 1:
            val = self.delete(self.small) * -1
            
            self.insert(val, self.large)
        if len(self.large) > len(self.small) + 1:
            val = self.delete(self.large)
            val = -1 * val
            self.insert(val, self.small )
        

    def findMedian(self) -> float:

        if len(self.small) == len(self.large):
            return ((-1 * self.small[0]) + self.large[0])/2
        elif len(self.small) > len(self.large):
            return -1 * self.small[0]
        elif len(self.large) > len(self.small):
            return self.large[0]

    def getParent(self, i):
        return (i-1)//2
    
    def left(self, i):
        return 2 * i +1
    
    def right(self, i):
        return 2 * i + 2

    def insert(self, num, arr):
        arr.append(num)
        i = len(arr) -1

        while i > 0 and arr[self.getParent(i)] > arr[i]:
            parent = self.getParent(i)
            arr[i] , arr[parent] =  arr[parent], arr[i]
            i = parent
    
    def delete(self, arr):
        if len(arr) == 0:
            return math.inf
        val = arr[0]
        
        arr[0]  = arr[len(arr)-1]
        arr.pop()
       
        self.heapify(arr, 0)

        return val


    def heapify(self, arr, i):
        
        left = self.left(i)
        right = self.right(i)

        smallest = i
        n = len(arr)

        if left < n and arr[left] < arr[smallest]:
            smallest = left
        if right < n and arr[right] < arr[smallest]:
            smallest = right
        if smallest != i:
            arr[smallest], arr[i] = arr[i], arr[smallest]
            self.heapify(arr, smallest)


        


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()