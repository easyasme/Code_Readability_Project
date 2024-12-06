class Twitter:

    def __init__(self):
        self.heap = []
        heapq.heapify(self.heap)
        self.recentness = 0
        #dictionary key userid and value set  of users
        self.following = {}
        self.cache = {}
        self.did_change= False
        self.prev_get = 0
    def postTweet(self, userId: int, tweetId: int) -> None:
        self.recentness -= 1
        heapq.heappush(self.heap, (self.recentness, userId, tweetId))
        self.did_change= True

    def getNewsFeed(self, userId: int) -> List[int]:
        if self.did_change == False:
            if userId in self.cache:
                if self.prev_get == userId:
                    return self.cache[userId]
        output = []
        add_back = []
        while self.heap:
            recentness, postId, tweetId = heapq.heappop(self.heap)
            add_back.append((recentness, postId, tweetId))
            if userId == postId:
                output.append(tweetId)
            if userId in self.following:
                if self.following[userId]:
                    if postId in self.following[userId]:
                        output.append(tweetId)
            if len(output) == 10:
                break
        for i in range(len(add_back)):
            heapq.heappush(self.heap, (add_back[i][0], add_back[i][1], add_back[i][2]))
        self.cache[userId] = output
        self.did_change= False
        self.prev_get = userId
        return output
    def follow(self, followerId: int, followeeId: int) -> None:
        if followerId not in self.following:
            temp = set([followeeId])
            self.following[followerId] = temp
        else:
            self.following[followerId].add(followeeId)
        self.did_change = True
        # for k,v in self.following.items():
        #     print('k: ', k, 'v: ', v)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        if followerId in self.following:
            if followeeId in self.following[followerId]:
                self.following[followerId].remove(followeeId)
                self.did_change = True

# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)