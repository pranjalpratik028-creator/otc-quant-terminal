import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy
from sklearn.ensemble import RandomForestClassifier
from collections import deque

st.set_page_config(page_title="ULTIMATE QUANT TERMINAL", layout="wide")

st.title("🧠 ULTIMATE QUANT TERMINAL (HEDGE-FUND STYLE)")

# -----------------------------
# MEMORY BUFFER
# -----------------------------
buffer_size = 1000
price_buffer = deque(maxlen=buffer_size)

# -----------------------------
# LIVE FEED GENERATOR
# -----------------------------
def generate_tick(last_price):
    regime = np.random.choice(["normal", "manipulated", "volatile"])

    if regime == "normal":
        return last_price + np.random.normal(0, 0.2)
    elif regime == "manipulated":
        return last_price + np.random.choice([-0.3, 0.3])
    else:
        return last_price + np.random.normal(0, 0.5)

if "price" not in st.session_state:
    st.session_state.price = 100

if st.button("▶️ Start Feed"):
    for _ in range(300):
        new_price = generate_tick(st.session_state.price)
        st.session_state.price = new_price
        price_buffer.append(new_price)

# -----------------------------
# BUILD DATA
# -----------------------------
if len(price_buffer) > 50:
    df = pd.DataFrame({"price": list(price_buffer)})

    df["returns"] = df["price"].diff().fillna(0)
    df["momentum"] = df["price"] - df["price"].shift(10).fillna(df["price"])
    df["volatility"] = df["returns"].rolling(20).std().fillna(0)

    # Multi-timeframe
    df["momentum_fast"] = df["price"] - df["price"].shift(5).fillna(df["price"])
    df["momentum_slow"] = df["price"] - df["price"].shift(20).fillna(df["price"])

    df["win"] = np.random.choice([0,1], len(df))

    # -----------------------------
    # AI MODEL (ENSEMBLE STYLE)
    # -----------------------------
    features = ["returns","momentum","volatility","momentum_fast","momentum_slow"]
    X = df[features]
    y = df["win"]

    model = RandomForestClassifier(n_estimators=200, max_depth=8)
    model.fit(X, y)

    latest = X.iloc[-1:]
    confidence = model.predict_proba(latest)[0][1]

    # -----------------------------
    # REGIME CLASSIFIER
    # -----------------------------
    vol = df["volatility"].iloc[-1]

    if vol < 0.05:
        regime = "🧊 CONTROLLED"
    elif vol > 0.4:
        regime = "🔥 EXTREME VOL"
    else:
        regime = "⚖️ NORMAL"

    # -----------------------------
    # ENTROPY + SIGNAL STACK
    # -----------------------------
    hist, _ = np.histogram(df["returns"], bins=30, density=True)
    entropy_score = entropy(hist)

    trend_strength = abs(df["momentum_fast"].iloc[-1])

    # -----------------------------
    # EVOLUTIONARY STRATEGY FILTER
    # -----------------------------
    score = 0

    if entropy_score < 1.6:
        score += 1
    if vol < 0.05:
        score += 1
    if confidence < 0.6:
        score += 1
    if trend_strength < 0.2:
        score += 1

    if score >= 3:
        decision = "🚨 BLOCK"
    elif confidence > 0.7 and trend_strength > 0.3:
        decision = "🎯 EXECUTE"
    else:
        decision = "⚠️ HOLD"

    # -----------------------------
    # PERFORMANCE SIMULATION
    # -----------------------------
    balance = 1000
    equity = []

    for i in range(len(df)):
        if confidence > 0.65 and entropy_score > 1.7:
            balance += 15
        else:
            balance -= 7
        equity.append(balance)

    # -----------------------------
    # UI
    # -----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Confidence", f"{confidence:.2f}")
    col2.metric("Entropy", f"{entropy_score:.2f}")
    col3.metric("Volatility", f"{vol:.2f}")
    col4.metric("Trend", f"{trend_strength:.2f}")

    st.subheader("🧠 Regime")
    st.write(regime)

    st.subheader("🎯 Decision Engine")
    st.write(decision)

    st.subheader("📈 Equity Curve")
    st.line_chart(equity)

    st.subheader("📊 Price Action")
    st.line_chart(df["price"])

    st.subheader("🚨 System Alerts")

    if decision == "🚨 BLOCK":
        st.error("MARKET MANIPULATION DETECTED")
    elif decision == "⚠️ HOLD":
        st.warning("NO CLEAR EDGE")
    else:
        st.success("EXECUTION WINDOW")

else:
    st.info("Start feed to activate system")