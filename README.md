# Collision Detection Simulation

## How to Run

1. Clone the repository and go to the app folder:
   git clone https://github.com/DavinTanaya/RealAnalysis.git
   cd RealAnalysis/app

2. Create virtual environment:
   python -m venv venv

3. Activate virtual environment:
   - Windows (PowerShell): .\venv\Scripts\Activate.ps1
   - Windows (CMD): .\venv\Scripts\activate.bat
   - macOS / Linux: source venv/bin/activate

4. Install dependencies:
   pip install pygame

5. Run the program:
   python simulation.py

## Game Controls

- P: Toggle Playable / Experiment Mode
- M: Toggle Naive (Discrete) vs Continuous (Uniform Continuity)
- F: Toggle Auto-Fire
- Space: Fire bullet (Experiment Mode)
- Mouse click: Aim and shoot (Playable Mode)
- WASD / Arrow keys: Move player
- Up / Down: Adjust bullet velocity
- Left / Right: Adjust delta t (time step)
- R: Reset stats
