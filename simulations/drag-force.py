import numpy as np
from dataclasses import dataclass

@dataclass
class Params:
    mass:     float  # kg
    diameter: float  # m
    C_d:      float  # dimensionless
    rho:      float  # kg/m³
    g:        float  # m/s²
    v_init:   float  # m/s launch speed
    angle:    float  # degrees
    x_init:   float  # m
    y_init:   float  # m
    dt:       float  # s
    t_end:    float  # s

ARENAS = {
    "Ball Arena (Denver Nuggets)":               1.014,
    "Delta Center (Utah Jazz)":                  1.051,
    "Paycom Center (OKC Thunder)":               1.173,
    "Footprint Center (Phoenix Suns)":           1.178,
    "State Farm Arena (Atlanta Hawks)":          1.181,
    "Little Caesars Arena (Detroit Pistons)":    1.183,
    "Target Center (Minnesota Timberwolves)":    1.188,
    "Spectrum Center (Charlotte Hornets)":       1.194,
    "Gainbridge Fieldhouse (Indiana Pacers)":    1.194,
    "Rocket Mortgage FieldHouse (Cleveland)":    1.196,
    "Frost Bank Center (San Antonio Spurs)":     1.197,
    "United Center (Chicago Bulls)":             1.199,
    "Fiserv Forum (Milwaukee Bucks)":            1.199,
    "American Airlines Center (Dallas Mavs)":    1.206,
    "Scotiabank Arena (Toronto Raptors)":        1.214,
    "FedExForum (Memphis Grizzlies)":            1.214,
    "Crypto.com Arena (Lakers/Clippers)":        1.215,
    "Kia Center (Orlando Magic)":                1.220,
    "Moda Center (Portland Trail Blazers)":      1.221,
    "Chase Center (Golden State Warriors)":      1.223,
    "Barclays Center (Brooklyn Nets)":           1.223,
    "Capital One Arena (Washington Wizards)":    1.223,
    "Toyota Center (Houston Rockets)":           1.223,
    "Madison Square Garden (NY Knicks)":         1.223,
    "Golden 1 Center (Sacramento Kings)":        1.224,
    "Wells Fargo Center (Philadelphia 76ers)":   1.224,
    "TD Garden (Boston Celtics)":                1.225,
    "Kaseya Center (Miami Heat)":                1.225,
    "Smoothie King Center (NO Pelicans)":        1.225,
}

BASE_PARAMS = Params(
    mass     = 0.623,
    diameter = 0.2388,
    C_d      = 0.47,
    rho      = 1.225,   # overridden per arena
    g        = 9.81,
    v_init   = 7.5,
    angle    = 45,
    x_init   = 0.0,
    y_init   = 2.0,
    dt       = 0.001,
    t_end    = 3.0,
)

def cross_section(diameter):
    return np.pi * (diameter / 2) ** 2

def drag_force(vx, vy, params):
    A = cross_section(params.diameter)
    v = np.sqrt(vx**2 + vy**2)
    if v == 0:
        return 0.0, 0.0
    Fd = 0.5 * params.rho * params.C_d * A * v**2
    return -Fd * vx / v, -Fd * vy / v

if __name__ == "__main__":
    # Use launch velocity components at 45 degrees for comparison
    angle_rad = np.radians(BASE_PARAMS.angle)
    vx = BASE_PARAMS.v_init * np.cos(angle_rad)
    vy = BASE_PARAMS.v_init * np.sin(angle_rad)

    print(f"Shot: v={BASE_PARAMS.v_init} m/s at {BASE_PARAMS.angle}°  "
          f"(vx={vx:.3f}, vy={vy:.3f} m/s)\n")
    print(f"{'Arena':<45} {'ρ (kg/m³)':>10} {'Fdx (N)':>10} {'Fdy (N)':>10} {'|Fd| (N)':>10}")
    print("-" * 90)

    for arena, rho in ARENAS.items():
        import dataclasses
        p = dataclasses.replace(BASE_PARAMS, rho=rho)
        Fdx, Fdy = drag_force(vx, vy, p)
        Fd_mag = np.sqrt(Fdx**2 + Fdy**2)
        print(f"{arena:<45} {rho:>10.3f} {Fdx:>10.4f} {Fdy:>10.4f} {Fd_mag:>10.4f}")
