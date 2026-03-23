"""Stock chart visualization generators."""

from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns

from wealth.vis.base import BaseChart, ChartConfig, ChartTheme, ChartType


class CandlestickChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, ax = plt.subplots(figsize=(16, 8))
        else:
            ax = self._figure.axes[0]
            ax.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        if "timestamp" in data.columns:
            data["date"] = pd.to_datetime(data["timestamp"])
        elif "date" in data.columns:
            data["date"] = pd.to_datetime(data["date"])

        for idx, (_, row) in enumerate(data.iterrows()):
            open_price = row.get("open", row.get("Open", 0))
            close_price = row.get("close", row.get("Close", 0))
            high_price = row.get("high", row.get("High", 0))
            low_price = row.get("low", row.get("Low", 0))

            color = colors["up_color"] if close_price >= open_price else colors["down_color"]

            body_height = abs(close_price - open_price)
            body_bottom = min(open_price, close_price)

            ax.plot([idx, idx], [low_price, high_price], color=color, linewidth=0.8)
            rect = Rectangle((idx - 0.3, body_bottom), 0.6, body_height if body_height > 0 else 0.1,
                           facecolor=color, edgecolor=color)
            ax.add_patch(rect)

        dates = pd.to_datetime(data["date"])
        ax.set_xlim(-1, len(data))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        ax.set_xlabel("日期", color=colors["text"])
        ax.set_ylabel("价格", color=colors["text"])
        ax.tick_params(colors=colors["text"])
        ax.grid(True, alpha=0.3, color=colors["grid"])

        if self.config.title:
            ax.set_title(self.config.title, color=colors["text"], fontsize=14)

        self._figure.tight_layout()
        return self._figure

    def to_html(self) -> str:
        if self._figure is None:
            raise ValueError("Chart not generated yet")
        from matplotlib import use
        use('Agg')
        buffer = BytesIO()
        self._figure.savefig(buffer, format='svg', bbox_inches='tight')
        return buffer.getvalue().decode()


class VolumeChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [3, 1]})
        else:
            ax1, ax2 = self._figure.axes[0], self._figure.axes[1]
            ax1.clear()
            ax2.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax1.set_facecolor(colors["background"])
        ax2.set_facecolor(colors["background"])

        if "timestamp" in data.columns:
            data["date"] = pd.to_datetime(data["timestamp"])
        elif "date" in data.columns:
            data["date"] = pd.to_datetime(data["date"])

        close_prices = data.get("close", data.get("Close", data["close"] if "close" in data else data["Close"]))
        open_prices = data.get("open", data.get("Open", data["open"] if "open" in data else data["Open"]))
        volumes = data.get("volume", data.get("Volume", data["volume"] if "volume" in data else data["Volume"]))

        colors_vol = [colors["up_color"] if close_prices.iloc[i] >= open_prices.iloc[i] else colors["down_color"]
                     for i in range(len(data))]

        ax2.bar(range(len(data)), volumes, color=colors_vol, alpha=0.7)

        if "ma5" in data.columns or "sma_5" in data.columns:
            ma = data.get("ma5", data.get("sma_5", None))
            if ma is not None:
                ax1.plot(range(len(data)), ma, color=colors["accent"], label="MA5", linewidth=1.5)

        ax2.set_xlabel("日期", color=colors["text"])
        ax1.set_ylabel("价格", color=colors["text"])
        ax2.set_ylabel("成交量", color=colors["text"])
        ax1.tick_params(colors=colors["text"])
        ax2.tick_params(colors=colors["text"])
        ax2.grid(True, alpha=0.3, color=colors["grid"])

        if self.config.title:
            self._figure.suptitle(self.config.title, color=colors["text"])

        self._figure.tight_layout()
        return self._figure

    def to_html(self) -> str:
        from matplotlib import use
        use('Agg')
        buffer = BytesIO()
        self._figure.savefig(buffer, format='html')
        return buffer.getvalue().decode()


class StockChartGenerator:
    def __init__(self, theme: ChartTheme = ChartTheme.DARK):
        self.theme = theme

    def create_candlestick_chart(self, data: pd.DataFrame, title: str = "K线图") -> CandlestickChart:
        config = ChartConfig(title=title, theme=self.theme)
        chart = CandlestickChart(config)
        chart.generate(data)
        return chart

    def create_volume_chart(self, data: pd.DataFrame, title: str = "成交量") -> VolumeChart:
        config = ChartConfig(title=title, theme=self.theme)
        chart = VolumeChart(config)
        chart.generate(data)
        return chart

    def create_combine_chart(self, data: pd.DataFrame, indicators: List[str] = None) -> Any:
        if self._figure is None:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), gridspec_kw={'height_ratios': [3, 1]})

        colors = self._get_theme_colors_for(ChartTheme.DARK)
        fig.patch.set_facecolor(colors["background"])

        if "timestamp" in data.columns:
            data["date"] = pd.to_datetime(data["timestamp"])
        elif "date" in data.columns:
            data["date"] = pd.to_datetime(data["date"])

        idx = range(len(data))

        for i, (_, row) in enumerate(data.iterrows()):
            open_p = row.get("open", row.get("Open", 0))
            close_p = row.get("close", row.get("Close", 0))
            high_p = row.get("high", row.get("High", 0))
            low_p = row.get("low", row.get("Low", 0))
            color = colors["up_color"] if close_p >= open_p else colors["down_color"]

            ax1.plot([i, i], [low_p, high_p], color=color, linewidth=0.8)
            body_height = abs(close_p - open_p) if abs(close_p - open_p) > 0 else 0.1
            rect = Rectangle((i - 0.3, min(open_p, close_p)), 0.6, body_height,
                           facecolor=color, edgecolor=color)
            ax1.add_patch(rect)

        if indicators:
            for ind in indicators:
                if ind == "ma5" and "sma_5" in data.columns:
                    ax1.plot(idx, data["sma_5"], color="#ff6b6b", label="MA5", linewidth=1.2)
                elif ind == "ma10" and "sma_10" in data.columns:
                    ax1.plot(idx, data["sma_10"], color="#4ecdc4", label="MA10", linewidth=1.2)
                elif ind == "ma20" and "sma_20" in data.columns:
                    ax1.plot(idx, data["sma_20"], color="#45b7d1", label="MA20", linewidth=1.2)

        volumes = data.get("volume", data.get("Volume", [0]*len(data)))
        vol_colors = [colors["up_color"] if data["close"].iloc[i] >= data["open"].iloc[i]
                     else colors["down_color"] for i in range(len(data))]
        ax2.bar(idx, volumes, color=vol_colors, alpha=0.7)

        ax1.set_ylabel("价格", color=colors["text"])
        ax2.set_ylabel("成交量", color=colors["text"])
        ax1.tick_params(colors=colors["text"])
        ax2.tick_params(colors=colors["text"])
        ax1.grid(True, alpha=0.3, color=colors["grid"])
        ax2.grid(True, alpha=0.3, color=colors["grid"])
        ax1.legend(loc="upper left", facecolor=colors["background"], labelcolor=colors["text"])

        fig.tight_layout()
        return fig

    def _get_theme_colors_for(self, theme: ChartTheme) -> Dict[str, str]:
        if theme == ChartTheme.DARK:
            return {
                "background": "#0a0e17", "text": "#ffffff", "grid": "#333333",
                "up_color": "#ef5350", "down_color": "#26a69a", "accent": "#667eea",
            }
        return {
            "background": "#ffffff", "text": "#000000", "grid": "#e0e0e0",
            "up_color": "#ef5350", "down_color": "#26a69a", "accent": "#667eea",
        }

    def _figure(self):
        return self._figure
