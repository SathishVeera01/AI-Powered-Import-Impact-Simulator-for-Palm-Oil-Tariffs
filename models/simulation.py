import numpy as np
import pandas as pd

# Elasticity coefficients derived from econometric analysis of India CPO trade
IMPORT_ELASTICITY = -0.018       # % change in import per 1% tariff increase
FARMER_PRICE_SENSITIVITY = 0.52  # INR/kg per 1% tariff (recalibrated)
CONSUMER_MARKUP = 6.5            # consumer price per kg derived from retail spread
CONSUMER_FIXED = 126.0           # baseline consumer retail floor (INR/kg)
CULTIVATION_RESPONSE = 0.0012    # mha per 1% tariff

# Baseline calibrated to REAL February 2025 India CPO market data:
# - Customs duty:    16.5% (actual current rate)
# - Global CPO:      ~$1086/ton (actual market price)
# - Farmer price:    ₹20.87/kg  (FFB mandi rate ₹20,871/ton ÷ 1000)
# - Consumer price:  ₹146/kg    (mid-range of ₹126–166 retail band)
# - Import volume:   ~0.72 MT/month
# - Import dependency: ~92% (India imports ~92% of palm oil needs)
BASE = {
    'tariff': 16.5,
    'global_price_usd': 1086.0,
    'import_volume': 0.72,
    'domestic_production': 0.063,   # India produces ~63k MT/month domestically
    'farmer_price': 20.87,          # ₹/kg (FFB rate)
    'consumer_price': 146.0,        # ₹/kg (retail mid-range)
    'import_dependency': 92.0,      # India is ~92% import dependent on palm oil
    'cultivation_area': 0.41        # ~0.41 million hectares under oil palm
}

def simulate_tariff_impact(tariff_rate: float, global_price_usd: float = 1086.0) -> dict:
    """
    Simulate the economic impact of a given customs duty rate on CPO imports.
    Calibrated to real February 2025 India market data.

    Parameters:
        tariff_rate: Customs duty in percentage (0–100)
        global_price_usd: Global CPO price in USD/ton

    Returns:
        Dictionary of predicted economic indicators
    """
    delta_tariff = tariff_rate - BASE['tariff']
    delta_price  = global_price_usd - BASE['global_price_usd']

    # Import volume response (falls as tariff rises)
    import_volume = BASE['import_volume'] + IMPORT_ELASTICITY * delta_tariff
    import_volume = max(0.05, import_volume)

    # Domestic production (slight increase as tariff rises — incentivises local farming)
    domestic_production = BASE['domestic_production'] + 0.0008 * delta_tariff
    domestic_production = min(domestic_production, 0.40)

    # Import dependency
    total_demand = import_volume + domestic_production
    import_dependency = (import_volume / total_demand) * 100

    # Farmer FFB price (INR/kg) — rises with tariff AND global price
    # Global price effect: converted at ~84 INR/USD, spread across processing margin
    global_price_effect = delta_price * 0.084 * 0.15   # 15% passthrough to FFB farmer
    farmer_price = BASE['farmer_price'] + FARMER_PRICE_SENSITIVITY * delta_tariff + global_price_effect
    farmer_price = max(10.0, farmer_price)

    # Consumer retail price (INR/kg) — based on global CPO cost + tariff + processing + retail margins
    # Formula: (Global price in INR/ton × (1 + tariff/100) + processing) / 1000 + retail margin
    inr_per_usd = 84.0
    cpo_inr_per_kg = (global_price_usd * inr_per_usd / 1000) * (1 + tariff_rate / 100)
    processing_margin = 28.0   # INR/kg (refining, packaging, transport)
    retail_margin = 22.0       # INR/kg (distributor + retailer)
    consumer_price = cpo_inr_per_kg + processing_margin + retail_margin
    consumer_price = max(100.0, consumer_price)

    # Cultivation area
    cultivation_area = BASE['cultivation_area'] + CULTIVATION_RESPONSE * delta_tariff
    cultivation_area = max(0.30, cultivation_area)

    # Compute % change vs baseline
    def pct_change(new, base):
        return round(((new - base) / base) * 100, 2)

    return {
        'tariff_rate': round(tariff_rate, 1),
        'global_price_usd': round(global_price_usd, 2),
        'import_volume_mt': round(import_volume, 4),
        'domestic_production_mt': round(domestic_production, 4),
        'import_dependency_pct': round(import_dependency, 2),
        'farmer_price_inr': round(farmer_price, 2),
        'consumer_price_inr': round(consumer_price, 2),
        'cultivation_area_mha': round(cultivation_area, 4),
        'import_volume_change_pct': pct_change(import_volume, BASE['import_volume']),
        'farmer_price_change_pct': pct_change(farmer_price, BASE['farmer_price']),
        'consumer_price_change_pct': pct_change(consumer_price, BASE['consumer_price']),
        'cultivation_change_pct': pct_change(cultivation_area, BASE['cultivation_area']),
        'import_dependency_change_pct': pct_change(import_dependency, BASE['import_dependency']),
    }

def compare_scenarios(tariff_list: list, global_price: float = 1086.0) -> pd.DataFrame:
    """Compare multiple tariff scenarios side by side."""
    rows = [simulate_tariff_impact(t, global_price) for t in tariff_list]
    return pd.DataFrame(rows)

def get_forecast_series(tariff_rate: float, months: int = 12) -> pd.DataFrame:
    """Generate month-by-month forecast under a given tariff."""
    base_result = simulate_tariff_impact(tariff_rate)
    dates = pd.date_range(start='2026-01-01', periods=months, freq='MS')

    seasonal_import = 0.04 * np.sin(2 * np.pi * np.arange(months) / 12)
    seasonal_price = 3.0 * np.sin(2 * np.pi * np.arange(months) / 12 + 1)

    return pd.DataFrame({
        'date': dates,
        'import_volume_mt': np.clip(base_result['import_volume_mt'] + seasonal_import + np.random.normal(0, 0.02, months), 0.05, 1.5),
        'farmer_price_inr': base_result['farmer_price_inr'] + seasonal_price + np.random.normal(0, 1.5, months),
        'consumer_price_inr': base_result['consumer_price_inr'] + seasonal_price * 1.3 + np.random.normal(0, 2, months),
        'import_dependency_pct': base_result['import_dependency_pct'] + np.random.normal(0, 0.5, months),
    })

if __name__ == "__main__":
    result = simulate_tariff_impact(20.0)
    print("Scenario at 20% tariff:")
    for k, v in result.items():
        print(f"  {k}: {v}")

    df = compare_scenarios([0, 5, 10, 20, 30, 50])
    print("\nScenario Comparison:")
    print(df[['tariff_rate', 'import_volume_mt', 'farmer_price_inr', 'consumer_price_inr', 'import_dependency_pct']])