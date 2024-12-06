class Twitter:
    globalTime = 1

    def __init__(self):
        self.tweets = defaultdict(list) # reverse order
        self.followed = defaultdict(set)

    def postTweet(self, userId: int, tweetId: int) -> None:
        self.followed[userId].add(userId)
        self.tweets[userId].append((Twitter.globalTime, tweetId))
        Twitter.globalTime += 1

    def getNewsFeed(self, userId: int) -> List[int]:
        newsFeed = []
        # print(self.followed[userId])
        # print(userId)
        for followedUser in self.followed[userId]:
            newsFeed.extend(self.tweets[followedUser][-10:])
        
        return [recTwt[1] for recTwt in heapq.nlargest(10, newsFeed)]

    def follow(self, followerId: int, followeeId: int) -> None:
        self.followed[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        self.followed[followerId].remove(followeeId) if followeeId in self.followed[followerId] else None
        

# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)