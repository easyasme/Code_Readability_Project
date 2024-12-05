from collections import defaultdict, deque
import heapq

class Twitter:

    def __init__(self):
        self._friendships = defaultdict(set)
        self._tweets = defaultdict(lambda: deque(maxlen=10))
        self._time = 0

    def postTweet(self, userId: int, tweetId: int) -> None:
        self._tweets[userId].append((self._time, tweetId))
        self._time -= 1

    def getNewsFeed(self, userId: int) -> List[int]:
        heap = list(self._tweets[userId])
        # heapq.heapify(heap)
        for f_id in self._friendships[userId]:
            for el in self._tweets[f_id]:
                heap.append(el)
        heap.sort()
        return [heap[i][1] for i in range(min(10, len(heap)))]
        #         if len(heap) == 10:
        #             heapq.heappushpop(heap, el)
        #         else:
        #             heapq.heappush(heap, el)
        # return [heapq.heappop(heap)[1] for i in range(len(heap))][::-1]


    def follow(self, followerId: int, followeeId: int) -> None:
        self._friendships[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        if followerId in self._friendships:
            if followeeId in self._friendships[followerId]:
                self._friendships[followerId].remove(followeeId)
        


# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)