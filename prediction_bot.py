"""
Stock Analysis Bot (Groq Edition - Free)
==========================================
Analyzes a stock ticker and sends a full financial report to Telegram.

Requirements:
    Run in VS Code terminal:
    python -m pip install yfinance groq requests

Run:
    python prediction_bot.py
"""

import re
import requests
import yfinance as yf
from groq import Groq

# ─────────────────────────────────────────────
#   YOUR KEYS
# ─────────────────────────────────────────────
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID")
# ─────────────────────────────────────────────


# ── Telegram ──────────────────────────────────────────────────────────────────

def send_telegram(message: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
    for chunk in chunks:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "HTML",
        }
        resp = requests.post(url, json=payload)
        if not resp.ok:
            print(f"Telegram error: {resp.text}")
            return False
    return True


# ── Helpers ───────────────────────────────────────────────────────────────────

def safe(val, fmt=".2f", fallback="N/A"):
    try:
        if val is None or (isinstance(val, float) and val != val):
            return fallback
        return f"{val:{fmt}}"
    except Exception:
        return fallback


def billions(val, fallback="N/A"):
    try:
        if val is None:
            return fallback
        return f"${val / 1e9:.2f}B"
    except Exception:
        return fallback


def pct(val, fallback="N/A"):
    try:
        if val is None:
            return fallback
        return f"{val * 100:.1f}%"
    except Exception:
        return fallback


def check(val, threshold, higher_is_better=True):
    try:
        if val is None:
            return "❓"
        return "✅" if (val > threshold) == higher_is_better else "❌"
    except Exception:
        return "❓"


# ── Data Fetching ─────────────────────────────────────────────────────────────

def fetch_financials(ticker: str) -> dict:
    tk = yf.Ticker(ticker)
    info = tk.info

    # Income Statement
    try:
        income = tk.financials
        revenue_list = income.loc["Total Revenue"].dropna().tolist() if "Total Revenue" in income.index else []
        net_income_list = income.loc["Net Income"].dropna().tolist() if "Net Income" in income.index else []
        revenue_current = revenue_list[0] if revenue_list else None
        revenue_prev = revenue_list[1] if len(revenue_list) > 1 else None
        net_income = net_income_list[0] if net_income_list else None
        revenue_growth = ((revenue_current - revenue_prev) / abs(revenue_prev)) if (revenue_current and revenue_prev) else None
        net_margin = (net_income / revenue_current) if (net_income and revenue_current) else None
    except Exception as e:
        print(f"Income statement error: {e}")
        revenue_current = revenue_prev = net_income = revenue_growth = net_margin = None

    # Balance Sheet
    try:
        bs = tk.balance_sheet
        cash = None
        for label in ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]:
            if label in bs.index:
                cash = bs.loc[label].iloc[0]
                break
        total_debt = bs.loc["Total Debt"].iloc[0] if "Total Debt" in bs.index else None
        equity = None
        for label in ["Stockholders Equity", "Total Equity Gross Minority Interest"]:
            if label in bs.index:
                equity = bs.loc[label].iloc[0]
                break
    except Exception as e:
        print(f"Balance sheet error: {e}")
        cash = total_debt = equity = None

    # Cash Flow
    try:
        cf = tk.cashflow
        op_cf = cf.loc["Operating Cash Flow"].iloc[0] if "Operating Cash Flow" in cf.index else None
        capex = cf.loc["Capital Expenditure"].iloc[0] if "Capital Expenditure" in cf.index else None
        free_cf = (op_cf + capex) if (op_cf is not None and capex is not None) else None
    except Exception as e:
        print(f"Cash flow error: {e}")
        op_cf = capex = free_cf = None

    # Ratios
    roe = (net_income / equity) if (net_income and equity and equity != 0) else None
    shares = info.get("sharesOutstanding")
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    eps = info.get("trailingEps")
    pe_ratio = info.get("trailingPE") or ((price / eps) if (price and eps and eps > 0) else None)
    fcf_per_share = (free_cf / shares) if (free_cf and shares) else None
    p_fcf = (price / fcf_per_share) if (price and fcf_per_share and fcf_per_share > 0) else None

    return {
        "ticker": ticker.upper(),
        "name": info.get("longName", ticker.upper()),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "price": price,
        "market_cap": info.get("marketCap"),
        "revenue_current": revenue_current,
        "revenue_prev": revenue_prev,
        "revenue_growth": revenue_growth,
        "net_income": net_income,
        "net_margin": net_margin,
        "cash": cash,
        "total_debt": total_debt,
        "equity": equity,
        "operating_cf": op_cf,
        "capex": capex,
        "free_cf": free_cf,
        "roe": roe,
        "pe_ratio": pe_ratio,
        "p_fcf": p_fcf,
        "eps": eps,
        "beta": info.get("beta"),
        "dividend_yield": info.get("dividendYield"),
    }


# ── AI Analysis ───────────────────────────────────────────────────────────────

def ai_verdict(data: dict) -> str:
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are a professional equity analyst. Analyze the following financial data for {data['ticker']} ({data['name']}) and give a concise investment verdict.

