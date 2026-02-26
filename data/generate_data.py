import pandas as pd
import numpy as np

np.random.seed(42)

months = pd.date_range(start='2014-01-01', end='2025-10-01', freq='MS')
n = len(months)

# Base tariff schedule (India's historical CPO tariff changes up to 2025)
# 2014-2015: 100%, 2016: 7.5%, 2017: 100%, 2018-2019: 100%,
# 2020: 10%, 2021: 17.5%, 2022-2023: 5%, 2024-2025: 27.5% (India raised duty Sep 2024)
tariff = np.array([
    *[100]*12,   # 2014
    *[100]*12,   # 2015
    *[7.5]*12,   # 2016
    *[100]*12,   # 2017
    *[100]*12,   # 2018
    *[100]*12,   # 2019
    *[10]*12,    # 2020
    *[17.5]*12,  # 2021
    *[5]*12,     # 2022
    *[5]*12,     # 2023
    *[5]*8,      # 2024 Jan–Aug (5%)
    *[27.5]*4,   # 2024 Sep–Dec (India raised to 27.5%)
    *[27.5]*10,  # 2025 Jan–Oct
])[:n]

# Global CPO price (USD/ton) — spike in 2022, stabilize, rise again in 2025
trend = np.linspace(600, 1050, n)
# Add a 2022 spike (Russia-Ukraine war effect on edible oils)
spike_2022 = np.zeros(n)
spike_2022[96:108] = np.array([200, 350, 500, 480, 420, 380, 300, 220, 150, 100, 60, 20])
# 2025 moderate rise due to El Nino supply concerns
rise_2025 = np.zeros(n)
rise_2025[132:] = np.linspace(0, 120, n - 132)
seasonal = 60 * np.sin(2 * np.pi * np.arange(n) / 12)
noise = np.random.normal(0, 40, n)
global_price = trend + spike_2022 + rise_2025 + seasonal + noise
global_price = np.clip(global_price, 400, 1800)

# Import volume (million tons/month) — inversely related to tariff
base_import = 0.8
import_volume = base_import - 0.003 * tariff + 0.0002 * (global_price - 800) + np.random.normal(0, 0.05, n)
import_volume = np.clip(import_volume, 0.1, 1.5)

# Domestic production (million tons/month)
dom_prod = 0.12 + 0.002 * np.arange(n) / 12 + np.random.normal(0, 0.01, n)
dom_prod = np.clip(dom_prod, 0.05, 0.3)

# Farmer price (INR/kg) — rises with tariff
farmer_price = 40 + 0.25 * tariff + 0.015 * global_price * 0.084 + np.random.normal(0, 2, n)
farmer_price = np.clip(farmer_price, 30, 120)

# Consumer retail price (INR/kg)
consumer_price = farmer_price * 1.35 + 5 + np.random.normal(0, 3, n)
consumer_price = np.clip(consumer_price, 50, 180)

# Import dependency ratio (%)
total_demand = import_volume + dom_prod
import_dependency = (import_volume / total_demand) * 100

# Cultivation area (million hectares)
cultivation_area = 0.35 + 0.001 * tariff + 0.0001 * np.arange(n) + np.random.normal(0, 0.005, n)

df = pd.DataFrame({
    'date': months,
    'tariff_rate': tariff,
    'global_cpo_price_usd': global_price.round(2),
    'import_volume_mt': import_volume.round(4),
    'domestic_production_mt': dom_prod.round(4),
    'farmer_price_inr': farmer_price.round(2),
    'consumer_price_inr': consumer_price.round(2),
    'import_dependency_pct': import_dependency.round(2),
    'cultivation_area_mha': cultivation_area.round(4)
})

df.to_csv('data/cpo_data.csv', index=False)
print(f"✅ Generated {n} months of CPO data → data/cpo_data.csv")
print(df.tail())