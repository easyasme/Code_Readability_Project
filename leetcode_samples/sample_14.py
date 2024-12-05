from collections import defaultdict
from typing import List

class Twitter:
    globalTime = 0
    PARTITION_CAPACITY = 10  # Capacity for each sublist partition

    def __init__(self):
        self.tweets = defaultdict(list)  # {userId: [(timestamp, tweetId)]}
        self.newsFeed = defaultdict(list)  # {userId: [sorted_sublist]}
        self.followed = defaultdict(set)  # {followerId: {followeeId}}
        self.followedBy = defaultdict(set)  # {followeeId: {followerId}}

    def postTweet(self, userId: int, tweetId: int) -> None:
        """Post a new tweet."""
        Twitter.globalTime += 1
        new_tweet = (Twitter.globalTime, tweetId)
        self.tweets[userId].append(new_tweet)
        
        # Update the news feed for the user and all their followers
        for follower in self.followedBy[userId] | {userId}:
            # Optimization: Directly append the latest tweet in its own sublist
            self.newsFeed[follower].append([new_tweet])

    def getNewsFeed(self, userId: int) -> List[int]:
        """Retrieve the 10 most recent tweets for a user."""
        # Flatten and sort the tweets from all partitions
        feed = []
        for partition in self.newsFeed[userId]:
            feed.extend(partition)
        
        # Sort by timestamp descending and take the top 10
        feed.sort(reverse=True, key=lambda x: x[0])
        return [tweetId for _, tweetId in feed[:10]]


    def follow(self, followerId: int, followeeId: int) -> None:
        """Follow a user."""
        if followeeId not in self.followed[followerId]:
            self.followed[followerId].add(followeeId)
            self.followedBy[followeeId].add(followerId)
            
            # Add all existing tweets from the followee to the follower's news feed
            for tweet in self.tweets[followeeId]:
                self.newsFeed[followerId].append([tweet])

    def unfollow(self, followerId: int, followeeId: int) -> None:
        """Unfollow a user."""
        if followeeId in self.followed[followerId]:
            self.followed[followerId].remove(followeeId)
            self.followedBy[followeeId].remove(followerId)
            
            # Remove all tweets from the unfollowed user
            self.newsFeed[followerId] = [
                [tweet for tweet in partition if tweet[1] not in {t[1] for t in self.tweets[followeeId]}]
                for partition in self.newsFeed[followerId]
            ]
