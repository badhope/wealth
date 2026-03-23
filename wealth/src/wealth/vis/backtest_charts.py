"""Backtest chart visualization generators."""

from typing import List, Dict, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

from wealth.vis.base import BaseChart, ChartConfig, ChartTheme


class EquityCurveChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, ax = plt.subplots(figsize=(14, 7))
        else:
            ax = self._figure.axes[0]
            ax.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        dates = pd.to_datetime(data.index if hasattr(data, 'index') else data.get('date', data.get('timestamp', range(len(data)))))
        values = data['value'] if 'value' in data.columns else data

        ax.fill_between(dates, values, alpha=0.3, color=colors["accent"])
        ax.plot(dates, values, color=colors["accent"], linewidth=2, label='账户价值')

        if 'cash' in data.columns:
            ax.plot(dates, data['cash'], color=colors["text"], linewidth=1, linestyle='--', alpha=0.5, label='现金')

        ax.set_xlabel("日期", color=colors["text"])
        ax.set_ylabel("价值", color=colors["text"])
        ax.tick_params(colors=colors["text"])
        ax.grid(True, alpha=0.3, color=colors["grid"])
        ax.legend(loc="upper left", facecolor=colors["background"], labelcolor=colors["text"])

        if self.config.title:
            ax.set_title(self.config.title, color=colors["text"], fontsize=14)

        self._figure.tight_layout()
        return self._figure

    def to_html(self) -> str:
        from matplotlib import use
        use('Agg')
        buffer = plt.Buffer
        return ""


class DrawdownChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, ax = plt.subplots(figsize=(14, 6))
        else:
            ax = self._figure.axes[0]
            ax.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        if 'drawdown' in data.columns:
            drawdown = data['drawdown']
        else:
            values = data['value'] if 'value' in data.columns else data
            cummax = np.maximum.accumulate(values)
            drawdown = (values - cummax) / cummax * 100

        dates = pd.to_datetime(data.index if hasattr(data, 'index') else range(len(data)))

        ax.fill_between(dates, drawdown, 0, alpha=0.5, color=colors["down_color"])
        ax.plot(dates, drawdown, color=colors["down_color"], linewidth=1.5)

        ax.set_xlabel("日期", color=colors["text"])
        ax.set_ylabel("回撤 (%)", color=colors["text"])
        ax.tick_params(colors=colors["text"])
        ax.grid(True, alpha=0.3, color=colors["grid"])

        if self.config.title:
            ax.set_title(self.config.title, color=colors["text"], fontsize=14)

        self._figure.tight_layout()
        return self._figure

    def to_html(self) -> str:
        return ""


class MonthlyReturnChart(BaseChart):
    def generate(self, data: pd.DataFrame) -> Any:
        if self._figure is None:
            self._figure, ax = plt.subplots(figsize=(14, 6))
        else:
            ax = self._figure.axes[0]
            ax.clear()

        colors = self._get_theme_colors()
        self._figure.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        if 'return' in data.columns:
            returns = data['return']
        else:
            returns = data['value'].pct_change().dropna() * 100 if 'value' in data.columns else []

        months = range(1, len(returns) + 1)
        bar_colors = [colors["up_color"] if r >= 0 else colors["down_color"] for r in returns]

        ax.bar(months, returns, color=bar_colors, alpha=0.8)
        ax.axhline(y=0, color=colors["text"], linewidth=0.5)

        ax.set_xlabel("月份", color=colors["text"])
        ax.set_ylabel("收益率 (%)", color=colors["text"])
        ax.tick_params(colors=colors["text"])
        ax.grid(True, alpha=0.3, color=colors["grid"], axis='y')

        if self.config.title:
            ax.set_title(self.config.title, color=colors["text"], fontsize=14)

        self._figure.tight_layout()
        return self._figure

    def to_html(self) -> str:
        return ""


class BacktestChartGenerator:
    def __init__(self, theme: ChartTheme = ChartTheme.DARK):
        self.theme = theme

    def create_equity_curve(self, data: pd.DataFrame, title: str = "资金曲线") -> EquityCurveChart:
        config = ChartConfig(title=title, theme=self.theme)
        chart = EquityCurveChart(config)
        chart.generate(data)
        return chart

    def create_drawdown_chart(self, data: pd.DataFrame, title: str = "回撤分析") -> DrawdownChart:
        config = ChartConfig(title=title, theme=self.theme)
        chart = DrawdownChart(config)
        chart.generate(data)
        return chart

    def create_monthly_returns(self, data: pd.DataFrame, title: str = "月度收益") -> MonthlyReturnChart:
        config = ChartConfig(title=title, theme=self.theme)
        chart = MonthlyReturnChart(config)
        chart.generate(data)
        return chart

    def create_trade_distribution(self, trades: List[Dict], title: str = "交易分布") -> Any:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        colors = self._get_theme_colors()
        fig.patch.set_facecolor(colors["background"])
        for ax in axes:
            ax.set_facecolor(colors["background"])

        pnls = [t['pnl'] for t in trades]
        axes[0].hist(pnls, bins=30, color=colors["accent"], alpha=0.7, edgecolor=colors["text"])
        axes[0].axvline(x=0, color=colors["text"], linewidth=1)
        axes[0].set_xlabel("盈亏", color=colors["text"])
        axes[0].set_ylabel("次数", color=colors["text"])
        axes[0].set_title("盈亏分布", color=colors["text"])

        holding_days = [t['holding_days'] for t in trades]
        axes[1].hist(holding_days, bins=20, color=colors["accent"], alpha=0.7, edgecolor=colors["text"])
        axes[1].set_xlabel("持有天数", color=colors["text"])
        axes[1].set_ylabel("次数", color=colors["text"])
        axes[1].set_title("持仓周期分布", color=colors["text"])

        for ax in axes:
            ax.tick_params(colors=colors["text"])
            ax.grid(True, alpha=0.3, color=colors["grid"])

        if title:
            fig.suptitle(title, color=colors["text"])

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
