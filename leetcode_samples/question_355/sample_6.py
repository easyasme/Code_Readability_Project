from collections import deque
import heapq

class Twitter:

    def __init__(self):
        self.following = {}
        self.tweets = {}

        self.tweet_rank = 0

    def postTweet(self, userId: int, tweetId: int) -> None:
        if userId not in self.tweets:
            self.tweets[userId] = deque()

        self.tweets[userId].appendleft([self.tweet_rank, tweetId])

        if len(self.tweets[userId]) > 10:
            self.tweets[userId].pop()

        self.tweet_rank -= 1

    def getNewsFeed(self, userId: int) -> List[int]:
        heap = []

        if userId in self.tweets:
            heap.append((self.tweets[userId][0][0], userId, 0))

        for followee in self.following.get(userId, {}):
            if followee in self.tweets:
                heap.append((self.tweets[followee][0][0], followee, 0))

        heapq.heapify(heap)

        res = []

        while heap and len(res) < 10:
            _, user_id, index = heapq.heappop(heap)

            res.append(self.tweets[user_id][index][1])

            if index + 1 < len(self.tweets[user_id]):
                heapq.heappush(heap, (self.tweets[user_id][index + 1][0], user_id, index + 1))

        return res

    def follow(self, followerId: int, followeeId: int) -> None:
        if followerId not in self.following:
            self.following[followerId] = set()

        self.following[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        self.following.get(followerId, set()).discard(followeeId)

# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)