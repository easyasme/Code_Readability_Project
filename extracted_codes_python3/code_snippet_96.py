#!/usr/bin/env python3 -i
from __future__ import print_function
import ple
import numpy as np
import keras
import random
import copy
from pprint import pprint
import matplotlib.pyplot as plt

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import Adam

CREEPS = 10


class Agent():
    """Q learning agent."""

    def __init__(self, actions, max_memory=1000, gamma=.95):
        """Initialize the agent.
        
        :param list actions: A list with all the available actions
        :param int max_memory: The upper limit for out memory
        :param int gamma: Discount factor for the future rewards
        :param int epsilor: Exploration rate. How likely we are to choose
                            a random action instead of the best one
        :param int epsilon_min: The minimum value for the epsilon
        :param int epsilon_decat: How will the epsilon decay over time
        :param int learning_rate: The learning rate of the model
        """
        self._actions = actions
        self._max_memory = max_memory
        self._gamma=gamma
        self._epsilon = 1.0  # exploration rate
        self._epsilon_min = 0.01
        self._epsilon_decay = 0.995
        self._learning_rate = 0.001

        self._model = None
        self.prepare_model()

        # memory of frames
        self._memory = []

    @property
    def memory(self):
        """Return a copy of the internal memory"""
        return copy.deepcopy(self._memory)

    @property
    def max_memory(self):
        """Return the max_memory limit."""
        return self._max_memory

    @property
    def actions(self):
        """Return the actions."""
        return copy.deepcopy(self._actions)
    
    def add_memory(self, memory):
        """Add a new state to the memory."""
        
        # make sure that the states are processed
        state, action, reward, next_state, done = memory
        self._memory.append((
            self.preprocess_state(state),
            action,
            reward,
            self.preprocess_state(next_state),
            done,
        ))

        while len(self._memory) > self._max_memory:
            # remove the latest memory until we get back to the maximum
            # capacity
            self._memory.pop(0)


    def prepare_model(self):
        """Prepare the NN model."""
        self._model = Sequential()
        self._model.add(
            Dense(164,
                  kernel_initializer='lecun_uniform',
                  # 3 coordinates for every creep (x, y, type)
                  # and two more for the player position
                  input_shape=(CREEPS*3+2, )
                 )
            )
        self._model.add(Activation('relu'))

        self._model.add(Dense(150,
                              kernel_initializer='lecun_uniform'))
        self._model.add(Activation('relu'))

        self._model.add(Dense(len(self._actions),
                              kernel_initializer='lecun_uniform'))

        #linear output so we can have range of real-valued outputs
        self._model.add(Activation('linear'))

        self._model.compile(loss='mse', optimizer=Adam())

    @staticmethod
    def preprocess_state(game_state):
        """Process the state in a simpler format for the network.

        Basically have an array with triples like this:
          (x, y, type)
        where type is -1 if that is a bad creep or +1 for a good creep

        The last 2 elements are the position of out player.
        """
        out = []
        for creep_x, creep_y in game_state['creep_pos']['BAD']:
            out.extend([creep_x, creep_y, -1])
        for creep_x, creep_y in game_state['creep_pos']['GOOD']:
            out.extend([creep_x, creep_y, 1])
        out.extend([game_state['player_x'], game_state['player_y']])
        return np.array([out])


    def pick_action(self, reward, obs):
        
        # with a probability choose a random action
        if np.random.rand() <= self._epsilon: 
            return random.choice(self._actions)

        # if we don't choose a random action

        # pre-process the state
        state = self.preprocess_state(obs)

        # predict the Q values for all the actins
        pred = self._model.predict(state)

        # chose the action with the highest Q value
        return self._actions[np.argmax(pred)]

    def replay(self, batch_size=32):
        """Replay the memory and train the model."""
        # print("Replay {} from {}".format(batch_size, len(self._memory)))
        minibatch = random.sample(self._memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            # if the game is done assume only the immediate reward
            target = reward

            # if the game is not done
            if not done:
                # add the current reward + ne next reward predicted by the network
                # discounted by a factor (gamma)
                target = reward + self._gamma * np.argmax(self._model.predict(next_state))

            # compute the output for the current state
            target_f = self._model.predict(state)

            # change only the spot for the reward that we choose
            # with the target reward
            target_f[0, self._actions.index(action)] = target

            # train the model so that starting from the base state
            # it will approximate the reward for the action that it took
            # closer to the target (what we estimate in practice by running the
            # simulation)
            self._model.fit(state, target_f, epochs=1, verbose=0)

        # if the exploration factor is still not at minimum
        if self._epsilon > self._epsilon_min:
            # decay the exploration factor once
            self._epsilon *= self._epsilon_decay

if __name__ == "__main__":
    print("Start ")
    game = ple.games.waterworld.WaterWorld(
        width=480, height=480, num_creeps=CREEPS, 
    )
    env = ple.PLE(game, fps=30*4, display_screen=False)

    agent = Agent(actions=env.getActionSet())

    env.init()

    # nb_frames = 2000
    nb_frames = 150000
    max_noops = 20
    rewards = []
    reward = 0.0
    old_reward = 0.0

    # start our training loop
    for f in range(nb_frames):
        # if the game is over, reset the game
        # we don't care about the "won" games and we don't count them
        # as the game can continue indefinitely we are only concerned with the
        # amount of frames
        if env.game_over():
            print("Finished a game !")
            env.reset_game()

        # get the action
        current_state = game.getGameState()
        action = agent.pick_action(reward, current_state)

        reward = env.act(action)
        old_reward += reward

        # keep the rewars
        rewards.append(old_reward)

        next_state = game.getGameState()
        agent.add_memory((current_state, action, reward, next_state, env.game_over()))
            
        if f % 100 == 0 and f > 0:
            agent.replay()
        if f % 1000 == 0 and f > 0:
            print("Run ", int(f/1000))


        # if f % 50 == 0:
        #     p.saveScreen("screen_capture.png")

    plt.plot(rewards)
    plt.ylabel("Rewards")
    plt.show()
    print("Done ----")
