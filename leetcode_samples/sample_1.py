class Twitter:

    def __init__(self):
        self.users = defaultdict(set)
        self.tweets = defaultdict(list)
        self.count = 0

    def postTweet(self, userId: int, tweetId: int) -> None:
        # add new tweet to tweets list
        self.tweets[userId].append([self.count, tweetId])
        self.count -= 1

    def getNewsFeed(self, userId: int) -> List[int]:
        news = []
        maxHeap = []

        # add yourself in your followee list
        self.users[userId].add(userId)

        # get the most recent tweet from all followees of the user
        for followeeId in self.users[userId]:
            if followeeId in self.tweets:
                index = len(self.tweets[followeeId]) - 1
                count, tweetId = self.tweets[followeeId][index]
                maxHeap.append([count, tweetId, followeeId, index-1])
        
        heapq.heapify(maxHeap)

        # add 10 most recent tweets
        while maxHeap and len(news) < 10:
            # add most recent tweet to news
            count, tweetId, followeeId, index = heapq.heappop(maxHeap)
            news.append(tweetId)
            # check if the followee still has tweets
            if index >= 0:
                # add their next most recent tweet
                count, tweetId = self.tweets[followeeId][index]
                heapq.heappush(maxHeap, [count, tweetId, followeeId, index-1])

        return news


    def follow(self, followerId: int, followeeId: int) -> None:
        # add folower sna followee
        self.users[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        if followerId in self.users:
            # remove followw from follower
            self.users[followerId].remove(followeeId)
        


# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)