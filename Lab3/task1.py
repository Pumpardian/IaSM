from random import random
from typing import NamedTuple
import scipy
import sympy as sp
import numpy as np
from scipy.stats import norm, chi2

class IRV(NamedTuple):
    func: callable
    x1: float
    x2: float
    y1: float
    y2: float

def run_task():
    function_string = "1/2 * sin(x + y)"
    function_sp = sp.simplify(function_string)
    func = sp.lambdify(sp.symbols("x, y"), function_sp) # density
    x_sym, y_sym = sp.symbols("x y")

    irv = IRV(func, float(0), float(sp.pi/2), float(0), float(sp.pi/2))
    irv_distribution_func = sp.integrate(function_sp, (x_sym, irv.x1, x_sym), (y_sym, irv.y1, y_sym))
    Func = sp.lambdify((x_sym, y_sym), irv_distribution_func) # distribution

    # plot part
    node_count = 16
    x_list = np.linspace(irv.x1, irv.x2, node_count)
    y_list = np.linspace(irv.y1, irv.y2, node_count)
    X, Y = np.meshgrid(x_list, y_list)
    Z1 = func(X, Y) # density mesh
    Z2 = Func(X, Y) # distribution mesh

    # disrtibution integral = 1 check
    integral_value = sp.integrate(function_sp, (x_sym, irv.x1, irv.x2), (y_sym, irv.y1, irv.y2))

    # marginal densities & indep check
    f_x_sp = sp.integrate(function_sp, (y_sym, irv.y1, irv.y2))
    f_x = sp.lambdify(x_sym, f_x_sp)
    f_y_sp = sp.integrate(function_sp, (x_sym, irv.x1, irv.x2))
    f_y = sp.lambdify(y_sym, f_y_sp)

    multiplied_sp = sp.Mul(f_x_sp, f_y_sp)
    multiplied = sp.lambdify((x_sym, y_sym), multiplied_sp)

    # f(x, y) - f(x)*f(y)
    Z3 = func(X, Y) - multiplied(X, Y) # difference mesh

    # conditional densities
    f_x_pipe_y_sp = function_sp / f_y_sp
    f_y_pipe_x_sp = function_sp / f_x_sp

    # sample
    sample_size = 1_000_000
    def generate_sample(irv: IRV, sample_size=sample_size):
        sample = [] # z*M < f(x,y) M=1
        while len(sample) < sample_size:
            x = irv.x1 + random() * (irv.x2 - irv.x1)
            y = irv.y1 + random() * (irv.y2 - irv.y1)
            z = random()
            if z < irv.func(x, y):
                sample.append((x, y))
        return sample

    sample = generate_sample(irv)
    x_sample = [val[0] for val in sample]
    y_sample = [val[1] for val in sample]

    # value characteristics (mean, variance, corelation)
    expected_mean = (scipy.integrate.dblquad(lambda x, y: x * func(x, y), irv.x1, irv.x2, irv.y1, irv.y2)[0],
        scipy.integrate.dblquad(lambda x, y: y * func(x, y), irv.x1, irv.x2, irv.y1, irv.y2)[0]
    )
    observed_mean = (np.mean(x_sample),np.mean(y_sample),)

    expected_variance = (scipy.integrate.dblquad(lambda x, y: (x - expected_mean[0])**2 * func(x, y), irv.x1, irv.x2, irv.y1, irv.y2,)[0],
        scipy.integrate.dblquad(lambda x, y: (y - expected_mean[1])**2 * func(x, y), irv.x1, irv.x2, irv.y1, irv.y2,)[0],
    )
    observed_variance = (np.var(x_sample),np.var(y_sample),)

    expected_r_xy = scipy.integrate.dblquad(lambda x, y: ((x - expected_mean[0]) * (y - expected_mean[1]) * func(x, y)),
                                            irv.x1, irv.x2, irv.y1, irv.y2)[0] / np.sqrt(expected_variance[0] * expected_variance[1])
    x_sample_centered = x_sample - observed_mean[0]
    y_sample_centered = y_sample - observed_mean[1]
    observed_r_xy = ((x_sample_centered @ y_sample_centered) / (len(x_sample) * np.sqrt(observed_variance[0] * observed_variance[1])))

    gamma = 0.975

    def get_delta(offset):
        t = norm.ppf(gamma / 2 + 0.5)
        return t * offset / np.sqrt(sample_size)

    def get_offset_delta(test_offset):
        alphas = ((1 - gamma) / 2, (1 + gamma) / 2)
        chis = (chi2.isf(alphas, sample_size - 1))
        temp = np.sqrt(sample_size - 1) * test_offset
        return (temp / np.sqrt(chis[0]), temp / np.sqrt(chis[1]))

    theoretical_std_deviation_x = expected_variance[0]**0.5
    theoretical_std_deviation_y = expected_variance[1]**0.5
    sample_std_deviation_x = observed_variance[0]**0.5
    sample_std_deviation_y = observed_variance[1]**0.5

    delta_x = get_delta(theoretical_std_deviation_x)
    delta_y = get_delta(theoretical_std_deviation_y)
    offset_delta_x = get_offset_delta(sample_std_deviation_x)
    offset_delta_y = get_offset_delta(sample_std_deviation_y)
    val_x = np.square(offset_delta_x)
    val_y = np.square(offset_delta_y)

    # 3d plot data
    bins_3d = 30
    H3d, xedges3d, yedges3d = np.histogram2d(
        x_sample, y_sample, bins=bins_3d, density=True
    )
    hist3d_data = (H3d, xedges3d, yedges3d)

    # hypothesis tests
    alpha_sig = 0.05

    # mean: z-test
    z_x = (observed_mean[0] - expected_mean[0]) / (theoretical_std_deviation_x / np.sqrt(sample_size))
    z_y = (observed_mean[1] - expected_mean[1]) / (theoretical_std_deviation_y / np.sqrt(sample_size))
    p_x_mean = 2 * (1 - norm.cdf(abs(z_x)))
    p_y_mean = 2 * (1 - norm.cdf(abs(z_y)))

    # variance: chi^2
    s2_x = np.var(x_sample, ddof=1)
    s2_y = np.var(y_sample, ddof=1)
    chi2_x = (sample_size - 1) * s2_x / expected_variance[0]
    chi2_y = (sample_size - 1) * s2_y / expected_variance[1]
    p_x_var = 2 * min(chi2.cdf(chi2_x, sample_size - 1), 1 - chi2.cdf(chi2_x, sample_size - 1))
    p_y_var = 2 * min(chi2.cdf(chi2_y, sample_size - 1), 1 - chi2.cdf(chi2_y, sample_size - 1))

    # corelation: fisher transform
    zr  = np.arctanh(np.clip(observed_r_xy, -0.999999, 0.999999))
    zr0 = np.arctanh(np.clip(expected_r_xy, -0.999999, 0.999999))
    se_r = 1.0 / np.sqrt(sample_size - 3)
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

    return X, Y, Z1, Z2, Z3, integral_value, multiplied_sp, f_x_pipe_y_sp, f_y_pipe_x_sp, \
            expected_mean, observed_mean, expected_variance, observed_variance, expected_r_xy, observed_r_xy, \
            delta_x, delta_y, val_x, val_y, x_sample, x_list, y_sample, y_list, f_x, f_y, \
            hist3d_data, hypothesis_tests, (irv.x1, irv.x2, irv.y1, irv.y2), func