class Twitter:

    def __init__(self):
        self.friends_map = defaultdict(set)
        self.tweets_maps = defaultdict(collections.deque)  # (time, tweetId)
        self.time = 0

    def postTweet(self, userId: int, tweetId: int) -> None:
        self.time += 1
        self.tweets_maps[userId].appendleft((self.time, tweetId))
        if len(self.tweets_maps[userId]) > 10:
            self.tweets_maps[userId].pop()

    def getNewsFeed(self, userId: int) -> List[int]:
        # Get k lists.
        friends = self.friends_map[userId] | {userId}  # Include the user themselves
        lists = [self.tweets_maps[friend] for friend in friends if friend in self.tweets_maps]
    
        if not lists:
            return []
        
        merged_feed = self.mergeKLists(lists)
        return [tweetId for _, tweetId in list(merged_feed)[:10]]

    def follow(self, followerId: int, followeeId: int) -> None:
        self.friends_map[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        self.friends_map[followerId].discard(followeeId)

    def mergeTwoLists(self, nums1, nums2):
        merged = collections.deque()  # To store the merged results in correct order
        i, j = 0, 0  # Start from the beginning (latest tweets first)

        while i < len(nums1) and j < len(nums2):
            if nums1[i][0] > nums2[j][0]:  # Compare timestamps
                merged.append(nums1[i])
                i += 1
            else:
                merged.append(nums2[j])
                j += 1
        
        # Append remaining tweets from nums1 or nums2
        while i < len(nums1):
            merged.append(nums1[i])
            i += 1
        
        while j < len(nums2):
            merged.append(nums2[j])
            j += 1
    
        return merged


    def mergeSort(self, lists, l, r):
        if l == r:
            return lists[l]
        if l > r:  # Handle empty lists case
            return collections.deque()
        mid = l + (r-l) // 2
        left_lists = self.mergeSort(lists, l, mid)
        right_lists = self.mergeSort(lists, mid+1, r)
        return self.mergeTwoLists(left_lists, right_lists)

    def mergeKLists(self, lists):
        if not lists:
            return []
        return self.mergeSort(lists, 0, len(lists) - 1)
        


# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)