"""API routes for Wealth platform."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import pandas as pd
import numpy as np
import io
import json
from loguru import logger

from wealth.api.schemas import (
    StockSearchRequest, StockSearchResponse,
    KlineRequest, KlineResponse,
    RealtimeQuoteResponse,
    StrategyBacktestRequest, BacktestResponse, TradeResponse, EquityCurvePoint,
    StrategyCompareRequest, StrategyCompareResponse,
    AlertCreateRequest, AlertResponse, AlertListResponse,
    PortfolioResponse, PortfolioPosition,
    MarketOverviewResponse,
    IndicatorsRequest, IndicatorsResponse,
    HealthResponse,
)
from wealth.data import AKShareSource, YFinanceSource, FundSource, EastMoneyCrawler
from wealth.engine import (
    TechnicalIndicators,
    get_strategy,
    BacktestEngine,
    Portfolio,
)
from wealth.alert import (
    Alert, AlertType, AlertLevel,
    NotifierManager, DesktopNotifier,
)

router = APIRouter()

ak_source = AKShareSource()
yf_source = YFinanceSource()
fund_source = FundSource()
em_crawler = EastMoneyCrawler()
notifier_manager = NotifierManager()
notifier_manager.add_notifier(DesktopNotifier())

portfolio = Portfolio(name="Default", initial_value=100000.0, cash=100000.0)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat(),
    )


@router.post("/stocks/search", response_model=list[StockSearchResponse])
async def search_stocks(request: StockSearchRequest):
    try:
        if request.market == "US":
            results = yf_source.search_stocks(request.keyword)
        else:
            results = ak_source.search_stocks(request.keyword)

        return [
            StockSearchResponse(
                symbol=r.symbol,
                name=r.name,
                market=r.market.value,
                sector=r.sector,
            )
            for r in results
        ]
    except Exception as e:
        logger.error(f"Search stocks failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stocks/quote/realtime", response_model=RealtimeQuoteResponse)
async def get_realtime_quote(symbol: str = Query(...)):
    try:
        market = symbol.market if hasattr(symbol, 'market') else None
        if symbol.endswith(".HK") or (len(symbol) <= 5 and symbol.isupper()):
            quote = yf_source.get_realtime_quote(symbol)
        else:
            quote = ak_source.get_realtime_quote(symbol)

        return RealtimeQuoteResponse(
            symbol=quote.symbol,
            name=quote.name,
            current_price=quote.current_price,
            change=quote.change,
            change_pct=quote.change_pct,
            open=quote.open,
            high=quote.high,
            low=quote.low,
            volume=quote.volume,
            amount=quote.amount,
            timestamp=quote.timestamp.isoformat(),
        )
    except Exception as e:
        logger.error(f"Get realtime quote failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stocks/kline", response_model=list[KlineResponse])
async def get_kline_data(request: KlineRequest):
    try:
        if request.symbol.endswith(".HK"):
            data = yf_source.get_kline_data(
                request.symbol, request.start_date, request.end_date, request.period, request.adjust
            )
        elif request.symbol.endswith(".O") or request.symbol.endswith(".AX"):
            data = yf_source.get_kline_data(
                request.symbol, request.start_date, request.end_date, request.period, request.adjust
            )
        elif request.symbol.startswith("5") or request.symbol.startswith("15"):
            data = fund_source.get_kline_data(
                request.symbol, request.start_date, request.end_date, request.period
            )
        else:
            data = ak_source.get_kline_data(
                request.symbol, request.start_date, request.end_date, request.period, request.adjust
            )

        return [
            KlineResponse(
                timestamp=k.timestamp.isoformat(),
                open=k.open,
                high=k.high,
                low=k.low,
                close=k.close,
                volume=k.volume,
                amount=k.amount,
            )
            for k in data
        ]
    except Exception as e:
        logger.error(f"Get kline data failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/indicators/calculate", response_model=IndicatorsResponse)
async def calculate_indicators(request: IndicatorsRequest):
    try:
        kline_data = await get_kline_data(KlineRequest(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
        ))

        df = pd.DataFrame([
            {
                "timestamp": k.timestamp,
                "open": k.open,
                "high": k.high,
                "low": k.low,
                "close": k.close,
                "volume": k.volume,
            }
            for k in kline_data
        ])
        df.set_index("timestamp", inplace=True)

        if request.indicators:
            result = df.to_dict("records")
        else:
            indicators = TechnicalIndicators.calculate_all(df)
            result = indicators.to_dict("records")

        return IndicatorsResponse(symbol=request.symbol, data=result)
    except Exception as e:
        logger.error(f"Calculate indicators failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: StrategyBacktestRequest):
    try:
        kline_data = await get_kline_data(KlineRequest(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
        ))

        df = pd.DataFrame([
            {
                "timestamp": k.timestamp,
                "open": k.open,
                "high": k.high,
                "low": k.low,
                "close": k.close,
                "volume": k.volume,
            }
            for k in kline_data
        ])
        df.set_index("timestamp", inplace=True)

        strategy = get_strategy(request.strategy)
        engine = BacktestEngine(
            initial_capital=request.initial_capital,
            commission_rate=request.commission_rate,
        )

        result = engine.run(
            strategy=strategy,
            data=df,
            symbol=request.symbol,
            stop_loss_pct=request.stop_loss_pct,
            take_profit_pct=request.take_profit_pct,
        )

        return BacktestResponse(
            strategy_name=result.strategy_name,
            symbol=result.symbol,
            start_date=result.start_date.isoformat(),
            end_date=result.end_date.isoformat(),
            initial_capital=result.initial_capital,
            final_value=result.final_value,
            total_return=result.portfolio_stats.total_return,
            annualized_return=result.portfolio_stats.annualized_return,
            volatility=result.portfolio_stats.volatility,
            sharpe_ratio=result.portfolio_stats.sharpe_ratio,
            max_drawdown=result.portfolio_stats.max_drawdown,
            max_drawdown_duration=result.portfolio_stats.max_drawdown_duration,
            win_rate=result.portfolio_stats.win_rate,
            profit_loss_ratio=result.portfolio_stats.profit_loss_ratio,
            total_trades=result.portfolio_stats.total_trades,
            winning_trades=result.portfolio_stats.winning_trades,
            losing_trades=result.portfolio_stats.losing_trades,
            avg_holding_days=result.portfolio_stats.avg_holding_days,
        )
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest/trades")
async def get_backtest_trades(request: StrategyBacktestRequest):
    try:
        kline_data = await get_kline_data(KlineRequest(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
        ))

        df = pd.DataFrame([
            {
                "timestamp": k.timestamp,
                "open": k.open,
                "high": k.high,
                "low": k.low,
                "close": k.close,
                "volume": k.volume,
            }
            for k in kline_data
        ])
        df.set_index("timestamp", inplace=True)

        strategy = get_strategy(request.strategy)
        engine = BacktestEngine(initial_capital=request.initial_capital)

        result = engine.run(strategy=strategy, data=df, symbol=request.symbol)

        return [
            TradeResponse(
                trade_id=t.trade_id,
                symbol=t.symbol,
                entry_date=t.entry_date.isoformat(),
                exit_date=t.exit_date.isoformat() if t.exit_date else None,
                entry_price=t.entry_price,
                exit_price=t.exit_price,
                quantity=t.quantity,
                pnl=t.pnl,
                pnl_pct=t.pnl_pct,
                holding_days=t.holding_days,
                strategy=t.strategy,
            )
            for t in result.trades
        ]
    except Exception as e:
        logger.error(f"Get backtest trades failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest/equity-curve")
async def get_equity_curve(request: StrategyBacktestRequest):
    try:
        kline_data = await get_kline_data(KlineRequest(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
        ))

        df = pd.DataFrame([
            {
                "timestamp": k.timestamp,
                "open": k.open,
                "high": k.high,
                "low": k.low,
                "close": k.close,
                "volume": k.volume,
            }
            for k in kline_data
        ])
        df.set_index("timestamp", inplace=True)

        strategy = get_strategy(request.strategy)
        engine = BacktestEngine(initial_capital=request.initial_capital)

        result = engine.run(strategy=strategy, data=df, symbol=request.symbol)

        return [
            EquityCurvePoint(
                date=idx.isoformat(),
                value=row["value"],
                cash=row["cash"],
                position_value=row["position_value"],
            )
            for idx, row in result.equity_curve.iterrows()
        ]
    except Exception as e:
        logger.error(f"Get equity curve failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest/compare", response_model=StrategyCompareResponse)
async def compare_strategies(request: StrategyCompareRequest):
    try:
        kline_data = await get_kline_data(KlineRequest(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
        ))

        df = pd.DataFrame([
            {
                "timestamp": k.timestamp,
                "open": k.open,
                "high": k.high,
                "low": k.low,
                "close": k.close,
                "volume": k.volume,
            }
            for k in kline_data
        ])
        df.set_index("timestamp", inplace=True)

        strategies = [get_strategy(s) for s in request.strategies]
        engine = BacktestEngine(initial_capital=request.initial_capital)

        results = engine.compare_strategies(strategies, df, request.symbol)

        response_results = {}
        for name, result in results.items():
            if result:
                response_results[name] = BacktestResponse(
                    strategy_name=result.strategy_name,
                    symbol=result.symbol,
                    start_date=result.start_date.isoformat(),
                    end_date=result.end_date.isoformat(),
                    initial_capital=result.initial_capital,
                    final_value=result.final_value,
                    total_return=result.portfolio_stats.total_return,
                    annualized_return=result.portfolio_stats.annualized_return,
                    volatility=result.portfolio_stats.volatility,
                    sharpe_ratio=result.portfolio_stats.sharpe_ratio,
                    max_drawdown=result.portfolio_stats.max_drawdown,
                    max_drawdown_duration=result.portfolio_stats.max_drawdown_duration,
                    win_rate=result.portfolio_stats.win_rate,
                    profit_loss_ratio=result.portfolio_stats.profit_loss_ratio,
                    total_trades=result.portfolio_stats.total_trades,
                    winning_trades=result.portfolio_stats.winning_trades,
                    losing_trades=result.portfolio_stats.losing_trades,
                    avg_holding_days=result.portfolio_stats.avg_holding_days,
                )

        return StrategyCompareResponse(results=response_results)
    except Exception as e:
        logger.error(f"Compare strategies failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts", response_model=AlertResponse)
async def create_alert(request: AlertCreateRequest):
    try:
        alert = Alert(
            alert_id=f"alert_{datetime.now().timestamp()}",
            symbol=request.symbol,
            alert_type=AlertType(request.alert_type),
            level=AlertLevel(request.level),
            condition=request.condition,
            current_value=0,
            message=f"{request.symbol} {request.condition}",
            metadata={"threshold_value": request.threshold_value},
        )

        result = await notifier_manager.send_alert(alert)

        return AlertResponse(
            alert_id=alert.alert_id,
            symbol=alert.symbol,
            alert_type=alert.alert_type.value,
            level=alert.level.value,
            condition=alert.condition,
            current_value=alert.current_value,
            message=alert.message,
            created_at=alert.created_at.isoformat(),
            triggered_at=alert.triggered_at.isoformat() if alert.triggered_at else None,
            is_active=alert.is_active,
        )
    except Exception as e:
        logger.error(f"Create alert failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts():
    try:
        alerts = notifier_manager.get_alert_history(limit=100)

        return AlertListResponse(
            alerts=[
                AlertResponse(
                    alert_id=a.alert_id,
                    symbol=a.symbol,
                    alert_type=a.alert_type.value,
                    level=a.level.value,
                    condition=a.condition,
                    current_value=a.current_value,
                    message=a.message,
                    created_at=a.created_at.isoformat(),
                    triggered_at=a.triggered_at.isoformat() if a.triggered_at else None,
                    is_active=a.is_active,
                )
                for a in alerts
            ]
        )
    except Exception as e:
        logger.error(f"List alerts failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio():
    try:
        symbols = [p.symbol for p in portfolio.positions]
        if symbols:
            quotes = em_crawler.get_realtime_quotes(symbols)
            prices = {q.symbol: q.current_price for q in quotes}
            portfolio.update_market_value(prices)

        return PortfolioResponse(
            name=portfolio.name,
            initial_value=portfolio.initial_value,
            total_value=portfolio.total_value,
            cash=portfolio.cash,
            total_pnl=portfolio.total_pnl,
            total_pnl_pct=portfolio.total_pnl_pct,
            position_count=len(portfolio.positions),
            positions=[
                PortfolioPosition(
                    symbol=p.symbol,
                    name=p.name,
                    quantity=p.quantity,
                    avg_cost=p.avg_cost,
                    current_price=p.current_price,
                    market_value=p.market_value,
                    unrealized_pnl=p.unrealized_pnl,
                    unrealized_pnl_pct=p.unrealized_pnl_pct,
                    weight=p.weight,
                )
                for p in portfolio.positions
            ],
        )
    except Exception as e:
        logger.error(f"Get portfolio failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/overview", response_model=MarketOverviewResponse)
async def get_market_overview():
    try:
        indices = yf_source.get_market_overview()
        limit_up = em_crawler.get_limit_up_stocks()

        return MarketOverviewResponse(
            indices={k: v for k, v in indices.items()},
            hot_stocks=[],
            limit_up_count=len(limit_up),
            limit_down_count=0,
        )
    except Exception as e:
        logger.error(f"Get market overview failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/funds/{symbol}")
async def get_fund_info(symbol: str):
    try:
        info = fund_source.get_fund_info(symbol)
        return {
            "symbol": info.symbol,
            "name": info.name,
            "fund_type": info.fund_type,
            "nav": info.nav,
            "nav_date": info.nav_date.isoformat() if info.nav_date else None,
            "manager": info.manager,
            "company": info.company,
            "min_purchase": info.min_purchase,
        }
    except Exception as e:
        logger.error(f"Get fund info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def list_strategies():
    return {
        "strategies": [
            {"name": "macd", "description": "MACD crossover strategy"},
            {"name": "kdj", "description": "KDJ indicator strategy"},
            {"name": "bollinger", "description": "Bollinger Bands strategy"},
            {"name": "mean_reversion", "description": "Mean reversion strategy"},
            {"name": "rsi", "description": "RSI indicator strategy"},
            {"name": "trend_following", "description": "Trend following with EMA"},
            {"name": "supertrend", "description": "SuperTrend strategy"},
        ]
    }


@router.post("/prediction")
async def predict_price(request: dict):
    try:
        symbol = request.get("symbol")
        model_type = request.get("model", "ensemble")
        days = request.get("days", 30)

        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol is required")

        kline_data = await get_kline_data(KlineRequest(
            symbol=symbol,
            start_date="2020-01-01",
            end_date=datetime.now().strftime("%Y-%m-%d"),
        ))

        df = pd.DataFrame([
            {
                "timestamp": k.timestamp,
                "open": k.open,
                "high": k.high,
                "low": k.low,
                "close": k.close,
                "volume": k.volume,
            }
            for k in kline_data
        ])
        df.set_index("timestamp", inplace=True)

        from wealth.ml.predictor import PricePredictor
        predictor = PricePredictor()
        result = predictor.predict(df, model=model_type, days=days)

        historical_dates = df.index.tolist()[-50:]
        predicted_dates = [f"D_{i+1}" for i in range(len(result.predicted))]

        chart_data = {
            "dates": [str(d) for d in historical_dates] + predicted_dates,
            "historical": df['close'].tolist()[-50:],
            "predicted": result.predicted.tolist(),
            "upper": result.confidence_upper.tolist(),
            "lower": result.confidence_lower.tolist(),
        }

        return {
            "symbol": symbol,
            "model": model_type,
            "predicted": result.predicted.tolist(),
            "confidence_lower": result.confidence_lower.tolist(),
            "confidence_upper": result.confidence_upper.tolist(),
            "metrics": result.metrics,
            "chartData": chart_data,
            "currentPrice": df['close'].iloc[-1],
            "predictedPrice": result.predicted[-1] if len(result.predicted) > 0 else df['close'].iloc[-1],
            "change": ((result.predicted[-1] - df['close'].iloc[-1]) / df['close'].iloc[-1] * 100) if len(result.predicted) > 0 else 0,
            "feature_importance": result.feature_importance.to_dict("records") if result.feature_importance is not None else None,
        }
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
