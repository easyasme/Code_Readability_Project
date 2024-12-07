class MedianFinder:

    def __init__(self):
        self.items = []
        

    def addNum(self, num: int) -> None:
        # binary search add
        def insert_item(left_idx, right_idx):
            if len(self.items) == 0:
                self.items.append(num)
                return

            if left_idx == len(self.items):
                self.items.append(num)
                return

            if left_idx > right_idx:
                self.items.insert(left_idx, num)
                return

            middle_idx = (left_idx + right_idx) // 2
            if self.items[middle_idx] >= num:
                insert_item(left_idx, middle_idx - 1)
            else:
                insert_item(middle_idx + 1, right_idx)
        insert_item(0, len(self.items))

    def findMedian(self) -> float:
        if len(self.items) == 0:
            return None
        middle_idx = (0 + len(self.items) - 1) // 2
        if len(self.items) % 2 == 0:
            return (self.items[middle_idx] + self.items[middle_idx + 1]) / 2
        return self.items[middle_idx]
        


# Your MedianFinder object will be instantiated and called as such:
# param_2 = obj.findMedian()