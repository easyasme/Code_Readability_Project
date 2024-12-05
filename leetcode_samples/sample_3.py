class Twitter:

    def __init__(self):
        self.timer = 0
        self.user_to_tweets = {}
        self.user_to_following = {}
        

    def postTweet(self, userId: int, tweetId: int) -> None:
        self.timer += 1
        if userId not in self.user_to_tweets:
            self.user_to_tweets[userId] = []
        self.user_to_tweets[userId].append((self.timer, tweetId))
        

    def getNewsFeed(self, userId: int) -> List[int]:
        # print("get feed for:", userId)
        # print(self.user_to_tweets)
        # print(self.user_to_following)
        min_heap = []
        for tweet in self.user_to_tweets.get(userId, []):
            heapq.heappush(min_heap, [-1*tweet[0], tweet[1]])
        for followee in self.user_to_following.get(userId,[]):
            for tweet in self.user_to_tweets.get(followee, []):
                heapq.heappush(min_heap, [-1*tweet[0], tweet[1]])
        # print("heap of tweets:", min_heap)
        res = []
        while len(res) < 10 and min_heap:
            res.append(min_heap[0][1])
            heapq.heappop(min_heap)
        return res
        

    def follow(self, followerId: int, followeeId: int) -> None:
        #follower is following followee
        if followerId not in self.user_to_following:
            self.user_to_following[followerId] = []
        if followeeId in self.user_to_following[followerId]:
            return
        self.user_to_following[followerId].append(followeeId)

        

    def unfollow(self, followerId: int, followeeId: int) -> None:
        if followerId not in self.user_to_following:
            return
        self.user_to_following[followerId].remove(followeeId)
        


# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)