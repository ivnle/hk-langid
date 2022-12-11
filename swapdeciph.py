# Python reimplementation of Trial Decipherment i.e. TopSwapDeciph
import re
import random
import math

def TopSwapDeciph(
    counts_c,
    counts_p,
    restarts=0,
    skip_heuristic=0,
    iterations=100,
    factor=1,
    num_bigrams=0
):
  print "[TOP SWAP DECIPH]\t" if num_bigrams else "[ALL SWAP DECIPH]\t"
  random.seed(19901020)

    # Get frequency orders, and remove unwanted characters.
  order_c = sorted(counts_c[1], key=counts_c[1].get, reverse=True)
  for i in range(len(order_c)):
    if order_c[i] == '_' or re.search('\s', order_c[i]) or order_c[i] == '‐':
      del order_c[i]
  order_p = sorted(counts_p[1], key=counts_p[1].get, reverse=True)
  for i in range(len(order_p)):
    if order_p[i] == '_' or re.search('\s', order_p[i]) or order_p[i] == '‐':
      del order_p[i]

    # Apply the alphabet size heuristic.
    min_alph_size = len(order_c) if len(order_c) < len(order_p) else len(order_p)
    if skip_heuristic and (len(order_p)*1.5 < len(order_c) or len(order_p)*0.25 > len(order_c)):
        return ({}, float("-inf"), -1)
    
    # Pad the plaintext alphabet with dashes, as needed.
    if len(order_p) < len(order_c):
        counts_p[1]['-'] = 1
        counts_p[0] += 1
    while len(order_p) < len(order_c):
        order_p.append('-')
    
    # Compute the probabilities of all bigrams.
    probs_p = {}
    for p1 in counts_p[1].keys():
        for p2 in counts_p[1].keys():
            probs_p[p1][p2] = math.log(0.9 *
                                        counts_p[2][p1][p2] / 
                                        counts_p[1][p1]
                                        +
                                        0.1 *
                                        counts_p[1][p2] /
                                        counts_p[0]
                                        )
            assert probs_p[p1][p2] < 0

    # Get frequency mapping key and evaluate it; this is our default key.
    key = {'_': '_'}
    for i in xrange(len(order_c)):
        key[order_c[i]] = order_p[i]
    bestkey = key
    bestscore = GetDeciphScoreKey(bestkey, counts_c, probs_p)
    bestiter = -1

    # Perform an initial run and random restarts.
    for iter in range(restarts+1):
        if iter > 0:
        # All iterations except 0 are random restarts.
            order_p = Scramble(order_p)

        # Initialize the key we will optimize this iteration.
        iterkey = {'_' : '_'}
        for i in range(len(order_c)):
            iterkey[order_c[i]] = order_p[i]
        iterscore = GetDeciphScoreKey(iterkey, counts_c, probs_p)

        # Take some number of steps "uphill".
        steps = iterations if iterations else factor*min_alph_size
        for _ in range(steps):
            bestnewkey = {}
            bestnewscore = -inf
            seen = {}

            if num_bigrams:
            # Rank the bigrams in the decipherment.
                bigrams_in_decipherment = {}
                for c1 in counts_c[2].keys():
                    if c1 == '_':
                        continue
                    d1 = iterkey[c1]
                    for c2 in counts_c[2][c1].keys():
                        if c2 == '_':
                            continue
                        d2 = iterkey[c2]
                        assert d2
                        bigrams_in_decipherment[c1+c2] = counts_p[2][d1][d2] or 0
                
                sorted_bigrams = sorted(bigrams_in_decipherment, key=lambda x: bigrams_in_decipherment[x])

                # Find the letters we need to swap.
                needtoswap = {}
                for i in range(num_bigrams) and i < len(sorted_bigrams):
                    needtoswap[sorted_bigrams[i][0]] = 1
                    needtoswap[sorted_bigrams[i][1]] = 1
                
                
                # Swap all letters we %needtoswap with all other letters,
                # and find the best resulting key.
                for i in range(len(order_c)):
                    c1 = order_c[i]
                    if not needtoswap.has_key(c1):
                        continue
                    if c1 == '_':
                        continue
                
                    for j in range(len(order_c)):
                        c2 = order_c[j]
                        if needtoswap[c2] and j <= i:
                            continue
                        if c2 == '_':
                            continue
                    
                        newkey = iterkey[:]
                        newkey[c1], newkey[c2] = newkey[c2], newkey[c1]
                        newscore = GetSwapScore(newkey, counts_c, probs_p, iterscore, c1, c2)
                        if newscore > bestnewscore:
                            bestnewkey = newkey[:]
                            bestnewscore = newscore
    
    return bestkey, bestscore, bestiter