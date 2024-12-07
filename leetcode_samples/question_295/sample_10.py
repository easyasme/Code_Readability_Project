# 295. Find Median from Data Stream
# Hard

# AM(28) M(14) F(10) A(9) G(5) L(2)
# TT(3) SP(2) Citadel(2)
# SF(6) 

class MedianFinder:
    
    # Other IDEAS: Two Heaps | Buckets | Segament Tree | Reservoir Sampling | Order Statistic Trees
    
    # IDEA: Insertion Sort + Binary Search
    # Time: O(n)
    # Space: O(n)
    # Runtime: 279 ms, faster than 15.89% of Python3 online submissions for Find Median from Data Stream.
    # Memory Usage: 36.5 MB, less than 13.40% of Python3 online submissions for Find Median from Data Stream.
    def __init__(self):
        self._sort = []

    # O(n)    
    def addNum(self, num: int) -> None:
        self._insert_sort(num)
        

    # Time: O(1)
    def findMedian(self) -> float:
        # corner cases
        N = len(self._sort)
        if N == 0: return 0
        if N == 1: return self._sort[0]
        
        # check even or odd cases
        index = N//2

        return self._sort[index] if N % 2 != 0 else (self._sort[index] + self._sort[index - 1]) / 2
        

    # Time: O(n) + O(log n) => O(n)
    def _insert_sort(self, num: int) -> None:
        if not len(self._sort):
            self._sort.append(num)
            return
        
        # do binary search to find insert position
        lo, hi = 0, len(self._sort) - 1
        
        # O(logn)
        while lo <= hi:
            mid = lo + (hi - lo) // 2
            val = self._sort[mid]
            
            if val >= num:
                lo = mid + 1
            else:
                hi = mid - 1
        # O(n)        
        self._sort.insert(lo, num)
    

class MedianFinder2:     
    # IDEA: Two Heaps -> Min Heap and Max Heap
    # Time: O(log n)
    # Space: O(n)
    # Runtime: 383 ms, faster than 44.67% of Python3 online submissions for Find Median from Data Stream.
    # Memory Usage: 36.2 MB, less than 46.92% of Python3 online submissions for Find Median from Data Stream 
  
    def __init__(self):
        self._min_heap: Heapq[int] = []
        self._max_heap: Heapq[int] = []
            

    # O(5 * logn)
    def addNum(self, num: int) -> None:
        # 1 - push into max heap first
        heappush(self._max_heap, -num)
        # 2 - pop max healp into min heap
        heappush(self._min_heap, -heappop(self._max_heap))
        
        # 3 - keep max heap count >= min heap
        if len(self._max_heap) < len(self._min_heap):
            heappush(self._max_heap, -heappop(self._min_heap))
        

    # Time: O(1)
    def findMedian(self) -> float:
        # corner cases
        if not self._max_heap and not self._min_heap:
            return 0.0
        
        return (-self._max_heap[0] + self._min_heap[0]) / 2.0 if len(self._max_heap) == len(self._min_heap) else -self._max_heap[0]
            
        
        
# Other approach or IDEAS:

# Buckets Approach
    '''
    The idea of dividing existing numbers into several ranges:
        Say we already have 10k numbers in vector, each time adding a number requires sorting all 10k numbers, which is slow.

        To optimize, we can store 10k numbers in several (say 10) vectors, and nums in each vector are sorted.

        Then each time we add a number, just need to find one vector with correct range,
        insert the number and sort this vector only. Since its size is relatively small, it's fast.

        When we have a vector's size greater than a threshold, just split it into two halfs.
    
    Link:
            https://leetcode.com/problems/find-median-from-data-stream/discuss/74057/Tired-of-TWO-HEAPSET-solutions-See-this-segment-dividing-solution-(c%2B%2B)
    '''
    
    
# Reservoir Sampling:
    '''
    Following along the lines of using buckets: if the stream is statistically distributed, you can rely on Reservoir Sampling. 
    Basically, if you could maintain just one good bucket (or reservoir) which could hold a representative sample of the entire 
    stream, you could estimate the median of the entire stream from just this one bucket. This means good time and memory performance. 
    Reservoir Sampling lets you do just that. Determining a "good" size for your reservoir? Now, that's a whole other challenge.
    A good explanation for this can be found in

    Link: 
        https://stackoverflow.com/questions/10657503/find-running-median-from-a-stream-of-integers/10693752#10693752
    '''
   
#
# Segment Trees:
    '''
    They are a great data structure if you need to do a lot of insertions or a lot of read queries over a limited range of input values.
    They allow us to do all such operations fast and in roughly the same amount of time, always. The only problem is that they are far
    from trivial to implement. Take a look at my 
    
    Link:
        https://leetcode.com/articles/a-recursive-approach-to-segment-trees-range-sum-queries-lazy-propagation/
    '''
    
#
# Order Statistic Trees:
    '''
    They are data structures which seem to be tailor-made for this problem. They have all the nice features of a BST, but also let 
    you find the kth order element stored in the tree. They are a pain to implement and no standard interview would require you to
    code these up. But they are fun to use if they are already implemented in the language of your choice.
    '''
    
    
# Your MedianFinder object will be instantiated and called as such:
# obj = MedianFinder()
# obj.addNum(num)
# param_2 = obj.findMedian()