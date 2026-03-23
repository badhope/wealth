"""Dashboard generator for system monitoring and overview."""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from wealth.vis.base import ChartConfig, ChartTheme


class DashboardGenerator:
    def __init__(self, theme: ChartTheme = ChartTheme.DARK):
        self.theme = theme

    def create_system_dashboard(self, metrics: Dict[str, Any]) -> Any:
        fig = plt.figure(figsize=(20, 12))
        gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.3, wspace=0.3)

        colors = self._get_theme_colors()
        fig.patch.set_facecolor(colors["background"])

        ax_cpu = fig.add_subplot(gs[0, 0:2])
        ax_mem = fig.add_subplot(gs[0, 2:4])
        ax_req = fig.add_subplot(gs[1, 0:2])
        ax_status = fig.add_subplot(gs[1, 2:4])
        ax_threat = fig.add_subplot(gs[2, 0:2])
        ax_perf = fig.add_subplot(gs[2, 2:4])

        for ax in [ax_cpu, ax_mem, ax_req, ax_status, ax_threat, ax_perf]:
            ax.set_facecolor(colors["background"])
            ax.tick_params(colors=colors["text"])
            ax.grid(True, alpha=0.2, color=colors["grid"])

        if 'cpu_percent' in metrics:
            ax_cpu.bar(['CPU'], [metrics['cpu_percent']], color=colors["accent"], alpha=0.8)
            ax_cpu.set_ylim(0, 100)
            ax_cpu.set_title('CPU 使用率', color=colors["text"])

        if 'memory_percent' in metrics:
            ax_mem.bar(['Memory'], [metrics['memory_percent']], color=colors["up_color"], alpha=0.8)
            ax_mem.set_ylim(0, 100)
            ax_mem.set_title('内存使用率', color=colors["text"])

        if 'requests' in metrics:
            ax_req.plot(metrics['requests'], color=colors["accent"], linewidth=2)
            ax_req.set_title('请求趋势', color=colors["text"])

        status_data = metrics.get('status_codes', {})
        if status_data:
            labels = [str(k) for k in status_data.keys()]
            values = list(status_data.values())
            ax_status.pie(values, labels=labels, autopct='%1.1f%%', colors=[colors["accent"]]*len(values))
            ax_status.set_title('HTTP 状态码分布', color=colors["text"])

        threat_data = metrics.get('threat_levels', {})
        if threat_data:
            labels = list(threat_data.keys())
            values = list(threat_data.values())
            ax_threat.bar(labels, values, color=[colors["up_color"], colors["accent"], colors["down_color"]][:len(values)])
            ax_threat.set_title('威胁等级分布', color=colors["text"])

        perf_data = metrics.get('response_times', [])
        if perf_data:
            ax_perf.plot(perf_data, color=colors["accent"], linewidth=2)
            ax_perf.set_title('响应时间 (ms)', color=colors["text"])

        return fig

    def create_market_dashboard(self, market_data: Dict[str, Any]) -> Any:
        fig = plt.figure(figsize=(20, 10))
        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)

        colors = self._get_theme_colors()
        fig.patch.set_facecolor(colors["background"])

        axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(3)]

        indices = market_data.get('indices', {})
        if indices:
            names = list(indices.keys())[:6]
            values = [indices[n].get('price', 0) for n in names]
            changes = [indices[n].get('change_pct', 0) for n in names]

            ax = axes[0]
            ax.set_facecolor(colors["background"])
            colors_bar = [colors["up_color"] if c >= 0 else colors["down_color"] for c in changes]
            ax.bar(names, values, color=colors_bar, alpha=0.8)
            ax.set_title('指数价格', color=colors["text"])
            ax.tick_params(colors=colors["text"])
            ax.grid(True, alpha=0.2, color=colors["grid"])

        sector_data = market_data.get('sectors', {})
        if sector_data:
            ax = axes[1]
            ax.set_facecolor(colors["background"])
            labels = list(sector_data.keys())[:8]
            values = list(sector_data.values())[:8]
            ax.pie(values, labels=labels, autopct='%1.1f%%', colors=plt.cm.Set3(np.linspace(0, 1, len(labels))))
            ax.set_title('行业分布', color=colors["text"])

        hot_stocks = market_data.get('hot_stocks', [])
        if hot_stocks:
            ax = axes[2]
            ax.set_facecolor(colors["background"])
            symbols = [s.get('symbol', '') for s in hot_stocks[:6]]
            changes = [s.get('change_pct', 0) for s in hot_stocks[:6]]
            colors_bar = [colors["up_color"] if c >= 0 else colors["down_color"] for c in changes]
            ax.barh(symbols, changes, color=colors_bar, alpha=0.8)
            ax.set_title('热门股票涨跌幅', color=colors["text"])
            ax.tick_params(colors=colors["text"])
            ax.grid(True, alpha=0.2, color=colors["grid"])

        turnover = market_data.get('turnover', {})
        if turnover:
            ax = axes[3]
            ax.set_facecolor(colors["background"])
            labels = ['上涨', '下跌', '平盘']
            values = [turnover.get('up', 0), turnover.get('down', 0), turnover.get('flat', 0)]
            colors_pie = [colors["up_color"], colors["down_color"], colors["accent"]]
            ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors_pie)
            ax.set_title('市场情绪', color=colors["text"])

        limit_data = market_data.get('limit', {})
        if limit_data:
            ax = axes[4]
            ax.set_facecolor(colors["background"])
            labels = ['涨停', '跌停']
            values = [limit_data.get('up', 0), limit_data.get('down', 0)]
            ax.bar(labels, values, color=[colors["up_color"], colors["down_color"]], alpha=0.8)
            ax.set_title('涨跌停统计', color=colors["text"])
            ax.tick_params(colors=colors["text"])
            ax.grid(True, alpha=0.2, color=colors["grid"])

        flow_data = market_data.get('money_flow', {})
        if flow_data:
            ax = axes[5]
            ax.set_facecolor(colors["background"])
            dates = list(flow_data.keys())[-10:]
            inflows = [flow_data[d].get('inflow', 0) for d in dates]
            outflows = [flow_data[d].get('outflow', 0) for d in dates]
            x = range(len(dates))
            ax.bar([i-0.2 for i in x], inflows, width=0.4, color=colors["up_color"], alpha=0.8, label='流入')
            ax.bar([i+0.2 for i in x], outflows, width=0.4, color=colors["down_color"], alpha=0.8, label='流出')
            ax.set_xticks(x)
            ax.set_xticklabels(dates, rotation=45)
            ax.set_title('资金流向', color=colors["text"])
            ax.legend(facecolor=colors["background"], labelcolor=colors["text"])

        return fig

    def create_portfolio_dashboard(self, portfolio_data: Dict[str, Any]) -> Any:
        fig = plt.figure(figsize=(18, 10))
        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)

        colors = self._get_theme_colors()
        fig.patch.set_facecolor(colors["background"])

        positions = portfolio_data.get('positions', [])
        if positions:
            ax = fig.add_subplot(gs[0, 0])
            ax.set_facecolor(colors["background"])
            symbols = [p.get('symbol', '') for p in positions[:6]]
            weights = [p.get('weight', 0) for p in positions[:6]]
            ax.pie(weights, labels=symbols, autopct='%1.1f%%', colors=plt.cm.Set3(np.linspace(0, 1, len(symbols))))
            ax.set_title('持仓权重', color=colors["text"])

            ax = fig.add_subplot(gs[0, 1])
            ax.set_facecolor(colors["background"])
            pnls = [p.get('unrealized_pnl', 0) for p in positions[:6]]
            colors_bar = [colors["up_color"] if p >= 0 else colors["down_color"] for p in pnls]
            ax.bar(symbols, pnls, color=colors_bar, alpha=0.8)
            ax.set_title('个股盈亏', color=colors["text"])
            ax.tick_params(colors=colors["text"])
            ax.grid(True, alpha=0.2, color=colors["grid"])

        total_value = portfolio_data.get('total_value', 0)
        cash = portfolio_data.get('cash', 0)
        invested = total_value - cash
        if total_value:
            ax = fig.add_subplot(gs[0, 2])
            ax.set_facecolor(colors["background"])
            ax.pie([invested, cash], labels=['已投资', '现金'], autopct='%1.1f%%',
                  colors=[colors["accent"], colors["up_color"]])
            ax.set_title('资产配置', color=colors["text"])

        history = portfolio_data.get('history', [])
        if history:
            ax = fig.add_subplot(gs[1, :2])
            ax.set_facecolor(colors["background"])
            dates = [h.get('date', '') for h in history]
            values = [h.get('value', 0) for h in history]
            ax.plot(dates, values, color=colors["accent"], linewidth=2)
            ax.fill_between(dates, values, alpha=0.3, color=colors["accent"])
            ax.set_title('账户历史', color=colors["text"])
            ax.tick_params(colors=colors["text"])
            ax.grid(True, alpha=0.2, color=colors["grid"])

        stats = portfolio_data.get('stats', {})
        if stats:
            ax = fig.add_subplot(gs[1, 2])
            ax.set_facecolor(colors["background"])
            ax.axis('off')
            stats_text = f"""
总收益率: {stats.get('total_return', 0):.2f}%
年化收益: {stats.get('annualized_return', 0):.2f}%
夏普比率: {stats.get('sharpe_ratio', 0):.2f}
最大回撤: {stats.get('max_drawdown', 0):.2f}%
            """
            ax.text(0.1, 0.5, stats_text, color=colors["text"], fontsize=12,
                   verticalalignment='center', fontfamily='monospace',
                   bbox=dict(boxstyle='round', facecolor=colors["background"], alpha=0.8))

        return fig

    def create_heatmap(self, data: pd.DataFrame, title: str = "相关性热力图") -> Any:
        fig, ax = plt.subplots(figsize=(10, 8))

        colors = self._get_theme_colors()
        fig.patch.set_facecolor(colors["background"])
        ax.set_facecolor(colors["background"])

        corr = data.corr()
        im = ax.imshow(corr, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)

        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45, ha='right')
        ax.set_yticklabels(corr.columns)

        for i in range(len(corr)):
            for j in range(len(corr)):
                text = ax.text(j, i, f'{corr.iloc[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=8)

        ax.set_title(title, color=colors["text"], pad=20)
        fig.colorbar(im, ax=ax)

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
