#######################################################################
# Copyright (C) 2016 Shangtong Zhang(zhangshangtong.cpp@gmail.com)    #
# Permission given to modify the code as long as you keep this        #
# declaration at the top                                              #
#######################################################################

import matplotlib.pyplot as plt
import numpy as np
from utils import *
import seaborn as sns

class Bandit:
    # @kArm: # of arms
    # @epsilon: probability for exploration in epsilon-greedy algorithm
    # @initial: initial estimation for each action
    # @stepSize: constant step size for updating estimations
    # @sampleAverages: if True, use sample averages to update estimations instead of constant step size
    # @UCB: if not None, use UCB algorithm to select action
    # @gradient: if True, use gradient based bandit algorithm
    # @gradientBaseline: if True, use average reward as baseline for gradient based bandit algorithm
    def __init__(self, kArm=10, epsilon=0, initial=0, stepSize=0.1, sampleAverages=False, UCBParam=None,
                 gradient=False, gradientBaseline=False, trueReward=0):
        self.k = kArm
        self.stepSize = stepSize
        self.sampleAverages = sampleAverages
        self.indices = np.arange(self.k)
        self.time = 0
        self.UCBParam = UCBParam
        self.gradient = gradient
        self.gradientBaseline = gradientBaseline
        self.averageReward = 0
        self.trueReward = trueReward

        # real reward for each action
        self.qTrue = []

        # estimation for each action
        self.qEst = np.zeros(self.k)

        # # of chosen times for each action
        self.actionCount = []

        self.epsilon = epsilon

        # initialize real rewards with N(0,1) distribution and estimations with desired initial value
        for i in range(0, self.k):
            self.qTrue.append(np.random.randn() + trueReward)
            self.qEst[i] = initial
            self.actionCount.append(0)

        self.bestAction = np.argmax(self.qTrue)

    # get an action for this bandit, explore or exploit?
    def getAction(self):
        # explore
        if self.epsilon > 0:
            if np.random.binomial(1, self.epsilon) == 1:
                np.random.shuffle(self.indices)
                return self.indices[0]

        # exploit
        if self.UCBParam is not None:
            UCBEst = self.qEst + \
                     self.UCBParam * np.sqrt(np.log(self.time + 1) / (np.asarray(self.actionCount) + 1))
            return argmax(UCBEst)
        if self.gradient:
            expEst = np.exp(self.qEst)
            self.actionProb = expEst / np.sum(expEst)
            return np.random.choice(self.indices, p=self.actionProb)
        return argmax(self.qEst)

    # take an action, update estimation for this action
    def takeAction(self, action):
        # generate the reward under N(real reward, 1)
        reward = np.random.randn() + self.qTrue[action]
        self.time += 1
        self.averageReward = (self.time - 1.0) / self.time * self.averageReward + reward / self.time
        self.actionCount[action] += 1

        if self.sampleAverages:
            # update estimation using sample averages
            self.qEst[action] += 1.0 / self.actionCount[action] * (reward - self.qEst[action])
        elif self.gradient:
            oneHot = np.zeros(self.k)
            oneHot[action] = 1
            if self.gradientBaseline:
                baseline = self.averageReward
            else:
                baseline = 0
            self.qEst = self.qEst + self.stepSize * (reward - baseline) * (oneHot - self.actionProb)
        else:
            # update estimation with constant step size
            self.qEst[action] += self.stepSize * (reward - self.qEst[action])
        return reward

figureIndex = 0

# for figure 2.1
def figure2_1():
    global figureIndex
    plt.figure(figureIndex)
    figureIndex += 1
    sns.violinplot(data=np.random.randn(200,10) + np.random.randn(10))
    plt.xlabel("Action")
    plt.ylabel("Reward distribution")
    plt.show()

# for figure 2.2
def epsilonGreedy(nBandits, time):
    epsilons = [0, 0.1, 0.01]
    bandits = [[], [], []]
    bestActionCounts = [np.zeros(time, dtype='float') for _ in range(0, len(epsilons))]
    averageRewards = [np.zeros(time, dtype='float') for _ in range(0, len(epsilons))]
    for i, eps in zip(range(0, len(epsilons)), epsilons):
        for j in range(0, nBandits):
            bandits[i].append(Bandit(epsilon=eps, sampleAverages=True))
    for epsInd in range(0, len(epsilons)):
        for i in range(0, nBandits):
            for t in range(0, time):
                action = bandits[epsInd][i].getAction()
                reward = bandits[epsInd][i].takeAction(action)
                averageRewards[epsInd][t] += reward
                if action == bandits[epsInd][i].bestAction:
                    bestActionCounts[epsInd][t] += 1
    global figureIndex
    plt.figure(figureIndex)
    figureIndex += 1
    for eps, counts in zip(epsilons, bestActionCounts):
        counts /= nBandits
        plt.plot(counts, label='epsilon = '+str(eps))
    plt.xlabel('Steps')
    plt.ylabel('% optimal action')
    plt.legend()
    plt.figure(figureIndex)
    figureIndex += 1
    for eps, rewards in zip(epsilons, averageRewards):
        rewards /= nBandits
        plt.plot(rewards, label='epsilon = '+str(eps))
    plt.xlabel('Steps')
    plt.ylabel('average reward')
    plt.legend()

