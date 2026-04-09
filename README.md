# 🌍 Stock Analysis and Market Prediction Bot

An advanced Python bot that combines **global news analysis, stock market intelligence, and automated trading insights**, delivered directly to Telegram.

---

## 🚀 Overview

This bot is designed to simulate a **mini hedge-fund level research system**, combining:

- News sentiment
- Market data
- Technical indicators
- Insider activity
- Institutional positioning

It continuously scans the market and produces **actionable reports** every cycle.

---

## 🔥 Features

### 📰 News Intelligence
- Aggregates news from:
  - CNBC
  - Bloomberg
  - Reuters
  - WSJ
  - Yahoo Finance
  - Bernama
  - The Edge
  - Free Malaysia Today
- Categorizes news into:
  - 🌎 World Affairs
  - 📈 Stock Market
  - 🇲🇾 Malaysia News

---

### 📊 Stock Market Analysis
- Extracts stock tickers from headlines
- Detects:
  - 🚀 Surges
  - 💥 Plunges
- Based on configurable % threshold

---

### 🧠 Technical Analysis Engine
Includes:
- RSI (Relative Strength Index)
- MACD
- Moving Averages (20 / 50 / 200)
- Bollinger Bands
- Support & Resistance Levels

---

### 🎯 Stock Scoring System (0–100)
Each stock is ranked using:

| Factor            | Weight |
|------------------|--------|
| Technicals       | 30%    |
| Insider Activity | 20%    |
| Investor Interest| 25%    |
| Momentum         | 15%    |
| Fundamentals     | 10%    |

Outputs:
- STRONG BUY
- BUY
- HOLD
- SELL

---

### 🕵️ Insider Tracking
- Tracks insider transactions using market data
- Generates BUY/SELL signals based on activity

---

### 💼 Investor Monitoring
Tracks holdings of major investors:
- Warren Buffett
- Ray Dalio
- Carl Icahn
- George Soros
- Bill Ackman

---

### 🏦 Institutional Analysis
- Tracks institutional ownership
- Analyzes major holders (Goldman, JPMorgan, etc.)

---

### ⚡ Market Anomaly Detection
- Detects stocks that move **against the market trend**
- Example:
  - S&P 500 ↓
  - Certain stocks ↑ → flagged as anomalies

---

### 📊 Statistical Entry System
Uses **Standard Deviation**:
- Mean price
- 1σ and 2σ entry levels
- Identifies:
  - VERY CHEAP
  - CHEAP
  - FAIR
  - EXPENSIVE

---

### 📈 Index Fund Tracker
Tracks:
- S&P 500 ETFs (VOO, SPY)
- Nasdaq (QQQ)
- Total Market
- International
- Bonds

Outputs:
- 🚀 Surged funds
- 💥 Plunged funds

---

### 📩 Telegram Integration
- Sends formatted reports automatically
- Handles long messages (splitting)
- Real-time alerts

---

## ⚙️ Installation

```bash
pip install requests beautifulsoup4 python-telegram-bot yfinance lxml feedparser pandas numpy ta
🔑 Setup
Create a Telegram Bot via BotFather
Get your:
BOT_TOKEN
CHAT_ID
Set environment variables:
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

OR edit directly in Config class.

▶️ Run the Bot
python bot.py
⏱️ Configuration

Inside Config:

SCAN_INTERVAL = 30  # minutes
PRICE_CHANGE_THRESHOLD = 5.0
LOOKBACK_DAYS = 1
📊 Example Output
🌍 World Affairs Update

📈 STOCK MOVEMENTS (>5%)

🚀 SURGES:
AAPL ↑ 6.2%
TSLA ↑ 8.5%

💥 PLUNGES:
META ↓ 5.7%

🎯 STOCK RECOMMENDATIONS
1. NVDA - STRONG BUY (82/100)
2. MSFT - BUY (74/100)

📊 STATISTICAL ENTRY POINTS
NVDA - CHEAP
Entry 1σ: $420
Entry 2σ: $390
🧠 Architecture

Modules:

NewsScraper
NewsCategorizer
StockAnalyzer
TechnicalAnalyzer
InsiderTracker
InvestorMonitor
InstitutionalTracker
StockScorer
MarketAnomalyDetector
IndexFundTracker
TelegramNotifier
⚠️ Disclaimer

This bot is for educational and informational purposes only.
It does NOT provide financial advice. Always do your own research before investing.

💡 Future Improvements
AI sentiment analysis (NLP)
Real-time websocket price feeds
Portfolio tracking
Backtesting system
Web dashboard (Flask / React)
🏆 Author

Built as a full-scale financial intelligence system combining:

Data engineering
Market analysis
Algorithmic thinking
