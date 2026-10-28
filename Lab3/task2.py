import numpy as np
from random import random
from scipy import stats
from scipy.stats import norm, chi2
import math

X = [1, 2, 3, 4, 5]
Y = [10, 20, 30, 40, 50]
P = [   # y1     y2     y3     y4     y5
        [0,     0,     0.05,  0.05,  0.1],   # x1
        [0.025, 0.025, 0.025, 0.025, 0.04],  # x2
        [0.05,  0.025, 0,     0,     0.1],   # x3
        [0.11,  0.07,  0.03,  0.05,  0.055], # x4
        [0.070, 0.05,  0.05,  0,     0]      # x5
]

def run_task():
    # marginal distributions
    p_x = [sum(row) for row in P]
    p_y = [sum(y) for y in zip(*P)]
    P_indep = np.outer(p_x, p_y)

    # conditional distribution
    p_yi = [[P[i][j] / p_x[i] for j in range(len(Y))] for i in range(len(X))]
    p_xi = [[P[i][j] / p_y[j] for i in range(len(X))] for j in range(len(Y))]
    
    # distribution functions
    F_x = np.cumsum(p_x)
    F_y = [np.cumsum(p_yi[i]) for i in range(len(Y))]

    def get_var_and_index(x, F_x, p):
        return next((x[i], i) for i, p_ in enumerate(F_x) if p_ >= p)

    # sample
    n = 10000
    x_l, y_l = [], []
    for _ in range(n):
        x, i = get_var_and_index(X, F_x, random())
        x_l.append(x)
        y_l.append(get_var_and_index(Y, F_y[i], random())[0])

    # imperical probabilities
    p_x_imp = [x_l.count(X[i]) / n for i in range(len(X))]
    p_y_imp = [y_l.count(Y[i]) / n for i in range(len(Y))]

    # joint imperical probabilities (for 3d diagram)
    p_xy_imp = np.zeros((len(X), len(Y)))
    for xi, yi in zip(x_l, y_l):
        p_xy_imp[X.index(xi), Y.index(yi)] += 1
    p_xy_imp /= n

    # value characteristics (mean, variance, corelation)
    r_theo = lambda M_xy, M_x, M_y, D_x, D_y: (M_xy - M_x * M_y) / math.sqrt(D_x * D_y)
    M_f = lambda v, p_v: sum([v[i] * p_v[i] for i in range(len(v))])
    def D_f(v, p_v, M=None):
        if M is None:
            M = M_f(v, p_v)
        return sum([(v[i] ** 2) * p_v[i] for i in range(len(v))]) - M ** 2

    M_x = M_f(X, p_x)
    M_y = M_f(Y, p_y)
    M_xy = sum([
        sum([x * y * P[i][j] for j, y in enumerate(Y)])
        for i, x in enumerate(X)
    ])
    D_x = D_f(X, p_x, M_x)
    D_y = D_f(Y, p_y, M_y)
    r_xy = r_theo(M_xy, M_x, M_y, D_x, D_y)
    r = stats.pearsonr(x_l, y_l)[0]

    # hypothesis tests
    alpha_sig = 0.05
    x_arr = np.array(x_l, dtype=float)
    y_arr = np.array(y_l, dtype=float)

    # mean: z-test
    sig_x = math.sqrt(D_x)
    sig_y = math.sqrt(D_y)
    z_x = (M_f(X, p_x_imp) - M_x) / (sig_x / math.sqrt(n))
    z_y = (M_f(Y, p_y_imp) - M_y) / (sig_y / math.sqrt(n))
    p_x_mean = 2 * (1 - norm.cdf(abs(z_x)))
    p_y_mean = 2 * (1 - norm.cdf(abs(z_y)))

    # variance: chi^2
    s2_x = np.var(x_arr, ddof=1)
    s2_y = np.var(y_arr, ddof=1)
    chi2_x = (n - 1) * s2_x / D_x
    chi2_y = (n - 1) * s2_y / D_y
    p_x_var = 2 * min(chi2.cdf(chi2_x, n - 1), 1 - chi2.cdf(chi2_x, n - 1))
    p_y_var = 2 * min(chi2.cdf(chi2_y, n - 1), 1 - chi2.cdf(chi2_y, n - 1))

    # corelation: fisher transform
    zr  = np.arctanh(np.clip(r,   -0.999999, 0.999999))
    zr0 = np.arctanh(np.clip(r_xy,-0.999999, 0.999999))
    se_r = 1.0 / math.sqrt(n - 3)
    z_corr = (zr - zr0) / se_r
    p_corr = 2 * (1 - norm.cdf(abs(z_corr)))

    hypothesis_tests = {
        'alpha': alpha_sig,
        'tests': [
            ("M[x]",  z_x,    p_x_mean),
            ("M[y]",  z_y,    p_y_mean),
            ("D[x]",  chi2_x, p_x_var),
            ("D[y]",  chi2_y, p_y_var),
            ("r_xy",  z_corr, p_corr),
        ],
    }

    return M_x, M_y, D_x, D_y, r_xy, r, X, Y, p_x, p_y, P_indep, p_x_imp, p_y_imp, x_l, y_l, M_f, D_f, \
            p_xy_imp, hypothesis_tests, p_xi, p_yi