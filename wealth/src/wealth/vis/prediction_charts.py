"""Prediction chart visualization generators."""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from wealth.vis.base import BaseChart, ChartConfig, ChartTheme


class PredictionChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, ax = plt.subplots(figsize=(14, 7))
        else:
            ax = self._figure.axes[0]
            ax.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        historical = data[data['type'] == 'historical'] if 'type' in data.columns else data.iloc[:len(data)//2]
        predicted = data[data['type'] == 'predicted'] if 'type' in data.columns else data.iloc[len(data)//2:]

        ax.plot(range(len(historical)), historical['value'], color=colors["accent"], linewidth=2, label='历史数据')

        if len(predicted) > 0:
            pred_dates = range(len(historical), len(historical) + len(predicted))
            ax.plot(pred_dates, predicted['value'], color=colors["up_color"], linewidth=2, linestyle='--', label='预测')

            if 'lower' in predicted.columns and 'upper' in predicted.columns:
                ax.fill_between(pred_dates, predicted['lower'], predicted['upper'], alpha=0.2, color=colors["accent"])

        ax.axvline(x=len(historical)-1, color=colors["text"], linestyle=':', linewidth=1, alpha=0.5)

        ax.set_xlabel("时间", color=colors["text"])
        ax.set_ylabel("价格", color=colors["text"])
        ax.tick_params(colors=colors["text"])
        ax.grid(True, alpha=0.3, color=colors["grid"])
        ax.legend(loc="upper left", facecolor=colors["background"], labelcolor=colors["text"])

        if self.config.title:
            ax.set_title(self.config.title, color=colors["text"], fontsize=14)

        self._figure.tight_layout()
        return self._figure

    def to_html(self) -> str:
        return ""


class ConfidenceIntervalChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, ax = plt.subplots(figsize=(14, 6))
        else:
            ax = self._figure.axes[0]
            ax.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        if 'predicted' in data.columns:
            ax.plot(range(len(data)), data['actual'], color=colors["text"], linewidth=2, label='实际值')
            ax.plot(range(len(data)), data['predicted'], color=colors["accent"], linewidth=2, linestyle='--', label='预测值')
        else:
            ax.plot(range(len(data)), data['value'], color=colors["accent"], linewidth=2, label='预测值')

        if 'lower' in data.columns and 'upper' in data.columns:
            ax.fill_between(range(len(data)), data['lower'], data['upper'], alpha=0.2, color=colors["accent"])

        ax.set_xlabel("样本", color=colors["text"])
        ax.set_ylabel("值", color=colors["text"])
        ax.tick_params(colors=colors["text"])
        ax.grid(True, alpha=0.3, color=colors["grid"])
        ax.legend(loc="upper left", facecolor=colors["background"], labelcolor=colors["text"])

        if self.config.title:
            ax.set_title(self.config.title, color=colors["text"], fontsize=14)

        self._figure.tight_layout()
        return self._figure

    def to_html(self) -> str:
        return ""


class FeatureImportanceChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, ax = plt.subplots(figsize=(10, 6))
        else:
            ax = self._figure.axes[0]
            ax.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        if 'importance' in data.columns and 'feature' in data.columns:
            sorted_data = data.sort_values('importance', ascending=True)
            y_pos = range(len(sorted_data))
            ax.barh(y_pos, sorted_data['importance'], color=colors["accent"], alpha=0.8)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(sorted_data['feature'])
        else:
            features = data.get('feature', data.index if hasattr(data, 'index') else range(len(data)))
            importance = data.get('importance', data.values.flatten() if hasattr(data, 'values') else data)
            sorted_idx = np.argsort(importance)
            ax.barh(range(len(sorted_idx)), importance[sorted_idx], color=colors["accent"], alpha=0.8)
            ax.set_yticks(range(len(sorted_idx)))
            ax.set_yticklabels([str(features[i]) for i in sorted_idx])

        ax.set_xlabel("重要性", color=colors["text"])
        ax.tick_params(colors=colors["text"])
        ax.grid(True, alpha=0.3, color=colors["grid"], axis='x')

        if self.config.title:
            ax.set_title(self.config.title, color=colors["text"], fontsize=14)

        self._figure.tight_layout()
        return self._figure

    def to_html(self) -> str:
        return ""


class PredictionChartGenerator:
    def __init__(self, theme: ChartTheme = ChartTheme.DARK):
        self.theme = theme

    def create_prediction(self, data: pd.DataFrame, title: str = "价格预测") -> PredictionChart:
        config = ChartConfig(title=title, theme=self.theme)
        chart = PredictionChart(config)
        chart.generate(data)
        return chart

    def create_confidence_interval(self, data: pd.DataFrame, title: str = "预测置信区间") -> ConfidenceIntervalChart:
        config = ChartConfig(title=title, theme=self.theme)
        chart = ConfidenceIntervalChart(config)
        chart.generate(data)
        return chart

    def create_feature_importance(self, data: pd.DataFrame, title: str = "特征重要性") -> FeatureImportanceChart:
        config = ChartConfig(title=title, theme=self.theme)
        chart = FeatureImportanceChart(config)
        chart.generate(data)
        return chart

    def create_residuals_plot(self, actual: np.ndarray, predicted: np.ndarray, title: str = "残差分析") -> Any:
        fig, ax = plt.subplots(figsize=(12, 5))

        colors = self._get_theme_colors()
        fig.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        residuals = actual - predicted
        ax.scatter(predicted, residuals, color=colors["accent"], alpha=0.6)
        ax.axhline(y=0, color=colors["text"], linewidth=1)

        ax.set_xlabel("预测值", color=colors["text"])
        ax.set_ylabel("残差", color=colors["text"])
        ax.tick_params(colors=colors["text"])
        ax.grid(True, alpha=0.3, color=colors["grid"])

        if title:
            ax.set_title(title, color=colors["text"], fontsize=14)

        fig.tight_layout()
        return fig

    def _get_theme_colors(self) -> Dict[str, str]:
        if self.theme == ChartTheme.DARK:
            return {
                "background": "#0a0e17", "text": "#ffffff", "grid": "#333333",
                "up_color": "#ef5350", "down_color": "#26a69a", "accent": "#667eea",
            }
        return {
            "background": "#ffffff", "text": "#000000", "grid": "#e0e0e0",
            "up_color": "#ef5350", "down_color": "#26a69a", "accent": "#667eea",
        }
