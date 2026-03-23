# API Protocol Documentation

## Overview

The Wealth API is a RESTful service built with FastAPI that provides comprehensive quantitative analysis capabilities for stocks and funds.

**Base URL**: `http://localhost:8000/api/v1`

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

**Note**: Future versions will implement JWT-based authentication.

## Common Headers

```
Content-Type: application/json
Accept: application/json
```

## Response Format

All responses follow this structure:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## Endpoints

### Health Check

**GET** `/health`

Check API health status.

**Response**:
```json
{
  "status": "healthy",
  "version": "0.3.0",
  "security": {
    "total_requests": 1234,
    "blocked_requests": 56,
    "rate_limit_hits": 12
  }
}
```

---

### Stock Quote (Real-time)

**POST** `/stocks/quote/realtime`

Get real-time stock quotes.

**Request Body**:
```json
{
  "symbol": "000001"
}
```

**Response**:
```json
{
  "symbol": "000001",
  "name": "平安银行",
  "price": 12.34,
  "change": 0.23,
  "change_pct": 1.90,
  "volume": 45678900,
  "amount": 567890123.45,
  "high": 12.50,
  "low": 12.10,
  "open": 12.15,
  "previous_close": 12.11
}
```

---

### K-Line Data

**POST** `/stocks/kline`

Get historical K-line data.

**Request Body**:
```json
{
  "symbol": "000001",
  "period": "day",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| symbol | string | Yes | Stock code |
| period | string | No | K-line type: day, week, month, 60min, 30min, 15min, 5min |
| start_date | string | No | Start date (YYYY-MM-DD) |
| end_date | string | No | End date (YYYY-MM-DD) |

**Response**:
```json
{
  "symbol": "000001",
  "name": "平安银行",
  "period": "day",
  "data": [
    {
      "timestamp": "2024-01-02",
      "open": 11.50,
      "high": 11.80,
      "low": 11.45,
      "close": 11.75,
      "volume": 12345678,
      "amount": 144567890.23,
      "change_pct": 2.17
    }
  ]
}
```

---

### Technical Indicators

**POST** `/indicators/calculate`

Calculate technical indicators.

**Request Body**:
```json
{
  "symbol": "000001",
  "period": "day",
  "indicators": ["rsi", "kdj", "macd", "bollinger"]
}
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| symbol | string | Yes | Stock code |
| period | string | No | K-line period (default: day) |
| indicators | array | No | Indicators to calculate (default: all) |

**Response**:
```json
{
  "symbol": "000001",
  "indicators": {
    "rsi": [
      {"timestamp": "2024-01-02", "value": 65.42}
    ],
    "kdj": [
      {"timestamp": "2024-01-02", "k": 72.35, "d": 68.21, "j": 80.64}
    ],
    "macd": [
      {"timestamp": "2024-01-02", "dif": 0.1234, "dea": 0.1123, "hist": 0.0111}
    ],
    "bollinger": [
      {"timestamp": "2024-01-02", "upper": 12.50, "middle": 12.00, "lower": 11.50}
    ]
  }
}
```

---

### Run Backtest

**POST** `/backtest/run`

Run strategy backtest.

**Request Body**:
```json
{
  "symbol": "000001",
  "strategy": "macd",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000
}
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| symbol | string | Yes | Stock code |
| strategy | string | Yes | Strategy name: macd, kdj, bollinger, mean_reversion |
| start_date | string | No | Start date |
| end_date | string | No | End date |
| initial_capital | number | No | Initial capital (default: 100000) |

**Response**:
```json
{
  "strategy_name": "macd",
  "symbol": "000001",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000.00,
  "final_capital": 125678.90,
  "total_return": 25.68,
  "annualized_return": 25.68,
  "sharpe_ratio": 1.85,
  "max_drawdown": 8.45,
  "win_rate": 58.33,
  "total_trades": 24,
  "trades": [
    {
      "trade_id": "TR001",
      "timestamp": "2024-01-15 10:30:00",
      "type": "buy",
      "price": 12.50,
      "quantity": 1000,
      "amount": 12500.00,
      "commission": 3.75
    }
  ]
}
```

---

### Strategy List

**POST** `/strategy/list`

Get available strategies.

**Request Body**: (optional)
```json
{
  "category": "technical"
}
```

**Response**:
```json
{
  "strategies": [
    {
      "name": "macd",
      "display_name": "MACD策略",
      "category": "technical",
      "description": "MACD金叉买入，死叉卖出",
      "parameters": [
        {"name": "fast_period", "default": 12, "description": "快线周期"},
        {"name": "slow_period", "default": 26, "description": "慢线周期"},
        {"name": "signal_period", "default": 9, "description": "信号线周期"}
      ]
    }
  ]
}
```

---

### Fund List

**GET** `/funds/list`

Get fund list with optional filtering.

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| page | number | No | Page number (default: 1) |
| page_size | number | No | Page size (default: 20) |
| risk_level | string | No | Risk level filter |

**Response**:
```json
{
  "total": 1000,
  "page": 1,
  "page_size": 20,
  "funds": [
    {
      "symbol": "000001",
      "name": "华夏成长混合",
      "net_value": 1.2345,
      "cumulative_value": 2.3456,
      "daily_return": 1.23,
      "subscription_status": "开放",
      "redemption_status": "开放",
      "risk_level": "中高"
    }
  ]
}
```

---

### AI Prediction

**POST** `/prediction/predict`

Get AI-based price prediction.

**Request Body**:
```json
{
  "symbol": "000001",
  "model": "lstm",
  "horizon": 30
}
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| symbol | string | Yes | Stock code |
| model | string | No | Model type: lstm, prophet, xgboost (default: lstm) |
| horizon | number | No | Prediction horizon in days (default: 30) |

**Response**:
```json
{
  "symbol": "000001",
  "model": "lstm",
  "prediction": [
    {"date": "2024-02-01", "predicted": 12.85, "lower": 12.50, "upper": 13.20}
  ],
  "accuracy": 87.5,
  "confidence": 0.85,
  "trend": "up"
}
```

---

### Security Stats

**GET** `/security/stats`

Get security monitoring statistics.

**Response**:
```json
{
  "total_requests": 12345,
  "blocked_requests": 234,
  "rate_limit_hits": 56,
  "suspicious_ips": 3,
  "top_blocked_ips": [
    {"ip": "192.168.1.100", "count": 45}
  ]
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_SYMBOL | 400 | Invalid stock/fund symbol |
| DATA_NOT_FOUND | 404 | Data not found |
| INVALID_PERIOD | 400 | Invalid period parameter |
| INVALID_STRATEGY | 400 | Invalid strategy name |
| SERVER_ERROR | 500 | Internal server error |
| RATE_LIMITED | 429 | Too many requests |

## Rate Limiting

| Endpoint | Limit |
|----------|-------|
| General | 100 requests/minute |
| /stocks/quote/realtime | 60 requests/minute |
| /prediction/predict | 10 requests/minute |

---

## WebSocket (Future)

Real-time data updates will be available via WebSocket.

**Endpoint**: `ws://localhost:8000/ws`

**Message Format**:
```json
{
  "type": "quote",
  "data": {
    "symbol": "000001",
    "price": 12.34,
    "change_pct": 1.90
  }
}
```
