#!/usr/bin/env python3
"""Environment setup and validation script for Wealth platform."""

import sys
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "-q"])
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress

console = Console()

class EnvironmentChecker:
    MIN_PYTHON_VERSION = (3, 10)
    REQUIRED_PACKAGES = {
        "core": [
            "pandas>=2.1.0",
            "numpy>=1.26.0",
            "fastapi>=0.109.0",
            "uvicorn[standard]>=0.27.0",
        ],
        "data": [
            "akshare>=1.13.0",
            "yfinance>=0.2.35",
            "httpx>=0.26.0",
        ],
        "engine": [
            "ta>=0.10.2",
            "scikit-learn>=1.4.0",
        ],
        "visualization": [
            "pyecharts>=2.0.4",
            "matplotlib>=3.8.0",
            "seaborn>=0.13.0",
            "plotly>=5.18.0",
        ],
        "alert": [
            "apscheduler>=3.10.4",
            "notify-py>=0.3.42",
            "plyer>=2.1.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "ruff>=0.1.0",
        ],
    }

    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.project_root = Path(__file__).parent.parent

    def check_python_version(self) -> bool:
        version = sys.version_info[:2]
        status = version >= self.MIN_PYTHON_VERSION
        self.results["python"] = {
            "status": status,
            "current": f"{version[0]}.{version[1]}.{sys.version_info.minor}",
            "required": f"{self.MIN_PYTHON_VERSION[0]}.{self.MIN_PYTHON_VERSION[1]}",
            "message": "OK" if status else f"需要 Python {self.MIN_PYTHON_VERSION[0]}.{self.MIN_PYTHON_VERSION[1]}+"
        }
        return status

    def check_package(self, package: str) -> bool:
        try:
            __import__(package.split(">=")[0].split("==")[0].replace("-", "_"))
            return True
        except ImportError:
            return False

    def check_packages(self) -> Dict[str, bool]:
        results = {}
        for category, packages in self.REQUIRED_PACKAGES.items():
            category_results = {}
            with Progress() as progress:
                task = progress.add_task(f"检查 {category}...", total=len(packages))
                for pkg in packages:
                    name = pkg.split(">=")[0].split("==")[0]
                    status = self.check_package(name)
                    category_results[pkg] = status
                    progress.advance(task)
            results[category] = category_results
        self.results["packages"] = results
        return results

    def check_system_dependencies(self) -> Dict[str, bool]:
        deps = {}
        deps["git"] = self._check_command("git --version")
        deps["node"] = self._check_command("node --version")
        deps["npm"] = self._check_command("npm --version")
        deps["playwright"] = self._check_command("playwright --version") if os.name == "nt" else True
        self.results["system"] = deps
        return deps

    def _check_command(self, cmd: str) -> bool:
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def generate_report(self) -> Table:
        table = Table(title="Wealth 环境检测报告")
        table.add_column("检查项", style="cyan")
        table.add_column("状态", style="magenta")
        table.add_column("详情", style="dim")

        for category, data in self.results.items():
            if category == "packages":
                for cat, pkgs in data.items():
                    for pkg, status in pkgs.items():
                        table.add_row(
                            f"{cat}.{pkg}",
                            "[green]✓[/green]" if status else "[red]✗[/red]",
                            "已安装" if status else "未安装"
                        )
            else:
                for name, status in data.items():
                    if isinstance(status, bool):
                        table.add_row(
                            name,
                            "[green]✓[/green]" if status else "[red]✗[/red]",
                            "可用" if status else "不可用"
                        )
        return table


class EnvironmentInstaller:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.console = Console()

    def install_python_packages(self, categories: Optional[List[str]] = None) -> bool:
        all_packages = []
        packages = EnvironmentChecker.REQUIRED_PACKAGES

        if categories:
            for cat in categories:
                if cat in packages:
                    all_packages.extend(packages[cat])
        else:
            for pkgs in packages.values():
                all_packages.extend(pkgs)

        self.console.print(f"\n[bold]安装 Python 包...[/bold]")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--upgrade", "pip"
            ])
            for pkg in all_packages:
                self.console.print(f"  安装 {pkg}...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", pkg, "-q"
                ])
            return True
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]安装失败: {e}[/red]")
            return False

    def setup_nodejs(self) -> bool:
        frontend_dir = self.project_root / "wealth" / "frontend"
        if not frontend_dir.exists():
            self.console.print("[yellow]前端目录不存在，跳过 Node.js 安装[/yellow]")
            return False

        self.console.print(f"\n[bold]安装前端依赖...[/bold]")
        try:
            subprocess.check_call(["npm", "install"], cwd=frontend_dir)
            return True
        except subprocess.CalledProcessError:
            self.console.print("[red]npm install 失败[/red]")
            return False

    def install_playwright(self) -> bool:
        self.console.print("\n[bold]安装 Playwright...[/bold]")
        try:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "--with-deps"])
            return True
        except subprocess.CalledProcessError:
            self.console.print("[yellow]Playwright 安装失败，浏览器自动化功能可能不可用[/yellow]")
            return False

    def create_virtual_env(self) -> bool:
        venv_dir = self.project_root / "venv"
        if venv_dir.exists():
            self.console.print("[yellow]虚拟环境已存在[/yellow]")
            return True

        self.console.print(f"\n[bold]创建虚拟环境...[/bold]")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
            self.console.print(f"[green]虚拟环境创建成功: {venv_dir}[/green]")
            return True
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]创建虚拟环境失败: {e}[/red]")
            return False


def main():
    console = Console()
    console.print("\n[bold cyan]Wealth 量化分析平台 - 环境配置工具[/bold cyan]\n")

    checker = EnvironmentChecker()

    console.print("[bold]1. 检查 Python 版本...[/bold]")
    checker.check_python_version()

    console.print("[bold]2. 检查系统依赖...[/bold]")
    checker.check_system_dependencies()

    console.print("[bold]3. 检查 Python 包...[/bold]")
    checker.check_packages()

    console.print("\n[bold]检测结果:[/bold]")
    console.print(checker.generate_report())

    if console.input("\n是否自动安装缺失的依赖? [y/N]: ").lower() == "y":
        installer = EnvironmentInstaller(Path(__file__).parent.parent)

        categories = console.input(
            "选择安装类别 (all/core/data/engine/visualization/alert/dev): "
        ).strip().split("/")

        if "all" in categories:
            categories = None

        if installer.install_python_packages(categories):
            console.print("\n[green]Python 包安装完成![/green]")
        else:
            console.print("\n[red]部分包安装失败[/red]")

        if sys.platform == "win32":
            installer.install_playwright()

        console.print("\n[bold]请重新运行检测以确认安装结果[/bold]")


if __name__ == "__main__":
    main()
