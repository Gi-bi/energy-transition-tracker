# Europe Energy Transition Tracker

An analytical project exploring how electricity generation sources
have evolved across European countries from 2000–present using
Eurostat energy balance data.

This project transforms raw infrastructure data into a longitudinal
view of Europe’s energy transition, identifying the dominant electricity
source for each country across time.

---

## Project Goal

Europe’s electricity system is undergoing a multi-decade transition
from fossil fuels toward renewable and low-carbon generation.

This project answers:

**Which energy source powered each country the most — and how has that changed over time?**

---

## Data Source

- Eurostat Energy Balances  
  *Production of electricity and derived heat by fuel* (`nrg_bal_peh`)
- Unit: Gigawatt-hours (GWh)
- Coverage: European countries, 2000–present

---

## Methodology

1. Cleaned and normalized Eurostat fuel categories
2. Grouped fuels into analytical energy systems:
   - Hydro
   - Wind
   - Coal
   - Natural Gas
   - Nuclear
   - Bioenergy
   - Geothermal
3. Calculated total electricity generation per country-year
4. Computed generation share by source
5. Identified dominant electricity source annually

---

## Europe Energy Transition Timeline

Visualization showing the dominant electricity generation source
for each European country over time.

![Energy Transition](figures/energy_transition_timeline.png)

---

## Key Observations

- Hydropower dominates Nordic and Balkan regions consistently.
- Nuclear provides long-term stability in France and Central Europe.
- Coal dependence persists longer in Eastern Europe.
- Wind and renewable growth accelerates after ~2010 across Western Europe.

---

## Tech Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Google Colab
- Git / GitHub

---

## Repository Structure


