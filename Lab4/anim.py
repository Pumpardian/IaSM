import numpy as np
from matplotlib.patches import Rectangle

def generate_events(lam, mu, T_max):
    events = []
    t = 0.0
    busy_until = 0.0
    t_serv = 1.0 / mu
    
    while True:
        t += np.random.exponential(1.0 / lam)
        if t > T_max:
            break
            
        if t >= busy_until:
            events.append({
                "time": t,
                "type": "accepted",
                "start": t,
                "end": t + t_serv
            })
            busy_until = t + t_serv
        else:
            events.append({
                "time": t,
                "type": "rejected"
            })
    return events

def init_animation(ax, T_max):
    ax.clear()
    ax.set_xlim(0, T_max)
    ax.set_ylim(0, 3)
    ax.set_yticks([0.5, 1.5, 2.5])
    ax.set_yticklabels(["Rejects", "Service", "Input flow"], fontsize=11)
    ax.set_xlabel("Time", fontsize=12)
    ax.set_title("Animated queueing model with rejects (M/D/1/1)", fontsize=14, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.6)
    return []

def update_frame(ax, events, T_max, frame):
    init_animation(ax, T_max)
    current_time = frame
    
    #current time (vertical line)
    ax.axvline(x=current_time, color="blue", linestyle="--", linewidth=2, alpha=0.7)
    
    total = 0
    served = 0
    for ev in events:
        if ev["time"] > current_time:
            break
        total += 1
        
        ax.plot(ev["time"], 2.5, "ko", markersize=5) # time of request
        if ev["type"] == "accepted":
            served += 1
            rect = Rectangle((ev["start"], 1.3), ev["end"] - ev["start"], 0.4, 
                             facecolor="#4CAF50", edgecolor="black", alpha=0.8)
            ax.add_patch(rect) # service time
            ax.plot([ev["time"], ev["time"]], [2.4, 1.7], "k:", linewidth=1) # dashed line
        else:
            ax.plot(ev["time"], 0.5, "rx", markersize=10, markeredgewidth=2) # cross
            ax.plot([ev["time"], ev["time"]], [2.4, 0.6], "r:", linewidth=1) # dashed line
            
    q = served / total if total > 0 else 0.0
    a = served / current_time if current_time > 0 else 0.0
    
    ax.set_title(f"Time: {current_time:.2f} | Total requests: {total} | Served: {served}\n"
                 f"Relative throughput (Q): {q:.3f} | Absolute throughput (A): {a:.3f}", 
                 fontsize=12, fontweight="bold")
    return []