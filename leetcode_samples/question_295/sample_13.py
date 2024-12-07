class MedianFinder:

    def __init__(self):
        self.left_max_heap = []
        self.right_min_heap = []
        self.left_heap_size = 0
        self.right_heap_size = 0

    def addNum(self, num: int) -> None:
        # first insert num into a heap
        if not self.left_max_heap or num < self.left_max_heap[0]:
            self.left_max_heap.append(num)
            self.left_heap_size += 1
            self.stepup_maxheap(self.left_max_heap,self. left_heap_size)
        else:
            self.right_min_heap.append(num)
            self.right_heap_size += 1
            self.stepup_minheap(self.right_min_heap, self.right_heap_size)

        # now do balancing i.e., len(left_max_heap) >= len(right_min_heap)
        if abs(self.left_heap_size - self.right_heap_size) > 1:
            val = self.get_top(self.left_max_heap, max=True)
            self.left_heap_size -= 1

            self.right_min_heap.append(val)
            self.right_heap_size += 1
            self.stepup_minheap(self.right_min_heap, self.right_heap_size)
        elif self.right_heap_size > self.left_heap_size:
            val = self.get_top(self.right_min_heap, min=True)
            self.right_heap_size -= 1

            self.left_max_heap.append(val)
            self.left_heap_size += 1
            self.stepup_maxheap(self.left_max_heap, self.left_heap_size)


    def findMedian(self) -> float:
        if self.left_heap_size == self.right_heap_size:
            return (self.left_max_heap[0] + self.right_min_heap[0]) / 2
        else:
            return self.left_max_heap[0]

    def heapify_max(self, arr, index, n): # stepdown
        largest = index
        lchild = 2*index+1
        rchild = 2*index + 2
        
        if lchild < n and arr[lchild] > arr[largest]:
            largest = lchild
        if rchild < n and arr[rchild] > arr[largest]:
            largest = rchild
            
        if largest != index:
            arr[index], arr[largest] = arr[largest], arr[index]
            self.heapify_max(arr, largest, n)

    def heapify_min(self, arr, index, n): # stepdown
        largest = index
        lchild = 2*index+1
        rchild = 2*index + 2
        
        if lchild < n and arr[lchild] < arr[largest]:
            largest = lchild
        if rchild < n and arr[rchild] < arr[largest]:
            largest = rchild
            
        if largest != index:
            arr[index], arr[largest] = arr[largest], arr[index]
            self.heapify_min(arr, largest, n)

    def stepup_maxheap(self, arr, n):
        child = n-1
        parent = (child-1) // 2
        while child > 0 and arr[child] > arr[parent]:
            arr[child], arr[parent] = arr[parent], arr[child]
            child = parent
            parent = (child-1) // 2

    def stepup_minheap(self, arr, n):
        child = n-1
        parent = (child-1) // 2
        while child > 0 and arr[child] < arr[parent]:
            arr[child], arr[parent] = arr[parent], arr[child]
            child = parent
            parent = (child-1) // 2     

    def get_top(self, arr, max=False, min=False):
        val = arr[0]
        last = arr.pop()
        if arr:
            arr[0] = last
            if max:
                self.heapify_max(arr, 0, len(arr))
            else:
                self.heapify_min(arr, 0, len(arr))
        return val   


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()