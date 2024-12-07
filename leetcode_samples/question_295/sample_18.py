class MinHeap:
    def __init__(self):
        self.heap = list()
        self.size = 0

    def get_children(self, index):
        return 2 * index + 1, 2 * index + 2

    def get_parent(self, index):
        return max(0, (index - 1) // 2)

    def push(self, val):
        if self.size == 0:
            self.heap.append(val)
            self.size += 1
            return
        
        self.heap.append(val)
        self.size += 1

        index = self.size - 1
        parent_index = self.get_parent(index)

        while self.heap[parent_index] > self.heap[index]:
            self.heap[parent_index], self.heap[index] = self.heap[index], self.heap[parent_index]
            index = parent_index
            parent_index = self.get_parent(index)

    def pop(self):
        if self.size == 0:
            return None

        element = self.heap[0]
        self.size -= 1
        if self.size == 0:
            return element

        self.heap[0] = self.heap.pop()
        self.heapify()

        return element

    def heapify(self, index=0):
        lc, rc = self.get_children(index)

        min_index = index

        if lc < self.size and self.heap[lc] < self.heap[min_index]:
            min_index = lc

        if rc < self.size  and self.heap[rc] < self.heap[min_index]:
            min_index = rc

        if min_index == index:
            return 

        self.heap[min_index], self.heap[index] = self.heap[index], self.heap[min_index]
        
        self.heapify(min_index)


    def peek(self):
        if self.size > 0:
            return self.heap[0]

        return None

    def __size__(self):
        return self.size
        



class MedianFinder:
    def __init__(self):
        self.min_heap = MinHeap() # larger half
        self.max_heap = MinHeap() # smaller half

    def addNum(self, num: int) -> None:
        if self.min_heap.size == 0:
            self.min_heap.push(num)
            return

        if self.min_heap.size > 0 and self.min_heap.peek() <= num:
            self.min_heap.push(num)

        else:
            self._max_heap_push(num)

        self._rebalance()


    def findMedian(self) -> float:
        if (self.min_heap.size + self.max_heap.size) % 2 == 0:
            median = (self.min_heap.peek() + self._max_heap_peek()) / 2.0        
        elif self.min_heap.size > self.max_heap.size:
            median = self.min_heap.peek()
        else:
            median = self._max_heap_peek()
        return median

    def _rebalance(self):
        if abs(self.min_heap.size - self.max_heap.size) <= 1:
            return

        if self.min_heap.size < self.max_heap.size:
            self.min_heap.push(self._max_heap_pop())

        else:
            self._max_heap_push(self.min_heap.pop())


    def _max_heap_push(self, num):
        self.max_heap.push(-num)

    def _max_heap_pop(self):
        if self.max_heap.size > 0:
            val = self.max_heap.pop()
            if val is not None:
                return -val

            return None

    def _max_heap_peek(self):
        if self.max_heap.size > 0:
            val = self.max_heap.peek()
            if val is not None:
                return -val

        return None


# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()