FINANCIAL DATA:
- Sector: {data['sector']} | Industry: {data['industry']}
- Price: ${safe(data['price'])} | Market Cap: {billions(data['market_cap'])}
- Revenue (current year): {billions(data['revenue_current'])}
- Revenue (prior year): {billions(data['revenue_prev'])}
- Revenue Growth: {pct(data['revenue_growth'])}
- Net Income: {billions(data['net_income'])}
- Net Margin: {pct(data['net_margin'])} (threshold: >10% = good)
- Cash: {billions(data['cash'])}
- Total Debt: {billions(data['total_debt'])}
- Shareholders Equity: {billions(data['equity'])}
- Operating Cash Flow: {billions(data['operating_cf'])}
- Free Cash Flow: {billions(data['free_cf'])}
- ROE: {pct(data['roe'])} (threshold: >15% = good)
- P/E Ratio: {safe(data['pe_ratio'], '.1f')} (S&P avg ~22)
- P/FCF Ratio: {safe(data['p_fcf'], '.1f')}
- Beta: {safe(data['beta'])}
- Dividend Yield: {pct(data['dividend_yield'])}

RULES:
- Evaluate each metric against its threshold
- Identify concentration risk, competition risk, disruption risk briefly
- Give a final verdict: STRONG BUY / BUY / HOLD / AVOID / STRONG AVOID
- Keep your full response under 350 words
- Use plain text only, no markdown

Structure your response EXACTLY like this:
STRENGTHS:
- point 1
- point 2

WEAKNESSES:
- point 1
- point 2

KEY RISKS:
- Concentration: ...
- Competition: ...
- Disruption: ...

VERDICT: [STRONG BUY / BUY / HOLD / AVOID / STRONG AVOID] — one sentence explanation
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ── Report Builder ────────────────────────────────────────────────────────────

def build_report(data: dict, verdict: str) -> str:
    d = data

    def row(label, value):
        return f"  <b>{label}:</b> {value}\n"

    debt_gt_cash = (d['total_debt'] or 0) > (d['cash'] or 0)

    r = ""
    r += f"📊 <b>STOCK ANALYSIS — {d['ticker']}</b>\n"
    r += f"<i>{d['name']} | {d['sector']}</i>\n"
    r += f"💰 Price: <b>${safe(d['price'])}</b>  |  Mkt Cap: <b>{billions(d['market_cap'])}</b>\n"
    r += "━" * 28 + "\n\n"

    r += "📈 <b>1. INCOME STATEMENT</b>\n"
    r += row("Revenue (Current Yr)", billions(d['revenue_current']))
    r += row("Revenue (Prior Yr)", billions(d['revenue_prev']))
    r += row("Revenue Growth", f"{pct(d['revenue_growth'])}  {check(d['revenue_growth'], 0)}")
    r += row("Net Income", billions(d['net_income']))
    r += row("Net Margin", f"{pct(d['net_margin'])}  {check(d['net_margin'], 0.10)}  <i>(good if &gt;10%)</i>")
    r += "\n"

    r += "🏦 <b>2. BALANCE SHEET</b>\n"
    r += row("Cash", billions(d['cash']))
    r += row("Total Debt", billions(d['total_debt']))
    r += row("Shareholders Equity", billions(d['equity']))
    r += row("Debt &gt; Cash?", "⚠️ Yes — leveraged" if debt_gt_cash else "✅ No — healthy")
    r += "\n"

    r += "💵 <b>3. CASH FLOW STATEMENT</b>\n"
    r += row("Operating Cash Flow", billions(d['operating_cf']))
    r += row("CapEx", billions(d['capex']))
    r += row("Free Cash Flow", f"{billions(d['free_cf'])}  {check(d['free_cf'], 0)}")
    r += "\n"

    r += "📐 <b>4. KEY RATIOS</b>\n"
    r += row("ROE", f"{pct(d['roe'])}  {check(d['roe'], 0.15)}  <i>(good if &gt;15%)</i>")
    r += row("Net Margin", f"{pct(d['net_margin'])}  {check(d['net_margin'], 0.10)}  <i>(good if &gt;10%)</i>")
    r += row("P/E Ratio", f"{safe(d['pe_ratio'], '.1f')}  <i>(S&amp;P avg ~22)</i>")
    r += row("P/FCF Ratio", safe(d['p_fcf'], '.1f'))
    r += row("Beta", safe(d['beta']))
    r += row("Dividend Yield", pct(d['dividend_yield']))
    r += "\n"

    r += "🤖 <b>5. AI VERDICT (Groq / LLaMA3)</b>\n"
    r += "━" * 28 + "\n"
    r += f"<pre>{verdict}</pre>\n"
    r += "\n⚠️ <i>Not financial advice. Do your own due diligence.</i>"

    return r


# ── Main ──────────────────────────────────────────────────────────────────────

def analyze(ticker: str):
    print(f"\n🔍 Fetching data for {ticker.upper()}...")
    data = fetch_financials(ticker)
    print("✅ Financial data fetched.")

    print("🤖 Running AI analysis via Groq...")
    verdict = ai_verdict(data)
    print("✅ AI analysis complete.")

    report = build_report(data, verdict)

    print("📤 Sending to Telegram...")
    success = send_telegram(report)
    if success:
        print("✅ Report sent to Telegram successfully!")
    else:
        print("❌ Failed to send. Check your Telegram bot token and chat ID.")

    print("\n" + "─" * 50)
    print("CONSOLE PREVIEW:")
    print("─" * 50)
    clean = re.sub(r'<[^>]+>', '', report)
    print(clean)

    return report


if __name__ == "__main__":
    print("=" * 50)
    print("  📊 Stock Analysis Bot  |  Powered by Groq")
    print("=" * 50)
    ticker = input("Enter stock ticker (e.g. AAPL, NKE, TSLA): ").strip().upper()
    if not ticker:
        print("No ticker entered. Exiting.")
    else:
        analyze(ticker)