# Exoplanet Transit Detection Pipeline
 
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rishabhjha2905-crypto/exoplanet-pipeline/blob/main/exoplanet.ipynb)
 
A data pipeline that automatically detects exoplanet transits from real NASA TESS telescope data. Given any star name, the pipeline fetches light curve data, runs a Box Least Squares (BLS) transit search, and produces a phase-folded transit plot — no prior knowledge of the planet's period or timing required.
 
## Overview
 
When a planet passes in front of its star from our perspective, it blocks a small fraction of the star's light, causing a periodic dip in brightness called a transit. This pipeline detects those dips automatically by:
 
1. Querying NASA's MAST archive via the `lightkurve` library
2. Downloading and stitching multi-sector TESS light curves with proper per-sector normalization
3. Running BLS (Box Least Squares) — the same algorithm used in real exoplanet discovery — to find the best-fit orbital period
4. Phase-folding all available data at the detected period to produce a clean average transit profile
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
 
## Usage
 
```python
detect_transit("WASP-17")   # hot Jupiter, 3.74 day period
detect_transit("HAT-P-7")   # hot Jupiter, 2.20 day period
detect_transit("any_star")  # works on any star with TESS data
```
 
## How to Run
 
1. Clone the repo
2. Install dependencies:
   ```
   pip install lightkurve astropy numpy matplotlib
   ```
3. Open `exoplanet.ipynb` in VS Code or Jupyter and run all cells
## Tech Stack
 
- Python
- lightkurve (NASA TESS/Kepler data access)
- astropy
- numpy, matplotlib
## Project Structure
 
```
exoplanet-pipeline/
├── exoplanet.ipynb   # Main notebook with full pipeline
└── README.md
```
 
## Background
 
Transit photometry is one of the primary methods used to discover exoplanets. NASA's TESS mission has discovered thousands of exoplanets by continuously monitoring stellar brightness across the sky. This pipeline replicates the core detection workflow — from raw photon counts to a confirmed periodic transit — using the same publicly available data that professional astronomers use.