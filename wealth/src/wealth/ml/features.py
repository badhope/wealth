"""Feature engineering for ML models."""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class FeatureEngine:
    def __init__(self):
        self.scalers: Dict[str, StandardScaler] = {}

    def create_features(self, data: pd.DataFrame, include_indicators: bool = True) -> pd.DataFrame:
        df = data.copy()

        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))

        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_60'] = df['close'].rolling(window=60).mean()

        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()

        df['volume_sma_5'] = df['volume'].rolling(window=5).mean()
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma_20']

        df['price_sma5_ratio'] = df['close'] / df['sma_5']
        df['price_sma10_ratio'] = df['close'] / df['sma_10']
        df['price_sma20_ratio'] = df['close'] / df['sma_20']

        df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
        df['close_open_ratio'] = (df['close'] - df['open']) / df['open']

        for window in [5, 10, 20]:
            df[f'volatility_{window}'] = df['returns'].rolling(window=window).std()

        df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
        df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
        df['momentum_20'] = df['close'] / df['close'].shift(20) - 1

        df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'] + 1e-10)

        if include_indicators and 'rsi' not in df.columns:
            df['rsi'] = self._calculate_rsi(df['close'])

        if include_indicators and 'macd_dif' not in df.columns:
            df['macd_dif'], df['macd_dea'], df['macd_bar'] = self._calculate_macd(df['close'])

        if include_indicators and 'kdj_k' not in df.columns:
            df['kdj_k'], df['kdj_d'], df['kdj_j'] = self._calculate_kdj(df)

        if include_indicators and 'bb_upper' not in df.columns:
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = self._calculate_bollinger(df['close'])

        df.dropna(inplace=True)

        return df

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        return 100 - (100 / (1 + rs))

    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal, adjust=False).mean()
        bar = 2 * (dif - dea)
        return dif, dea, bar

    def _calculate_kdj(self, data: pd.DataFrame, period: int = 9) -> tuple:
        low_n = data['low'].rolling(window=period).min()
        high_n = data['high'].rolling(window=period).max()
        rsv = (data['close'] - low_n) / (high_n - low_n + 1e-10) * 100
        k = rsv.ewm(com=2, adjust=False).mean()
        d = k.ewm(com=2, adjust=False).mean()
        j = 3 * k - 2 * d
        return k, d, j

    def _calculate_bollinger(self, prices: pd.Series, period: int = 20, std_dev: int = 2):
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower

    def scale_features(self, data: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
        df = data.copy()
        scaler = StandardScaler()
        df[feature_cols] = scaler.fit_transform(df[feature_cols])
        self.scalers['default'] = scaler
        return df

    def create_lag_features(self, data: pd.DataFrame, target: str, lags: List[int] = [1, 2, 3, 5, 10]) -> pd.DataFrame:
        df = data.copy()
        for lag in lags:
            df[f'{target}_lag_{lag}'] = df[target].shift(lag)
        df.dropna(inplace=True)
        return df

    def create_rolling_features(self, data: pd.DataFrame, columns: List[str], windows: List[int] = [5, 10, 20]) -> pd.DataFrame:
        df = data.copy()
        for col in columns:
            for window in windows:
                df[f'{col}_rolling_mean_{window}'] = df[col].rolling(window=window).mean()
                df[f'{col}_rolling_std_{window}'] = df[col].rolling(window=window).std()
        df.dropna(inplace=True)
        return df

    def get_feature_importance(self, model, feature_names: List[str]) -> pd.DataFrame:
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importance = np.abs(model.coef_)
        else:
            return pd.DataFrame()

        return pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
