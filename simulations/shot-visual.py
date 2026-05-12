import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from dataclasses import dataclass
import dataclasses

@dataclass
class Params:
    mass:     float  # kg
    diameter: float  # m
    C_d:      float  # dimensionless
    rho:      float  # kg/m³
    g:        float  # m/s²
    v_init:   float  # m/s
    angle:    float  # degrees
    x_init:   float  # m
    y_init:   float  # m
    dt:       float  # s
    t_end:    float  # s

# Shot calibrated so sea-level shot just reaches the basket
BASE_PARAMS = Params(
    mass=0.623, diameter=0.2388, C_d=0.47, rho=1.225,
    g=9.81, v_init=9.5, angle=52.0,
    x_init=0.0, y_init=2.2, dt=0.001, t_end=3.0,
)

ARENAS = {
    "Ball Arena – Denver":    1.014,
    "Delta Center – Utah":    1.051,
    "Paycom Center – OKC":    1.173,
    "TD Garden – Boston":     1.225,
    "MSG – New York":         1.223,
}

COLORS = {
    "Ball Arena – Denver":  "#4A90D9",
    "Delta Center – Utah":  "#00C853",
    "Paycom Center – OKC":  "#007AC1",
    "TD Garden – Boston":   "#BA0C2F",
    "MSG – New York":       "#F5A623",
}

BASKET_X    = 7.24   # m — 3-point top of arc
BASKET_Y    = 3.048  # m — 10 ft
RIM_RADIUS  = 0.2286 # m — 9 in
BALL_RADIUS = BASE_PARAMS.diameter / 2
HIT_TOL     = RIM_RADIUS - BALL_RADIUS  # ~0.11 m clearance for ball center

def drag_force(vx, vy, params):
    A  = np.pi * (params.diameter / 2) ** 2
    v  = np.sqrt(vx**2 + vy**2)
    if v == 0:
        return 0.0, 0.0
    Fd = 0.5 * params.rho * params.C_d * A * v**2
    return -Fd * vx / v, -Fd * vy / v

def simulate(params):
    angle_rad = np.radians(params.angle)
    s0 = [params.x_init, params.y_init,
          params.v_init * np.cos(angle_rad),
          params.v_init * np.sin(angle_rad)]

    def odes(t, s):
        x, y, vx, vy = s
        Fdx, Fdy = drag_force(vx, vy, params)
        return [vx, vy, Fdx / params.mass, -params.g + Fdy / params.mass]

    def hit_ground(t, s):
        return s[1]
    hit_ground.terminal  = True
    hit_ground.direction = -1

    return solve_ivp(odes, (0, params.t_end), s0,
                     t_eval=np.arange(0, params.t_end, params.dt),
                     events=hit_ground, max_step=params.dt)

def y_at_basket(sol):
    """Interpolated height at BASKET_X on the descending arc."""
    xs, ys = sol.y[0], sol.y[1]
    # Only look at the descending half
    peak_i = np.argmax(ys)
    xs_down, ys_down = xs[peak_i:], ys[peak_i:]
    if xs_down[-1] < BASKET_X:
        return None
    idx = np.searchsorted(xs_down, BASKET_X)
    if idx == 0 or idx >= len(xs_down):
        return None
    x0, x1 = xs_down[idx-1], xs_down[idx]
    y0, y1 = ys_down[idx-1], ys_down[idx]
    return y0 + (y1 - y0) * (BASKET_X - x0) / (x1 - x0)


fig = plt.figure(figsize=(14, 7))
fig.patch.set_facecolor("#0d0d0d")

# Main axis
ax = fig.add_axes([0.05, 0.10, 0.60, 0.80])
ax.set_facecolor("#111111")

# Inset — zoomed basket area
ax_inset = fig.add_axes([0.68, 0.30, 0.28, 0.50])
ax_inset.set_facecolor("#1a1a1a")

results = {}
for name, rho in ARENAS.items():
    p   = dataclasses.replace(BASE_PARAMS, rho=rho)
    sol = simulate(p)
    y_b = y_at_basket(sol)
    made = (y_b is not None) and (abs(y_b - BASKET_Y) < HIT_TOL)
    results[name] = (sol, y_b, made)

