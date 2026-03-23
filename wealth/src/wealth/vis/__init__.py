"""Visualization module for Wealth platform."""

from wealth.vis.base import ChartType, ChartTheme, BaseChart
from wealth.vis.stock_charts import StockChartGenerator, CandlestickChart, VolumeChart
from wealth.vis.backtest_charts import BacktestChartGenerator, EquityCurveChart, DrawdownChart
from wealth.vis.indicator_charts import IndicatorChartGenerator, MACDChart, KDJChart, BollingerChart
from wealth.vis.prediction_charts import PredictionChartGenerator
from wealth.vis.dashboard import DashboardGenerator

__all__ = [
    "ChartType",
    "ChartTheme",
    "BaseChart",
    "StockChartGenerator",
    "CandlestickChart",
    "VolumeChart",
    "BacktestChartGenerator",
    "EquityCurveChart",
    "DrawdownChart",
    "IndicatorChartGenerator",
    "MACDChart",
    "KDJChart",
    "BollingerChart",
    "PredictionChartGenerator",
    "DashboardGenerator",
]
