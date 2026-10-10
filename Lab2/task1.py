import random
import numpy as np
import sympy as sp
from scipy import stats
from scipy.stats import chi2, norm

def generate_data(f, y, n):
    result = []
    for _ in range(n):
        number = random.random()
        result.append(float(f.subs(y, number)))
    return result

def MX_practical(data):
    return sum(data)/len(data)

def MX_theory(f):
    x = sp.symbols('x')
    return sp.integrate(x * f, (x, 0, 1))

def DX_practical(data):
    MX = MX_practical(data)
    return sum((X_i - MX) ** 2 for X_i in data) / (len(data) - 1)

def DX_theory(f):
    x = sp.symbols('x')
    return float(sp.integrate(x ** 2 * f, (x, 0, 1))) - MX_theory(f) ** 2

def CI_MX(data, confidence):
    MX = MX_practical(data)
    DX = DX_practical(data)
    delta = norm.ppf(confidence) / np.sqrt(len(data))
    return float(MX - delta), float(MX + delta)

def CI_DX(data, confidence):
    n = len(data)
    DX = DX_practical(data)

    alpha = 1 - confidence

    chi_upper = chi2.ppf(alpha / 2, n - 1)
    chi_lower = chi2.ppf(1 - alpha / 2, n - 1)

    return float( (n - 1) * DX / chi_upper ), float( (n - 1) * DX / chi_lower )

def solve(n):
    x, y = sp.symbols('x,y')
    
    f = x
    rev_f = sp.solve(sp.Eq(y, f), x)[0]
    
    data = generate_data(rev_f, y, n)
    
    df = sp.diff(f, x)
    
    mx_theory = MX_theory(df)
    dx_theory = DX_theory(df)
    
    mx_practical = MX_practical(data)
    dx_practical = DX_practical(data)
    
    ci_mx = CI_MX(data, 0.975)
    ci_dx = CI_DX(data, 0.975)
	  
    statistic, p_value = stats.kstest(data, lambda x: x) # Kolmogorov-Smirnov: data has func distribution

    if p_value < 0.05:
        return None, None, None, None, None, None, None
    
    return data ,mx_practical, mx_theory, dx_practical, dx_theory, ci_mx, ci_dx