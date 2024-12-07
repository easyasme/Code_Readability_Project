class Twitter:
# follow yourself
    def __init__(self):
        self.followMap = defaultdict(set)
        self.tweetMap = defaultdict(list)
        self.time = 0

    def postTweet(self, userId: int, tweetId: int) -> None:
        self.tweetMap[userId].append((self.time, tweetId))
        self.time += 1

    def getNewsFeed(self, userId: int) -> List[int]:
        res = []
        self.followMap[userId].add(userId)
        maxHeap = []
        for users in self.followMap[userId]:
            if users in self.tweetMap:
                indx = len(self.tweetMap[users]) - 2
                t, tid = self.tweetMap[users][-1]
                heappush(maxHeap, (-1 * t, tid, users, indx))

        while maxHeap and len(res) < 10:
            t, tid, users, indx = heappop(maxHeap)
            res.append(tid)
            
            if indx >= 0: 
                t, tid = self.tweetMap[users][indx]
                heappush(maxHeap, (-1 * t, tid, users, indx-1))
        return res



        

    def follow(self, followerId: int, followeeId: int) -> None:
        self.followMap[followerId].add(followeeId)
        

    def unfollow(self, followerId: int, followeeId: int) -> None:
        if followeeId in self.followMap[followerId]: self.followMap[followerId].remove(followeeId)


# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)