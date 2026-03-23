"""Base visualization classes."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import base64
from io import BytesIO


class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    CANDLESTICK = "candlestick"
    PIE = "pie"
    HEATMAP = "heatmap"
    SCATTER = "scatter"
    KLINE = "kline"
    AREA = "area"


class ChartTheme(str, Enum):
    DARK = "dark"
    LIGHT = "light"
    TRADITIONAL = "traditional"


@dataclass
class ChartConfig:
    width: int = 1200
    height: int = 600
    title: Optional[str] = None
    theme: ChartTheme = ChartTheme.DARK
    export_format: str = "png"
    dpi: int = 100


class BaseChart(ABC):
    def __init__(self, config: ChartConfig = None):
        self.config = config or ChartConfig()
        self._data = None
        self._figure = None

    @abstractmethod
    def generate(self, data: Any) -> Any:
        pass

    @abstractmethod
    def to_html(self) -> str:
        pass

    def to_base64(self, format: str = "png") -> str:
        if self._figure is None:
            raise ValueError("Chart not generated yet")

        buffer = BytesIO()
        self._figure.savefig(buffer, format=format, dpi=self.config.dpi, bbox_inches='tight')
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode()

    def to_bytesio(self, format: str = "png") -> BytesIO:
        if self._figure is None:
            raise ValueError("Chart not generated yet")

        buffer = BytesIO()
        self._figure.savefig(buffer, format=format, dpi=self.config.dpi, bbox_inches='tight')
        buffer.seek(0)
        return buffer

    def save(self, filepath: str):
        if self._figure is None:
            raise ValueError("Chart not generated yet")
        self._figure.savefig(filepath, dpi=self.config.dpi, bbox_inches='tight')

    def _get_theme_colors(self) -> Dict[str, str]:
        if self.config.theme == ChartTheme.DARK:
            return {
                "background": "#0a0e17",
                "text": "#ffffff",
                "grid": "#333333",
                "up_color": "#ef5350",
                "down_color": "#26a69a",
                "accent": "#667eea",
            }
        elif self.config.theme == ChartTheme.LIGHT:
            return {
                "background": "#ffffff",
                "text": "#000000",
                "grid": "#e0e0e0",
                "up_color": "#ef5350",
                "down_color": "#26a69a",
                "accent": "#667eea",
            }
        else:
            return {
                "background": "#ffffff",
                "text": "#000000",
                "grid": "#cccccc",
                "up_color": "#d32f2f",
                "down_color": "#388e3c",
                "accent": "#1976d2",
            }
