import fastf1
import fastf1.plotting
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import google.generativeai as genai  # FIXED IMPORT NAME
import seaborn as sns

# --- DEFINE COLORS MANUALLY (Fix for fastf1 version update) ---
COMPOUND_COLORS = {
    'SOFT': '#da291c',    # Red
    'MEDIUM': '#ffd12e',  # Yellow
    'HARD': '#f0f0f0',    # White
    'INTERMEDIATE': '#43d26b', # Green
    'WET': '#2e6da4'      # Blue
}



# 1. Cache Setup
if not os.path.exists('cache'):
    os.makedirs('cache')

fastf1.Cache.enable_cache('cache')
fastf1.plotting.setup_mpl(misc_mpl_mods=False) # Better F1 styling

# 2. Main Menu
def main():
    print("\n======================================")
    print("   F1 TELEMETRY & AI ANALYSIS TOOL    ")
    print("======================================")

    while True:
        print("\nEnter the analysis you want to perform:")
        print("1. Compare Drivers (Telemetry)")
        print("2. Analyze Lap Times (Violin Plot)")
        print("3. Analyze Tyre Strategy (Stint Map)")
        print("4. Map of the Track (Neon)")
        print("5. Ask the AI Engineer")
        print("6. Exit")

        choice = input("Choice: ").strip()
        
        if choice == '1':
            CompareDrivers()
        elif choice == '2':
            LapTimeAnalysis()
        elif choice == '3':
            TyreStrategyAnalysis()
        elif choice == '4':
            MapOfTheTrack()
        elif choice == '5':
            prompt = input("What is your question for the Race Engineer? ")
            print(ask_ai_engineer(prompt))
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

# --- OPTION 1: TELEMETRY ---
def CompareDrivers():
    print("Enter Grand Prix (e.g., 'Monaco'):")
    gp_name = input().strip()
    print("Enter Year (e.g., 2024):")
    year = int(input().strip())
    print("Enter Session (Q or R):")
    session_type = input().strip().upper()

    try:
        race = fastf1.get_session(year, gp_name, session_type)
        print(f"Loading {gp_name} {year}...")
        race.load()
    except Exception as e:
        print(f"Error loading session: {e}")
        return

    print("Enter first driver code (e.g. VER):")
    d1_code = input().strip().upper()
    print("Enter second driver code (e.g. NOR):")
    d2_code = input().strip().upper()

    try:
        d1_lap = race.laps.pick_driver(d1_code).pick_fastest()
        d2_lap = race.laps.pick_driver(d2_code).pick_fastest()
        
        d1_tel = d1_lap.get_car_data().add_distance()
        d2_tel = d2_lap.get_car_data().add_distance()
    except:
        print("Error: Driver not found or no data available.")
        return

    # Plotting
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Driver 1
    ax.plot(d1_tel['Distance'], d1_tel['Speed'], 
            color=fastf1.plotting.driver_color(d1_code), 
            label=d1_code)
    
    # Driver 2
    ax.plot(d2_tel['Distance'], d2_tel['Speed'], 
            color=fastf1.plotting.driver_color(d2_code), 
            label=d2_code)

    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Speed (km/h)')
    ax.set_title(f"{d1_code} vs {d2_code} - {gp_name} {year}")
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.show()

# --- OPTION 2: LAP TIMES ---
def LapTimeAnalysis():
    print("Enter Grand Prix (e.g., 'Monaco'):")
    gp = input().strip()
    print("Enter Year (e.g., 2024):")
    year = int(input().strip())
    
    try:
        race = fastf1.get_session(year, gp, 'R')
        print("Loading data...")
        race.load()
        
        # Filter out slow laps (Safety Car / In-laps) to make graph readable
        laps = race.laps.pick_quicklaps()
        
        plt.style.use('dark_background')
        plt.figure(figsize=(12, 6))
        
        # Create Box Plot using MANUAL dictionary
        sns.boxplot(data=laps, x="Driver", y="LapTime", hue="Compound", palette=COMPOUND_COLORS)
        
        plt.title(f"Lap Time Distribution - {gp} {year}")
        plt.grid(alpha=0.2)
        plt.show()
    except Exception as e:
        print(f"Error: {e}")

# --- OPTION 3: TYRE STRATEGY ---
def TyreStrategyAnalysis():
    print("Enter Grand Prix (e.g., 'Bahrain'):")
    gp = input().strip()
    print("Enter Year (e.g., 2024):")
    year = int(input().strip())
    
    try:
        session = fastf1.get_session(year, gp, 'R')
        print("Loading data...")
        session.load()
        laps = session.laps
        drivers = session.drivers
        
        fig, ax = plt.subplots(figsize=(12, 8))
        plt.style.use('dark_background')
        
        print("Generating Stint Map...")
        
        for driver in drivers:
            driver_laps = laps.pick_driver(driver)
            stints = driver_laps.groupby('Stint')
            
            for stint_number, stint_data in stints:
                compound = stint_data.iloc[0]['Compound']
                
                # Use Manual Dictionary
                color = COMPOUND_COLORS.get(compound, 'white')
                
                start_lap = stint_data['LapNumber'].min()
                end_lap = stint_data['LapNumber'].max()
                
                if stint_number == 1: start_lap = 0
                
                ax.barh(y=driver, width=end_lap - start_lap, left=start_lap, 
                        color=color, edgecolor='black')
                        
        ax.set_xlabel("Lap Number")
        ax.set_title(f"Tyre Strategy - {gp} {year}")
        ax.invert_yaxis()
        plt.show()
    except Exception as e:
        print(f"Error loading tyre data: {e}")

# --- OPTION 4: MAP ---
def MapOfTheTrack():
    print("Enter Circuit (e.g., 'Silverstone'):")
    circuit_name = input().strip()
    print("Enter Year:")
    year = int(input().strip())

    try:
        race = fastf1.get_session(year, circuit_name, 'R')
        print("Loading map data...")
        race.load()
        
        # Safer: Pick fastest lap of the session (doesn't rely on one driver)
        lap = race.laps.pick_fastest()
        tel = lap.get_telemetry()

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')

        # Neon Glow Effect
        ax.plot(tel['X'], tel['Y'], color='cyan', linewidth=10, alpha=0.1)
        ax.plot(tel['X'], tel['Y'], color='cyan', linewidth=5, alpha=0.3)
        ax.plot(tel['X'], tel['Y'], color='white', linewidth=1) # Center line

        ax.set_aspect('equal')
        ax.axis('off') # Remove box for cleaner look
        plt.title(f"{circuit_name} {year}", color='white')
        plt.show()
    except Exception as e:
        print(f"Error loading map: {e}")

# --- OPTION 5: AI ENGINEER ---
def ask_ai_engineer(prompt):
    # USE YOUR ACTUAL KEY HERE
    api_key = "AIzaSyBOM1E7WXn37v-MmfGODjsfTVfqgdWd_14" 
    
    if api_key == "YOUR_API_KEY_HERE":
        return "Error: Please edit the code and paste your Google API Key."

    try:
        genai.configure(api_key=api_key)
        print("Radio Check... (Contacting AI Engineer)...")
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(prompt)
        return f"\n--- AI Engineer Report ---\n{response.text}\n"
        
    except Exception as e:
        return f"Radio Failure (Error): {e}"

# Run the program
if __name__ == "__main__":
    main()