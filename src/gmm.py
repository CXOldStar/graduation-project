"""This module defines the GMM and contains functions to training.
"""


import numpy as np
import math

import corpus


def gaussian(features, means=np.array([0]), covariances=np.array([[1]])):
    """A multivariate (D features) gaussian pdf.

    @param features: Dx1 vector of features
    @param means: Dx1 vector of means (one for each feature).
    @param covariances: DxD matrix of covariances.

    @returns: a float.
    """
    D = len(features)
    determinant = np.linalg.det(covariances)
    cte = 1 / ((2*math.pi)**(D/2) * determinant**(1/2))
    inverse = np.linalg.inv(covariances)

    #(x - mu)' * inverse * (x - mu)
    #due the structure of array, the A.T is made at the end
    A = np.array([(features - means).tolist()])
    power = np.dot(A, inverse)
    power = np.dot(power, A.T)
    power = (-1/2)*power[0, 0]

    return (cte * math.exp(power))

def create_gmm(M, D):
    """Creates a GMM.

    @param M: number of mixtures.
    @param D: size of features (used to the means and covariances).

    @returns: an untrained GMM.
    """
    weights = np.array([random.uniform(1, 10) for _ in range(M)])
    weights = (1/np.sum(weights)) * weights

    gmm = list()
    for weight in weights:
        means = np.array([random.uniform(5, 10) for _ in range(D)])

        covariances = np.zeros((D, D))
        for i in range(D):
            covariances[i, i] = random.uniform(50*D, 100*D)

        mixture = (weight, means, covariances)
        gmm.append(mixture)

    return gmm

def eval_gmm(gmm, features):
    """Feeds the GMM with the given features.

    @param gmm: the GMM used (a list of (weight, means, covariances));
    @param features: a Dx1 vector of features.

    @returns: the weighted sum of gaussians of gmm.
    """
    prob = 0
    for mixture in gmm:
        (weight, means, covariances) = mixture
        prob = prob + weight*gaussian(features, means, covariances)

    return prob

def eval_avg_gmm(gmms, mfccs):
    D = len(mfccs[:, 0])
    logprob = 0

    for (gmm, features) in zip(gmms, mfccs.T):
        prob = eval_gmm(gmm, features)
        logprob = logprob + math.log(prob, 10)

    T = len(mfccs[0])
    logprob = (1/T) * logprob

    return logprob

#TODO criar funcao para gerar o UBM-GMM e treiná-lo

#TEST
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import random
    from useful import CORPORA_DIR, FEATURES_DIR

    #Showing the 1st MFCC (index ZERO) over time
    mfccs = corpus.read_features(13, 0, 0.97, 'enroll_1', 'f00', 1)
    T = len(mfccs[0])
    fig = plt.figure()
    fig.suptitle('MFCC #0\n1 <= frame <= %d' % T)
    plt.grid(True)
    plt.plot(mfccs[0]) #figure 1
    plt.xlabel('frame')
    plt.ylabel('feature value')

    #Showing random D-featured gaussian over time
    frames = np.linspace(1, T, T)
    value = list()
    for features in mfccs.T:
        #features = features[0 : 1]  #D = 1 (only 1st feature)
        D = len(features)
        means = np.array([random.uniform(5, 10) for _ in range(D)])
        covariances = np.zeros((D, D))
        for i in range(D):
            covariances[i, i] = random.uniform(50*D, 100*D)
        y = gaussian(features, means, covariances)
        value.append(y)
    value = np.array(value)
    fig = plt.figure()
    fig.suptitle('Gaussian for MFCC #0\n1 <= frame <= %d' % T)
    plt.grid(True)
    plt.xlabel('frame')
    plt.ylabel('feature value')
    plt.plot(frames, value) #figure 2

    #Evaluating a GMM with M mixtures for a Dx1 feature vector
    M = 32
    features = mfccs.T[0]
    D = len(features)
    gmm = create_gmm(M, D)
    prob = eval_gmm(gmm, features)
    print(prob)

    #Evaluating one GMMs with M mixtures for a Dx1 feature vector for each frame
    probs = list()
    logprob = 0
    for features in mfccs.T:
        #features = features[0 : 1]  #D = 1 (only 1 feature)
        D = len(features)
        gmm = create_gmm(M, D)
        prob = eval_gmm(gmm, features)
        logprob = logprob + math.log(prob, 10)
        print(prob)
        probs.append(prob)
    T = len(mfccs[0])
    logprob = (1/T) * logprob
    print('T =', T, 'logprob =', logprob)
    probs = np.array(probs)
    fig = plt.figure()
    fig.suptitle('GMMs \n1 <= frame <= %d' % T)
    plt.grid(True)
    plt.xlabel('frame')
    plt.ylabel('prob')
    plt.plot(frames, probs) #figure 3

    gmms = [create_gmm(M, len(features)) for features in mfccs.T]
    print('T =', len(gmms), 'M =', len(gmms[0]))
    logprob = eval_avg_gmm(gmms, mfccs)
    print('logprob =', logprob)

    #plt.show()