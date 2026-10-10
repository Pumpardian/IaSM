import numpy as np
from scipy.stats import chisquare, nbinom
from task1 import MX_practical, DX_practical, CI_MX, CI_DX

def MX_pascal(x, p):
    return x * (1 - p) / p

def DX_pascal(x, p):
    return x * (1 - p) / (p ** 2)

def negative_binomal(r, p, size):
    samples = []
    for _ in range(size):
        successes = 0
        failures = 0
        while successes < r:
            if np.random.rand() < p:
                successes += 1
            else:
                failures += 1
        samples.append(failures)
    
    return np.array(samples)

def check_pascal_distribution(sample, r, p, alpha=0.05):
    
    max_value = np.max(sample)
    
    observed_freq, bin_edges = np.histogram(sample, bins=range(max_value + 2), density=False)
    
    x_values = np.arange(0, max_value + 1)
    expected_prob = nbinom.pmf(x_values, r, p) # r,p -> x probability
    
    expected_freq = expected_prob * len(sample)
    
    observed_freq = observed_freq / np.sum(observed_freq)
    expected_freq = expected_freq / np.sum(expected_freq)

    observed_freq *= len(sample)
    expected_freq *= len(sample)

    non_zero_mask = expected_freq > 0
    observed_freq = observed_freq[non_zero_mask]
    expected_freq = expected_freq[non_zero_mask]
    
    chi2_stat, p_value = chisquare(f_obs=observed_freq, f_exp=expected_freq) 
    
    if p_value > alpha:
        return True
    else:
        return False
    
def solve(n, p, x):
    neg_bin_practical = negative_binomal(x, p, n)\
    
    mx_theory = MX_pascal(x, p)
    dx_theory = DX_pascal(x, p)
    
    mx_practical = MX_practical(neg_bin_practical)
    dx_practical = DX_practical(neg_bin_practical)
    
    ci_mx = CI_MX(neg_bin_practical, 0.975)
    ci_dx = CI_DX(neg_bin_practical, 0.975)
    
    res = check_pascal_distribution(neg_bin_practical, x, p)
    
    if res == False:
        return None, None, None, None, None, None, None
    
    return neg_bin_practical, mx_practical, mx_theory, dx_practical, dx_theory, ci_mx, ci_dx