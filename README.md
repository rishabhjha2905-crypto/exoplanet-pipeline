# Exoplanet Transit Detection Pipeline
 
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rishabhjha2905-crypto/exoplanet-pipeline/blob/main/exoplanet.ipynb)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://exoplanet-transit-finder.streamlit.app/)
 
A data pipeline that automatically detects exoplanet transits from real NASA TESS telescope data. Given any star name, the pipeline fetches light curve data, runs a Box Least Squares (BLS) transit search, and produces a phase-folded transit plot — no prior knowledge of the planet's period or timing required.
 
Includes a Streamlit web app where anyone can type in a star name and get results without touching any code.
 
## Web App
 
**Live demo: [exoplanet-transit-finder.streamlit.app](https://exoplanet-transit-finder.streamlit.app/)**
 
Type in any star name, choose Fast mode (3 sectors, ~3-5 min) or Full mode (all sectors, ~10-20 min), and the app automatically fetches TESS data, runs BLS, and displays the raw light curve, periodogram, and phase-folded transit. If no significant transit is detected, it says so rather than showing a misleading plot.
 
To run locally:
```
pip install -r requirements.txt
streamlit run app.py
```
 
## Overview
 
When a planet passes in front of its star from our perspective, it blocks a small fraction of the star's light, causing a periodic dip in brightness called a transit. This pipeline detects those dips automatically by:
 
1. Querying NASA's MAST archive via the `lightkurve` library
2. Downloading and stitching multi-sector TESS light curves with proper per-sector normalization
3. Running BLS (Box Least Squares) — the same algorithm used in real exoplanet discovery — to find the best-fit orbital period
4. Checking detection significance using peak BLS power and transit depth thresholds
5. Phase-folding all available data at the detected period to produce a clean average transit profile
## Results
 
| Star | Detected Period | True Period | Transit Depth |
|------|----------------|-------------|---------------|
| WASP-17 | 3.7355 days | 3.7354 days | 1.54% |
| HAT-P-7 | 2.2047 days | 2.2047 days | 0.59% |
 
Both periods match published values to 4 decimal places. The phase-folded light curves show clean U-shaped transit profiles — the flat bottom indicates full transits from large hot Jupiter planets rather than grazing transits.
 
## Key Technical Decisions
 
**Per-sector normalization before stitching** — TESS observes in 27-day sectors with gaps in between. Normalizing each sector independently before combining prevents flux offsets between sectors from adding noise that would wash out the transit signal.
 
**BLS over Lomb-Scargle** — BLS (Box Least Squares) is specifically designed to find the periodic box-shaped dips produced by planet transits. Lomb-Scargle is optimized for sinusoidal signals and performs poorly on transit data.
 
**frequency_factor for grid control** — lightkurve internally determines period grid density from dataset length. Using `frequency_factor` overrides this to keep the grid computationally tractable without sacrificing period accuracy.
 
**Significance thresholds** — BLS always returns a best period even for stars with no planet, so detections are only shown when peak power ≥ 50 and transit depth ≥ 0.05%. Below these thresholds the result is flagged as noise rather than a planet candidate.
 
**Fast/Full mode toggle** — Fast mode downloads 3 sectors (~3-5 min), Full mode downloads all available sectors (~10-20 min). More sectors improve signal-to-noise for long-period or shallow transits but cost significantly more time.
 
## How to Run (Notebook)
 
1. Clone the repo
2. Install dependencies:
   ```
   pip install lightkurve astropy numpy matplotlib streamlit
   ```
3. Open `exoplanet.ipynb` in VS Code or Jupyter and run all cells
## Tech Stack
 
- Python
- lightkurve (NASA TESS/Kepler data access)
- astropy
- numpy, matplotlib
- Streamlit (web app)
## Project Structure
 
```
exoplanet-pipeline/
├── exoplanet.ipynb   # Main analysis notebook
├── app.py            # Streamlit web app
├── requirements.txt  # Dependencies
└── README.md
```
 
## Background
 
Transit photometry is one of the primary methods used to discover exoplanets. NASA's TESS mission has discovered thousands of exoplanets by continuously monitoring stellar brightness across the sky. This pipeline replicates the core detection workflow — from raw photon counts to a confirmed periodic transit — using the same publicly available data that professional astronomers use.