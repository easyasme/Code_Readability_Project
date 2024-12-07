class MedianFinder:
    def __init__(self):
        self.lower_half_max_heap = []
        self.upper_half_min_heap = []

    def addNum(self, num: int) -> None:
        if (len(self.lower_half_max_heap) == 0) or (num <= -self.lower_half_max_heap[0]):
            heapq.heappush(self.lower_half_max_heap, -num)

            if len(self.lower_half_max_heap) > len(self.upper_half_min_heap) + 1:
                heapq.heappush(self.upper_half_min_heap, -heapq.heappop(self.lower_half_max_heap))
        else:
            heapq.heappush(self.upper_half_min_heap, num)

            if len(self.upper_half_min_heap) > len(self.lower_half_max_heap):
                heapq.heappush(self.lower_half_max_heap, -heapq.heappop(self.upper_half_min_heap))

    def findMedian(self) -> float:
        if len(self.lower_half_max_heap) > len(self.upper_half_min_heap):
            return -self.lower_half_max_heap[0]

        return (self.upper_half_min_heap[0] - self.lower_half_max_heap[0]) / 2