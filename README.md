# Surface Wind Visualization
A Python script to visualize and animate global surface wind patterns using GFS weather model data.

## Data Source
This project relies on the NOAA/NCEP GFS weather model data, which is publicly available and provided by the National Oceanic and Atmospheric Administration (NOAA).

## Features
- Fetches and processes wind speed and direction data from NOAA's GFS.
- Visualizes surface wind patterns with a map overlay.
- Generates an animated GIF of wind patterns over time.

## Requirements
- Python 3.8+
- Required libraries (install via `requirements.txt`):
  - xarray
  - numpy
  - matplotlib
  - mpl_toolkits.basemap
  - imageio

## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Surface-Wind-Visualization.git
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Run the script:
   ```bash
   python main.py
4. The output GIF will be saved in the specified directory.

## Sample File
![](https://github.com/tanmaymelanta/Surface-Wind-Visualization/blob/main/surface_wind_speed.gif)
