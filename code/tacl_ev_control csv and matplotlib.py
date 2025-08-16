import traci
import matplotlib.pyplot as plt

# SUMO GUI launch command
sumoBinary = "sumo-gui"
sumoCmd = [
    sumoBinary,
    "-n", "sumo.net.xml",
    "-r", "sumo.rou.xml",
    "-a", "chargingstations.add.xml",
    "--delay", "120",
    "--start"
]

EV_ID = "ev1"
BATTERY_THRESHOLD = 49
CHARGING_STATION_EDGES = ["2i", "3o"]

battery_levels = []
times = []

def main():
    traci.start(sumoCmd)
    print("[INFO] SUMO started")

    while EV_ID not in traci.vehicle.getIDList():
        traci.simulationStep()

    # Get original route and destination
    original_route = traci.vehicle.getRoute(EV_ID)
    original_destination = original_route[-1]

    rerouted = False
    charging = False
    charging_started = False
    assigned_charger = None

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        time = traci.simulation.getTime()

        if EV_ID not in traci.vehicle.getIDList():
            break

        battery = float(traci.vehicle.getParameter(EV_ID, "device.battery.actualBatteryCapacity"))
        max_battery = float(traci.vehicle.getParameter(EV_ID, "device.battery.maximumBatteryCapacity"))
        battery_percent = 100 * battery / max_battery

        print(f"[{time:.1f}s] Battery: {battery_percent:.2f}%")
        battery_levels.append(battery_percent)
        times.append(time)

        # Battery low: find nearest charging station and reroute
        if not rerouted and battery_percent < BATTERY_THRESHOLD:
            current_edge = traci.vehicle.getRoadID(EV_ID)
            assigned_charger = find_nearest_charger(current_edge)
            if assigned_charger:
                route = traci.simulation.findRoute(current_edge, assigned_charger).edges
                if len(route) > 1:
                    traci.vehicle.setRoute(EV_ID, route)
                    rerouted = True
                    print(f"[INFO] Battery low. Rerouting to charger at {assigned_charger}")
                else:
                    print(f"[ERROR] No valid route to {assigned_charger}")
            else:
                print("[WARN] No charger available!")

        # Arrived at charger
        if rerouted and traci.vehicle.getRoadID(EV_ID) == assigned_charger and not charging:
            charging = True
            charging_started = False
            print(f"[INFO] Arrived at charging station {assigned_charger}")

        # Begin charging
        if charging and not charging_started and not traci.vehicle.isStopped(EV_ID):
            lane = traci.vehicle.getLaneID(EV_ID)
            pos = traci.vehicle.getLanePosition(EV_ID)
            lane_len = traci.lane.getLength(lane)
            stop_pos = min(pos + 2.0, lane_len - 1.0)

            if lane_len - pos < 3.0:
                print(f"[WARN] Too close to end of lane {lane} to stop safely.")
            else:
                traci.vehicle.setStop(EV_ID, edgeID=assigned_charger, pos=stop_pos, duration=9999)
                charging_started = True
                print(f"[INFO] EV stopped to charge at {assigned_charger}")

        # Resume after fully charged
        if charging and battery_percent >= 99.9:
            current_edge = traci.vehicle.getRoadID(EV_ID)
            try:
                new_route = traci.simulation.findRoute(current_edge, original_destination).edges
                traci.vehicle.setRoute(EV_ID, new_route)
                traci.vehicle.resume(EV_ID)
                print(f"[INFO] Fully charged. Resuming to destination via: {new_route}")
            except:
                print(f"[ERROR] Cannot resume: no route from {current_edge} to {original_destination}")
            rerouted = False
            charging = False
            charging_started = False
            assigned_charger = None

    traci.close()
    print("[INFO] Simulation complete.")
    plot_battery(times, battery_levels)

# Find the closest charger based on route length
def find_nearest_charger(current_edge):
    best_charger = None
    best_length = float("inf")
    for charger_edge in CHARGING_STATION_EDGES:
        try:
            route = traci.simulation.findRoute(current_edge, charger_edge)
            if route.length < best_length:
                best_length = route.length
                best_charger = charger_edge
        except:
            continue
    return best_charger

# Plot battery over time
def plot_battery(times, battery_levels):
    plt.plot(times, battery_levels, label="Battery %")
    plt.xlabel("Simulation Time (s)")
    plt.ylabel("Battery Level (%)")
    plt.title("EV Battery Over Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
