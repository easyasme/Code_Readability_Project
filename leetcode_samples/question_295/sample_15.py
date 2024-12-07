class MedianFinder:

    def __init__(self):
        # Two heaps: small (max-heap) and large (min-heap)
        self.small = []  # Simulated max-heap (store negatives)
        self.large = []  # Min-heap

    def addNum(self, num: int) -> None:
        # Add the number to the correct heap
        if self.large and num > self.large[0]:
            self.insert(num, self.large)  # Add to min-heap
        else:
            self.insert(-num, self.small)  # Add to max-heap (store as negative)

        # Balance the heaps to maintain size constraints
        if len(self.small) > len(self.large) + 1:
            val = -self.delete(self.small)  # Remove from max-heap
            self.insert(val, self.large)   # Add to min-heap
        elif len(self.large) > len(self.small) + 1:
            val = self.delete(self.large)  # Remove from min-heap
            self.insert(-val, self.small)  # Add to max-heap

    def findMedian(self) -> float:
        # Return the median depending on the size of the heaps
        if len(self.small) == len(self.large):
            return (-self.small[0] + self.large[0]) / 2
        elif len(self.small) > len(self.large):
            return -self.small[0]
        else:
            return self.large[0]

    def getParent(self, i):
        return (i - 1) // 2

    def left(self, i):
        return 2 * i + 1

    def right(self, i):
        return 2 * i + 2

    def insert(self, num, arr):
        # Insert the element into the heap
        arr.append(num)
        i = len(arr) - 1

        # Heapify-up to maintain the heap property
        while i > 0 and arr[self.getParent(i)] > arr[i]:
            parent = self.getParent(i)
            arr[i], arr[parent] = arr[parent], arr[i]
            i = parent

    def delete(self, arr):
        # Remove the root element from the heap
        if not arr:
            return float('inf')
        val = arr[0]
        arr[0] = arr[-1]
        arr.pop()
        self.heapify(arr, 0)
        return val

    def heapify(self, arr, i):
        # Heapify-down to maintain the heap property
        n = len(arr)
        while True:
            left = self.left(i)
            right = self.right(i)
            smallest = i

            if left < n and arr[left] < arr[smallest]:
                smallest = left
            if right < n and arr[right] < arr[smallest]:
                smallest = right
            if smallest == i:
                return

            arr[i], arr[smallest] = arr[smallest], arr[i]
            i = smallest
