"""Technical indicator chart generators."""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from wealth.vis.base import BaseChart, ChartConfig, ChartTheme


class MACDChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [2, 1]})
        else:
            ax1, ax2 = self._figure.axes[0], self._figure.axes[1]
            ax1.clear()
            ax2.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax1.set_facecolor(colors["background"])
        ax2.set_facecolor(colors["background"])

        close = data['close'] if 'close' in data.columns else data['Close']
        dates = range(len(data))

        ax1.plot(dates, close, color=colors["text"], linewidth=1.5, label='收盘价')

        if 'sma_20' in data.columns:
            ax1.plot(dates, data['sma_20'], color=colors["accent"], linewidth=1, label='MA20')

        dif = data['macd_dif'] if 'macd_dif' in data.columns else data.get('dif', None)
        dea = data['macd_dea'] if 'macd_dea' in data.columns else data.get('dea', None)
        macd_bar = data['macd_bar'] if 'macd_bar' in data.columns else data.get('macd_bar', None)

        if dif is not None and dea is not None:
            ax2.plot(dates, dif, color="#3498db", linewidth=1, label='DIF')
            ax2.plot(dates, dea, color="#e74c3c", linewidth=1, label='DEA')

            if macd_bar is not None:
                bar_colors = [colors["up_color"] if b >= 0 else colors["down_color"] for b in macd_bar]
                ax2.bar(dates, macd_bar, color=bar_colors, alpha=0.5, width=0.8)

        ax1.set_ylabel("价格", color=colors["text"])
        ax2.set_ylabel("MACD", color=colors["text"])
        ax1.tick_params(colors=colors["text"])
        ax2.tick_params(colors=colors["text"])
        ax1.grid(True, alpha=0.3, color=colors["grid"])
        ax2.grid(True, alpha=0.3, color=colors["grid"])
        ax1.legend(loc="upper left", facecolor=colors["background"], labelcolor=colors["text"])
        ax2.legend(loc="upper left", facecolor=colors["background"], labelcolor=colors["text"])

        if self.config.title:
            self._figure.suptitle(self.config.title, color=colors["text"])

        self._figure.tight_layout()
        return self._figure

    def to_html(self) -> str:
        return ""


class KDJChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, ax = plt.subplots(figsize=(14, 6))
        else:
            ax = self._figure.axes[0]
            ax.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        dates = range(len(data))

        k = data['kdj_k'] if 'kdj_k' in data.columns else data.get('k', None)
        d = data['kdj_d'] if 'kdj_d' in data.columns else data.get('d', None)
        j = data['kdj_j'] if 'kdj_j' in data.columns else data.get('j', None)

        if k is not None:
            ax.plot(dates, k, color="#3498db", linewidth=1.5, label='K')
        if d is not None:
            ax.plot(dates, d, color="#e74c3c", linewidth=1.5, label='D')
        if j is not None:
            ax.plot(dates, j, color="#2ecc71", linewidth=1, label='J', alpha=0.7)

        ax.axhline(y=80, color=colors["down_color"], linestyle='--', linewidth=0.8, alpha=0.5)
        ax.axhline(y=20, color=colors["up_color"], linestyle='--', linewidth=0.8, alpha=0.5)
        ax.fill_between(dates, 80, 100, alpha=0.1, color=colors["down_color"])
        ax.fill_between(dates, 0, 20, alpha=0.1, color=colors["up_color"])

        ax.set_xlabel("日期", color=colors["text"])
        ax.set_ylabel("KDJ", color=colors["text"])
        ax.tick_params(colors=colors["text"])
        ax.grid(True, alpha=0.3, color=colors["grid"])
        ax.legend(loc="upper left", facecolor=colors["background"], labelcolor=colors["text"])
        ax.set_ylim(-10, 110)

        if self.config.title:
            ax.set_title(self.config.title, color=colors["text"], fontsize=14)

        self._figure.tight_layout()
        return self._figure

    def to_html(self) -> str:
        return ""


class BollingerChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, ax = plt.subplots(figsize=(14, 7))
        else:
            ax = self._figure.axes[0]
            ax.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        close = data['close'] if 'close' in data.columns else data['Close']
        dates = range(len(data))

        ax.plot(dates, close, color=colors["text"], linewidth=1.5, label='收盘价')

        if 'bb_upper' in data.columns and 'bb_middle' in data.columns and 'bb_lower' in data.columns:
            ax.plot(dates, data['bb_upper'], color=colors["accent"], linewidth=1, linestyle='--', label='布林上轨')
            ax.plot(dates, data['bb_middle'], color=colors["accent"], linewidth=1, label='布林中轨')
            ax.plot(dates, data['bb_lower'], color=colors["accent"], linewidth=1, linestyle='--', label='布林下轨')
            ax.fill_between(dates, data['bb_upper'], data['bb_lower'], alpha=0.1, color=colors["accent"])

        ax.set_xlabel("日期", color=colors["text"])
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


class RSIChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, ax = plt.subplots(figsize=(14, 5))
        else:
            ax = self._figure.axes[0]
            ax.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        dates = range(len(data))
        rsi = data['rsi'] if 'rsi' in data.columns else None

        if rsi is not None:
            ax.plot(dates, rsi, color="#9b59b6", linewidth=1.5, label='RSI')

        ax.axhline(y=70, color=colors["down_color"], linestyle='--', linewidth=0.8)
        ax.axhline(y=30, color=colors["up_color"], linestyle='--', linewidth=0.8)
        ax.fill_between(dates, 70, 100, alpha=0.1, color=colors["down_color"])
        ax.fill_between(dates, 0, 30, alpha=0.1, color=colors["up_color"])

        ax.set_xlabel("日期", color=colors["text"])
        ax.set_ylabel("RSI", color=colors["text"])
        ax.tick_params(colors=colors["text"])
        ax.grid(True, alpha=0.3, color=colors["grid"])
        ax.legend(loc="upper left", facecolor=colors["background"], labelcolor=colors["text"])
        ax.set_ylim(-5, 105)

        if self.config.title:
            ax.set_title(self.config.title, color=colors["text"], fontsize=14)

        self._figure.tight_layout()
        return self._figure

    def to_html(self) -> str:
        return ""


class IndicatorChartGenerator:
    def __init__(self, theme: ChartTheme = ChartTheme.DARK):
        self.theme = theme

    def create_macd(self, data: pd.DataFrame, title: str = "MACD指标") -> MACDChart:
        config = ChartConfig(title=title, theme=self.theme)
        return MACDChart(config).generate(data) or MACDChart(config)

    def create_kdj(self, data: pd.DataFrame, title: str = "KDJ指标") -> KDJChart:
        config = ChartConfig(title=title, theme=self.theme)
        return KDJChart(config).generate(data) or KDJChart(config)

    def create_bollinger(self, data: pd.DataFrame, title: str = "布林带") -> BollingerChart:
        config = ChartConfig(title=title, theme=self.theme)
        return BollingerChart(config).generate(data) or BollingerChart(config)

    def create_rsi(self, data: pd.DataFrame, title: str = "RSI指标") -> RSIChart:
        config = ChartConfig(title=title, theme=self.theme)
        return RSIChart(config).generate(data) or RSIChart(config)

    def create_all_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        charts = {}
        charts['macd'] = self.create_macd(data)
        charts['kdj'] = self.create_kdj(data)
        charts['bollinger'] = self.create_bollinger(data)
        charts['rsi'] = self.create_rsi(data)
        return charts