# for figure 2.3
def optimisticInitialValues(nBandits, time):
    bandits = [[], []]
    bestActionCounts = [np.zeros(time, dtype='float') for _ in range(0, len(bandits))]
    bandits[0] = [Bandit(epsilon=0, initial=5, stepSize=0.1) for _ in range(0, nBandits)]
    bandits[1] = [Bandit(epsilon=0.1, initial=0, stepSize=0.1) for _ in range(0, nBandits)]
    for banditInd in range(0, len(bandits)):
        for i in range(0, nBandits):
            for t in range(0, time):
                action = bandits[banditInd][i].getAction()
                bandits[banditInd][i].takeAction(action)
                if action == bandits[banditInd][i].bestAction:
                    bestActionCounts[banditInd][t] += 1
    bestActionCounts[0] /= nBandits
    bestActionCounts[1] /= nBandits
    global figureIndex
    plt.figure(figureIndex)
    figureIndex += 1
    plt.plot(bestActionCounts[0], label='epsilon = 0, q = 5')
    plt.plot(bestActionCounts[1], label='epsilon = 0.1, q = 0')
    plt.xlabel('Steps')
    plt.ylabel('% optimal action')
    plt.legend()

# for figure 2.4
def ucb(nBandits, time):
    bandits = [[], []]
    averageRewards = [np.zeros(time, dtype='float') for _ in range(0, len(bandits))]
    bandits[0] = [Bandit(epsilon=0, stepSize=0.1, UCBParam=2) for _ in range(0, nBandits)]
    bandits[1] = [Bandit(epsilon=0.1, stepSize=0.1) for _ in range(0, nBandits)]
    for banditInd in range(0, len(bandits)):
        for i in range(0, nBandits):
            for t in range(0, time):
                action = bandits[banditInd][i].getAction()
                reward = bandits[banditInd][i].takeAction(action)
                averageRewards[banditInd][t] += reward
    averageRewards[0] /= nBandits
    averageRewards[1] /= nBandits
    global figureIndex
    plt.figure(figureIndex)
    figureIndex += 1
    plt.plot(averageRewards[0], label='UCB c = 2')
    plt.plot(averageRewards[1], label='epsilon greedy epsilon = 0.1')
    plt.xlabel('Steps')
    plt.ylabel('Average reward')
    plt.legend()

# for figure 2.5
def gradientBandit(nBandits, time):
    bandits =[[], [], [], []]
    bandits[0] = [Bandit(gradient=True, stepSize=0.1, gradientBaseline=True, trueReward=4) for _ in range(0, nBandits)]
    bandits[1] = [Bandit(gradient=True, stepSize=0.1, gradientBaseline=False, trueReward=4) for _ in range(0, nBandits)]
    bandits[2] = [Bandit(gradient=True, stepSize=0.4, gradientBaseline=True, trueReward=4) for _ in range(0, nBandits)]
    bandits[3] = [Bandit(gradient=True, stepSize=0.4, gradientBaseline=False, trueReward=4) for _ in range(0, nBandits)]
    bestActionCounts = [np.zeros(time, dtype='float') for _ in range(0, len(bandits))]
    for banditInd in range(0, len(bandits)):
        for i in range(0, nBandits):
            for t in range(0, time):
                action = bandits[banditInd][i].getAction()
                bandits[banditInd][i].takeAction(action)
                if action == bandits[banditInd][i].bestAction:
                    bestActionCounts[banditInd][t] += 1
    for counts in bestActionCounts:
        counts /= nBandits
    labels = ['alpha = 0.1, with baseline',
              'alpha = 0.1, without baseline',
              'alpha = 0.4, with baseline',
              'alpha = 0.4, without baseline']
    global figureIndex
    plt.figure(figureIndex)
    figureIndex += 1
    for i in range(0, len(bandits)):
        plt.plot(bestActionCounts[i], label=labels[i])
    plt.xlabel('Steps')
    plt.ylabel('% Optimal action')
    plt.legend()

# Figure 2.6
def figure2_6(nBandits, time):
    labels = ['epsilon-greedy', 'gradient bandit',
              'UCB', 'optimistic initialization']
    generators = [lambda epsilon: Bandit(epsilon=epsilon, sampleAverages=True),
                  lambda alpha: Bandit(gradient=True, stepSize=alpha, gradientBaseline=True),
                  lambda coef: Bandit(epsilon=0, stepSize=0.1, UCBParam=coef),
                  lambda initial: Bandit(epsilon=0, initial=initial, stepSize=0.1)]
    parameters = [np.arange(-7, -1),
                  np.arange(-5, 2),
                  np.arange(-4, 3),
                  np.arange(-2, 3)]
    averageRewards = []
    for i in range(len(labels)):
        averageRewards.append([])
        for param_ in parameters[i]:
            param = pow(2, param_)
            reward = 0.0
            for banditIndex in range(nBandits):
                bandit = generators[i](param)
                print labels[i], 'parameter:', param, str(banditIndex) + 'th bandit'
                for step in range(time):
                    action = bandit.getAction()
                    reward += bandit.takeAction(action)
            reward /= nBandits * time
            averageRewards[-1].append(reward)

    global figureIndex
    plt.figure(figureIndex)
    figureIndex += 1
    for i in range(len(labels)):
        plt.plot(parameters[i], averageRewards[i], label=labels[i])
    plt.xlabel('Parameter(2^x)')
    plt.ylabel('Average reward')
    plt.legend()


# epsilonGreedy(200, 1000)
# optimisticInitialValues(200, 1000)
# ucb(1000, 1000)
# gradientBandit(200, 1000)
figure2_1()
figure2_6(200, 1000)
plt.show()
