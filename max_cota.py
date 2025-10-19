import fastf1
import numpy as np
import matplotlib.pyplot as plt

fastf1.Cache.enable_cache('f1_cache')

# Max Verstappen
DRIVER = 'VER'

# Austin GP round mapping by year
austin_rounds = {2021: 17, 2022: 19, 2023: 18, 2024: 19}

# Store data
lap_times = []
sector_times = []
speed_traces = []
corner_deltas = []
SEASONS = []

NUM_CORNERS = 20

for season, round_number in austin_rounds.items():
    try:
        session = fastf1.get_session(season, round_number, 'Q')
        session.load()
    except Exception as e:
        print(f"Failed to load {season} Austin GP: {e}")
        continue
    
    # Fastest lap
    lap = session.laps.pick_driver(DRIVER).pick_fastest()
    if lap is None:
        continue
    
    SEASONS.append(season)
    lap_times.append(lap['LapTime'].total_seconds())
    
    # Sector times
    sectors = [lap['Sector1Time'].total_seconds(),
               lap['Sector2Time'].total_seconds(),
               lap['Sector3Time'].total_seconds()]
    sector_times.append(sectors)
    
    # Telemetry
    tel = lap.get_car_data().add_distance()
    distance_common = np.linspace(0, tel['Distance'].max(), 3000)
    speed = np.interp(distance_common, tel['Distance'], tel['Speed'])
    speed_traces.append((distance_common, speed))
    
    # Corner-by-corner delta (vs average speed)
    avg_speed = np.mean(speed)
    corner_points = np.linspace(0, distance_common.max(), NUM_CORNERS)
    corner_delta = np.interp(corner_points, distance_common, speed - avg_speed)
    corner_deltas.append(corner_delta)

# -----------------------------
# Plotting
# -----------------------------
fig, axs = plt.subplots(3, 2, figsize=(14, 12))
fig.suptitle("Max Verstappen - Austin GP Qualifying (2021-2024)", fontsize=16)

# Lap Times
axs[0,0].bar(SEASONS, lap_times, color='red', alpha=0.7)
axs[0,0].set_title("Fastest Qualifying Lap Time")
axs[0,0].set_ylabel("Lap Time (s)")
axs[0,0].text(0.5, -0.25, "Max's absolute speed each year", 
              ha='center', transform=axs[0,0].transAxes, fontsize=8)

# Sector Times
sector_array = np.array(sector_times)
for i, sector in enumerate(['Sector 1', 'Sector 2', 'Sector 3']):
    axs[0,1].plot(SEASONS, sector_array[:,i], marker='o', label=sector)
axs[0,1].set_title("Sector Times")
axs[0,1].set_ylabel("Time (s)")
axs[0,1].legend(fontsize=8)
axs[0,1].text(0.5, -0.25, "Strengths & weaknesses in each sector", 
              ha='center', transform=axs[0,1].transAxes, fontsize=8)

# Speed Traces
for i, (dist, speed) in enumerate(speed_traces):
    axs[1,0].plot(dist, speed, label=f"{SEASONS[i]}")
axs[1,0].set_title("Speed Trace")
axs[1,0].set_ylabel("Speed (km/h)")
axs[1,0].legend(fontsize=8)
axs[1,0].text(0.5, -0.25, "Speed profile around the lap each year", 
              ha='center', transform=axs[1,0].transAxes, fontsize=8)

# Corner Delta
for i, delta in enumerate(corner_deltas):
    axs[1,1].bar(np.arange(1, NUM_CORNERS+1) + i*0.2, delta, width=0.2, label=f"{SEASONS[i]}")
axs[1,1].set_title("Corner-by-Corner Delta vs Average")
axs[1,1].set_xlabel("Corner #")
axs[1,1].set_ylabel("Delta (km/h)")
axs[1,1].legend(fontsize=8)
axs[1,1].text(0.5, -0.25, "Positive = faster than average", 
              ha='center', transform=axs[1,1].transAxes, fontsize=8)

# Lap Time Trend
axs[2,0].plot(SEASONS, lap_times, marker='o', color='red')
axs[2,0].set_title("Lap Time Trend")
axs[2,0].set_xlabel("Year")
axs[2,0].set_ylabel("Lap Time (s)")
axs[2,0].text(0.5, -0.25, "Improvement or consistency over 4 years", 
              ha='center', transform=axs[2,0].transAxes, fontsize=8)

# Optional
axs[2,1].axis('off')

plt.tight_layout(rect=[0,0,1,0.96])
plt.show()
