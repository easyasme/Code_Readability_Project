from collections import deque, defaultdict

class Twitter:
    def __init__(self):
        self.timestamp = 0
        self.posts = defaultdict(list)
        self.followees = defaultdict(set)

    def postTweet(self, userId: int, tweetId: int) -> None:
        self.posts[userId].append((self.timestamp, tweetId))
        self.timestamp -= 1


    def getNewsFeed(self, userId: int) -> List[int]:
        users = self.followees[userId]
        users.add(userId)
        output = []

        for user in users:
            output.extend(self.posts[user])
        output.sort()

        result = []
        length = min(len(output), 10)
        for i in range(length):
            result.append(output[i][1])
        return result

    def follow(self, followerId: int, followeeId: int) -> None:
        self.followees[followerId].add(followeeId)
        
    def unfollow(self, followerId: int, followeeId: int) -> None:
        if followeeId not in self.followees[followerId]:
            return

        self.followees[followerId].remove(followeeId)
        


# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)