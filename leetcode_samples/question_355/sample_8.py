import heapq
from collections import defaultdict
class Twitter:    

    def __init__(self):
        self.relationships = defaultdict(set) # userId: (followeeId)
        self.tweets = defaultdict(list) # userId: [time, tweetId]
        self.time = 0

    def postTweet(self, userId: int, tweetId: int) -> None: #(userId, tweetId)
        self.tweets[userId].append([self.time, tweetId])
        self.time -= 1

    def getNewsFeed(self, userId: int) -> List[int]:
        res = []
        maxHeap = []

        self.relationships[userId].add(userId)
        # (time, tweetId, userId, index)
        for followeeId in self.relationships[userId]:
            tweets = self.tweets[followeeId]
            if tweets:
                idx = len(tweets) - 1
                time, tweetId = tweets[idx] # get last
                heapq.heappush(maxHeap, [time, tweetId, followeeId, idx - 1]) # prime it to provide the next latest tweet
        while maxHeap and len(res) < 10:
            time, tweetId, followeeId, idx = heapq.heappop(maxHeap)
            res.append(tweetId)

            if idx >= 0: # if idx == 0 then that means there is exactly 1 tweet left. below 0 means no more
                time, tweetId = self.tweets[followeeId][idx]
                heapq.heappush(maxHeap, [time, tweetId, followeeId, idx - 1])
        return res

    def follow(self, followerId: int, followeeId: int) -> None:
        if followerId == followeeId:
            return
        if followeeId in self.relationships[followerId]:
            return
        self.relationships[followerId].add(followeeId)
        
    def unfollow(self, followerId: int, followeeId: int) -> None:
        if followeeId in self.relationships[followerId]:
            self.relationships[followerId].remove(followeeId)


# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)