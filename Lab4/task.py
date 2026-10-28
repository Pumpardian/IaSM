import numpy as np

# A/S/C/D
# M/D/1/1

# lam - requests / time unit
# mu - service / time unit

def analytical_solution(lam, mu):
    q_theor = mu / (lam + mu) # request service probability
    a_theor = lam * q_theor # average serviced requests / time unit
    return q_theor, a_theor

def simulate_qs(lam, mu, num_requests=1000000):
    t_serv = 1.0 / mu
    served_requests = 0
    busy_until = 0.0
    
    inter_arrival_times = np.random.exponential(1.0 / lam, num_requests)
    arrival_times = np.cumsum(inter_arrival_times)
    
    total_time = arrival_times[-1]
    
    for t in arrival_times:
        if t >= busy_until:
            served_requests += 1
            busy_until = t + t_serv
    q_sim = served_requests / num_requests
    a_sim = served_requests / total_time
    
    return q_sim, a_sim, served_requests, num_requests

def solve(lambda_ = 2.0, mu = 3.0):
    q_theor, a_theor = analytical_solution(lambda_, mu)
    q_sim, a_sim, served, total = simulate_qs(lambda_, mu)
    error_q = abs(q_theor - q_sim) / q_theor * 100
    error_a = abs(a_theor - a_sim) / a_theor * 100
    return q_theor, a_theor, q_sim, a_sim, served, total, error_q, error_a

if __name__ == "__main__":
    solve()