for name, (sol, y_b, made) in results.items():
    color  = COLORS[name]
    result = "MAKE" if made else "MISS"
    label  = f"{name}  (ρ={ARENAS[name]:.3f})  [{result}]"
    ax.plot(sol.y[0], sol.y[1], color=color, linewidth=2.0, label=label, zorder=3)
    ax_inset.plot(sol.y[0], sol.y[1], color=color, linewidth=2.0, zorder=3)
    if y_b is not None:
        marker = "o" if made else "x"
        ms     = 9 if made else 10
        ax.plot(BASKET_X, y_b, marker=marker, color=color, markersize=ms, zorder=5, markeredgewidth=2)
        ax_inset.plot(BASKET_X, y_b, marker=marker, color=color, markersize=ms, zorder=5, markeredgewidth=2)
        # Annotate inset with height delta vs Boston
        if name != "TD Garden – Boston":
            boston_y = results["TD Garden – Boston"][1]
            if boston_y is not None:
                delta_cm = (y_b - boston_y) * 100
                sign     = "+" if delta_cm > 0 else ""
                ax_inset.annotate(f"{sign}{delta_cm:.1f} cm", xy=(BASKET_X, y_b),
                                  xytext=(BASKET_X + 0.06, y_b),
                                  color=color, fontsize=8, va="center")

# No-drag baseline
p_nodrag  = dataclasses.replace(BASE_PARAMS, rho=0.0, C_d=0.0)
sol_nodrag = simulate(p_nodrag)
ax.plot(sol_nodrag.y[0], sol_nodrag.y[1], color="white", linewidth=1.2,
        linestyle="--", alpha=0.35, label="No drag (baseline)", zorder=2)

# Basket geometry — main
rim_main = plt.Circle((BASKET_X, BASKET_Y), RIM_RADIUS, color="#FF6B00",
                       fill=False, linewidth=2.5, zorder=6)
ax.add_patch(rim_main)
ax.plot([BASKET_X + RIM_RADIUS + 0.03, BASKET_X + RIM_RADIUS + 0.03],
        [BASKET_Y - 0.35, BASKET_Y + 0.35], color="white", linewidth=3, zorder=6)
ax.axvline(BASKET_X, color="#FF6B00", linewidth=0.8, linestyle=":", alpha=0.5, zorder=2)

# Basket geometry — inset
rim_inset = plt.Circle((BASKET_X, BASKET_Y), RIM_RADIUS, color="#FF6B00",
                        fill=False, linewidth=2.5, zorder=6)
ax_inset.add_patch(rim_inset)
ax_inset.plot([BASKET_X + RIM_RADIUS + 0.03, BASKET_X + RIM_RADIUS + 0.03],
              [BASKET_Y - 0.35, BASKET_Y + 0.35], color="white", linewidth=3, zorder=6)
ax_inset.axvline(BASKET_X, color="#FF6B00", linewidth=0.8, linestyle=":", alpha=0.5)
ax_inset.axhline(BASKET_Y, color="#FF6B00", linewidth=0.6, linestyle=":", alpha=0.4)

# Release point
ax.plot(BASE_PARAMS.x_init, BASE_PARAMS.y_init, "w^", markersize=9, zorder=5)
ax.annotate("Release", xy=(0.1, 2.2), color="white", fontsize=8, alpha=0.7)

# Court floor
ax.axhline(0, color="#7B5A00", linewidth=2.5, zorder=1)

# Main axis styling
ax.set_xlabel("Horizontal Distance (m)", color="white", fontsize=12)
ax.set_ylabel("Height (m)", color="white", fontsize=12)
ax.set_title(
    f"Same 3-Point Shot Across 5 NBA Arenas — Altitude vs. Trajectory\n"
    f"v₀ = {BASE_PARAMS.v_init} m/s  |  θ = {BASE_PARAMS.angle}°  |  "
    f"Release height = {BASE_PARAMS.y_init} m  |  Basket at {BASKET_X} m",
    color="white", fontsize=12, pad=10,
)
ax.tick_params(colors="white")
for sp in ax.spines.values():
    sp.set_edgecolor("#333333")
ax.legend(loc="upper right", fontsize=8.5, facecolor="#1a1a1a",
          labelcolor="white", edgecolor="#444444")
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
ax.grid(True, alpha=0.12, color="white")

# Inset styling
ax_inset.set_xlim(BASKET_X - 0.6, BASKET_X + 0.7)
ax_inset.set_ylim(BASKET_Y - 0.6, BASKET_Y + 0.6)
ax_inset.set_title("Basket View", color="white", fontsize=9)
ax_inset.tick_params(colors="white", labelsize=7)
for sp in ax_inset.spines.values():
    sp.set_edgecolor("#555555")
ax_inset.grid(True, alpha=0.15, color="white")

# Connection lines from main to inset
for spine_x, spine_y in [(BASKET_X - 0.6, BASKET_Y - 0.6),
                          (BASKET_X + 0.7, BASKET_Y - 0.6)]:
    fig.add_artist(plt.Line2D([0, 0], [0, 0], color="#555555", linewidth=0.5))

plt.savefig("shot_comparison.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.show()
