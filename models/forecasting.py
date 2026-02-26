import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

def load_data():
    df = pd.read_csv('data/cpo_data.csv', parse_dates=['date'])
    return df

def evaluate(y_true, y_pred, name="Model"):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    print(f"\n📊 {name} Evaluation:")
    print(f"   MAE:  {mae:.4f}")
    print(f"   RMSE: {rmse:.4f}")
    print(f"   R²:   {r2:.4f}")
    return {'mae': mae, 'rmse': rmse, 'r2': r2}

def train_import_forecaster(df):
    features = ['tariff_rate', 'global_cpo_price_usd', 'domestic_production_mt']
    X = df[features].values
    y = df['import_volume_mt'].values
    split = int(len(X) * 0.8)
    model = GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42)
    model.fit(X[:split], y[:split])
    metrics = evaluate(y[split:], model.predict(X[split:]), "Import Volume Forecaster")
    return model, metrics

def train_price_forecaster(df):
    features = ['tariff_rate', 'global_cpo_price_usd', 'import_volume_mt']
    X = df[features].values
    y = df['farmer_price_inr'].values
    split = int(len(X) * 0.8)
    model = GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42)
    model.fit(X[:split], y[:split])
    metrics = evaluate(y[split:], model.predict(X[split:]), "Farmer Price Forecaster")
    return model, metrics

def train_consumer_price_forecaster(df):
    features = ['tariff_rate', 'global_cpo_price_usd', 'import_volume_mt', 'farmer_price_inr']
    X = df[features].values
    y = df['consumer_price_inr'].values
    split = int(len(X) * 0.8)
    model = GradientBoostingRegressor(n_estimators=150, random_state=42)
    model.fit(X[:split], y[:split])
    metrics = evaluate(y[split:], model.predict(X[split:]), "Consumer Price Forecaster")
    return model, metrics

if __name__ == "__main__":
    df = load_data()
    train_import_forecaster(df)
    train_price_forecaster(df)
    train_consumer_price_forecaster(df)
    print("\n✅ All models trained successfully.")