# 📊 Value-at-Risk (VaR) & Expected Shortfall (ES) Calculator

A simple but complete Python tool for downloading financial price data, computing daily returns, and calculating **Value-at-Risk (VaR)** and **Expected Shortfall (ES)** using historical simulation.  
The project also generates a histogram of daily returns and saves it as an image.

---

## 🚀 Features

- 📥 Automatically downloads adjusted close prices using **Yahoo Finance (yfinance)**
- 📈 Computes **daily returns** from closing prices  
- 🔻 Calculates:
  - **VaR 95%**
  - **VaR 99%**
  - **ES 95%**
  - **ES 99%**
- 🖼 Saves histogram plot of returns (`AAPL_returns_hist_FINAL.png`)
- 🧹 Clean and modular code structure
- 🧪 Safe handling of NaNs and empty tail events
- 💾 Runs fully from the command line

---

## 🧮 What is VaR & ES?

| Metric | Explanation |
|--------|-------------|
| **Value-at-Risk (VaR)** | The maximum expected loss at a given confidence level (e.g., 95%). |
| **Expected Shortfall (ES)** | The *average* loss in the worst α% of cases (e.g., worst 5%). |

Example:  
If **VaR(95%) = -2%**, it means:  
➡️ "There is a 5% chance the daily loss exceeds 2%."

If **ES(95%) = -3.4%**, it means:  
➡️ "If loss is worse than VaR, the *average* loss is 3.4%."

---

## 🛠 Installation

Install dependencies:

```bash
pip install yfinance pandas numpy matplotlib



