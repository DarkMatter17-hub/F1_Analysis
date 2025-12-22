import fastf1
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os



# 1. Cache Setup
if not os.path.exists('cache'):
    os.makedirs('cache')

fastf1.Cache.enable_cache('cache')

# 2. User Inputs
def main():
    print("Welcome to the F1 Telemetry Analysis Tool!")

    while True: # <--- This keeps the program running
        print("\n--------------------------------------")
        print("Enter the analysis you want to perform:")
        print("1. Compare Drivers")
        print("2. Analyze Lap Times")
        print("3. Analyze Tyre Strategy")
        print("4. Map of the track")
        print("5. Exit") # <--- Added an exit option

        analysis_choice = input("Choice: ").strip()
        
        match analysis_choice:
            case '1':
                CompareDrivers()
            case '2':
                print("Lap Time Analysis is under development.")
            case '3':
                print("Tyre Strategy Analysis is under development.")
            case '4':
                MapOfTheTrack()
            case '5':
                print("Exiting...")
                break # <--- This breaks the loop and stops the program
            case _:
                print("Invalid choice. Please select a valid option.")




def CompareDrivers():
    # 2. User Inputs for Grand Prix and Year
    print("Enter the Grand Prix you want to analyze (e.g., 'Monaco', 'Silverstone'):")
    gp_name = input().strip()
    print("Enter the Year of the Grand Prix (e.g., 2023):")
    year = int(input().strip()) 
    print("Enter the Session Type (e.g., 'Q' for Qualifying, 'R' for Race):")
    session_type = input().strip().upper()

    # 3. Load Session
    # Get the session object
    race = fastf1.get_session(year, gp_name, session_type)

    print(f"Contacting the track... downloading data for {gp_name} {year}...")
    race.load() 
    print("Data downloaded successfully")

    # 4. Driver Selection
    print("\nEnter the driver codes you want to compare.")
    print("(e.g., 'VER', 'NOR', 'HAM', 'LEC')")

    driver1 = input("Enter the first driver code: ").strip().upper()
    driver2 = input("Enter the second driver code: ").strip().upper()

    # Get fastest laps
    try:
        d1_lap = race.laps.pick_driver(driver1).pick_fastest()
        d2_lap = race.laps.pick_driver(driver2).pick_fastest()
    except Exception as e:
        print(f"Error: Could not find data for one of the drivers. Check the codes. {e}")
        exit()

    print(f"\n{driver1}'s Fastest Lap: {d1_lap['LapTime']}")
    print(f"{driver2}'s Fastest Lap: {d2_lap['LapTime']}")

    # 5. Get Telemetry
    print("Extracting telemetry data...")
    d1_tel = d1_lap.get_car_data().add_distance()
    d2_tel = d2_lap.get_car_data().add_distance()

    # Preview data
    print("\n--- Telemetry Preview (First 5 rows) ---")
    print(d1_tel.head())

    # 6. Mode Selection (Styling)
    mode = input("\nSelect Mode (type 'light' or 'dark'): ").lower().strip()

    if mode == 'light':
        bg_color = 'white'
        text_color = 'black'
        grid_color = 'lightgray'
    else:
        # Default to Dark mode
        bg_color = '#1e1e1e' 
        text_color = 'white'
        grid_color = '#333333'

    # 7. Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Styling axes
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.title.set_color(text_color)
    ax.tick_params(axis='x', colors=text_color) 
    ax.tick_params(axis='y', colors=text_color)
    for spine in ax.spines.values():
        spine.set_edgecolor(text_color)

    # --- DYNAMIC PLOTTING FIXES START HERE ---

    # Use the 'driver1' variable for the label, not the string 'Verstappen'
    ax.plot(d1_tel['Distance'], d1_tel['Speed'], color='cyan', label=driver1)

    # Use the 'driver2' variable for the label, not the string 'Norris'
    ax.plot(d2_tel['Distance'], d2_tel['Speed'], color='magenta', label=driver2)

    ax.set_xlabel('Distance in Meters')
    ax.set_ylabel('Speed in km/h')

    # Use an f-string with the variables gp_name, year, driver1, and driver2
    ax.set_title(f"Telemetry Comparison: {driver1} vs {driver2} - {gp_name} {year}")

    ax.legend() 
    ax.grid(color=grid_color, linestyle='--') # Added a grid for better readability

    # --- DYNAMIC PLOTTING FIXES END HERE ---

    plt.show()


def TyreStrategyAnalysis():
    print("Tyre Strategy Analysis is under development.")

def LapTimeAnalysis():
    print("Lap Time Analysis is under development.")


def MapOfTheTrack():
    print("Enter the circuit name you want to map (e.g., 'Monaco', 'Silverstone'):")
    circuit_name = input().strip()
    print("Enter the year of the circuit (e.g., 2023):")
    year = int(input().strip())

    # Load data
    race = fastf1.get_session(year, circuit_name, 'R')
    race.load()
    
    driver = 'VER'
    circuit = race.laps.pick_driver(driver).pick_fastest()
    tel = circuit.get_telemetry()

    # 1. SETUP DARK THEME
    # 'dark_background' style sets white text and black bg automatically
    plt.style.use('dark_background') 
    
    fig, ax = plt.subplots(figsize=(20, 20))
    
    # Ensure the background is pitch black
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')

    # Define your neon color (e.g., Cyan: '#00FFFF', Neon Red: '#FF0033')
    neon_color = '#00FFFF' 

    # 2. CREATE THE GLOW EFFECT
    # Plot the line multiple times with increasing width and low opacity
    for i in range(5):
        ax.plot(tel['X'], tel['Y'], color=neon_color, linewidth=(i * 1.5) + 2,  alpha=0.1, zorder=1)                 # Render at bottom

    # 3. PLOT THE MAIN SHARP LINE
    ax.plot(tel['X'], tel['Y'], 
            color=neon_color, linewidth=2, alpha=1.0, zorder=2) # Render on top of the glow

    # 4. STYLE THE AXES (Spines and Ticks)
    ax.set_xlabel("X Coordinate (m)", color=neon_color)
    ax.set_ylabel("Y Coordinate (m)", color=neon_color)
    ax.set_title(f"Neon Map: {circuit_name} ({year})", color=neon_color)
    
    # Color the numbers (ticks) and the box (spines) to match
    ax.tick_params(colors=neon_color, which='both')
    for spine in ax.spines.values():
        spine.set_edgecolor("#FA466A")

    ax.set_aspect('equal')
    plt.show()

# Run the function
# MapOfTheTrack()


main()
