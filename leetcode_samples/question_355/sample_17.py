import heapq

class Twitter:

    def __init__(self):
        self.tweets = {}
        self.following = {}
        self.time = 0

    def postTweet(self, userId: int, tweetId: int) -> None:
        if userId not in self.tweets:
            self.tweets[userId] = []
        self.tweets[userId].append((self.time, tweetId))
        self.time += 1

    def getNewsFeed(self, userId: int) -> List[int]:
        min_heap = []

        if userId in self.tweets:
            for tweet in self.tweets[userId][-10:]:
                heapq.heappush(min_heap, tweet)
        
        if userId in self.following:
            for followee in self.following[userId]:
                if followee in self.tweets:
                    for tweet in self.tweets[followee][-10:]:
                        heapq.heappush(min_heap, tweet)
                        if len(min_heap) > 10:
                            heapq.heappop(min_heap)
        
        result = []
        while min_heap:
            result.append(heapq.heappop(min_heap))
        result.sort(reverse=True)
        
        return [tweet[1] for tweet in result]


    def follow(self, followerId: int, followeeId: int) -> None:
        if followerId == followeeId:
            return
        if followerId not in self.following:
            self.following[followerId] = set()
        self.following[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        if followerId in self.following:
            self.following[followerId].discard(followeeId)


# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)