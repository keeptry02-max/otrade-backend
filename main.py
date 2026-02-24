from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

MODAL = 7217598
RISK_PERCENT = 0.02
RISK_PER_TRADE = MODAL * RISK_PERCENT

sector_data = {
    "banking": ["BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK"],
    "mining": ["ADRO.JK","ANTM.JK","INCO.JK","PTBA.JK"],
    "consumer": ["ICBP.JK","UNVR.JK","MYOR.JK"]
}

@app.get("/")
def home():
    return {"app": "O'trade Backend Running"}

@app.get("/scan")
def scan_sector(sector: str):
    if sector not in sector_data:
        return {"error": "Sector not found"}

    results = []

    for sym in sector_data[sector]:
        df = yf.download(sym, period="6mo", interval="1d", auto_adjust=True)
        if df.empty:
            continue

        df["EMA20"] = df["Close"].ewm(span=20).mean()
        df["EMA50"] = df["Close"].ewm(span=50).mean()
        df.dropna(inplace=True)

        latest = df.iloc[-1]

        entry = float(latest["Close"])
        stop = entry * 0.97
        risk = entry - stop
        tp = entry + 2 * risk
        lot = int(RISK_PER_TRADE / risk / 100) if risk > 0 else 0

        results.append({
            "symbol": sym,
            "entry": round(entry,2),
            "stop_loss": round(stop,2),
            "take_profit": round(tp,2),
            "lot": lot
        })

    return {"sector": sector, "data": results}
