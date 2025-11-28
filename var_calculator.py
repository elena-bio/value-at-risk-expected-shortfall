# var_calculator.py
"""
Debug-robust Historical VaR & ES Calculator
FIX: Ensures strict scalar conversion before percentage formatting (safe_pct_str usage).
"""

import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

# ---------- helpers ----------
def to_scalar_strict(x):
    """
    Try to coerce x to a single python float.
    If x is Series/ndarray of length 1 -> return float(value).
    If x is Series/ndarray with length >1 -> raise ValueError with info.
    If conversion fails -> raise.
    """
    # pandas Series
    if isinstance(x, pd.Series):
        if x.size == 1:
            return float(x.iloc[0])
        else:
            raise ValueError(f"Cannot convert Series with size>1 to scalar. Series.shape={x.shape}\nValues:\n{x.head(5)}")
    # pandas DataFrame
    if isinstance(x, pd.DataFrame):
        # try to reduce if single cell
        if x.size == 1:
            return float(x.values.ravel()[0])
        else:
            raise ValueError(f"Cannot convert DataFrame with size>1 to scalar. DataFrame.shape={x.shape}")
    # numpy array
    if isinstance(x, np.ndarray):
        arr = np.asarray(x).ravel()
        if arr.size == 1:
            return float(arr[0])
        else:
            raise ValueError(f"Cannot convert ndarray with size>1 to scalar. ndarray.shape={x.shape}")
    # numpy scalar or plain python number
    try:
        return float(x)
    except Exception as e:
        raise ValueError(f"Cannot convert object to float: {type(x)} - {e}")

def safe_pct_str(x):
    """
    Safely format x as percentage string. Accepts scalars or single-element containers.
    
    CRITICAL FIX: Strictly converts to a standard Python float before formatting 
    to prevent TypeError on NumPy/Pandas scalar types, and provides safe fallback.
    """
    try:
        # Convert strictly to a standard Python float
        val = to_scalar_strict(x)
        # Format the standard Python float
        return f"{val:.4%}"
    except Exception:
        # fallback: show repr for debugging
        return f"(conversion/formatting error) {repr(x)}"

# ---------- core functions ----------
def download_close_series(ticker="AAPL", period="1y"):
    """Downloads adjusted close price data."""
    # Note: explicit auto_adjust=True fixes the FutureWarning
    df = yf.download(ticker, period=period, auto_adjust=True)
    if isinstance(df, pd.Series):
        return df.dropna()
    if "Close" not in df.columns:
        raise RuntimeError("Downloaded data does not contain 'Close' column. df.columns=" + repr(df.columns))
    close = df["Close"].dropna()
    return close

def compute_returns(close_series):
    """Computes daily percentage returns."""
    return close_series.pct_change().dropna()

def historical_var(returns, level=95):
    """Calculates Historical Value at Risk (VaR)."""
    alpha = 100 - level
    val = np.percentile(returns, alpha)
    return val

def expected_shortfall(returns, var_value):
    """Calculates Expected Shortfall (ES)."""
    tail = returns[returns <= var_value]
    if len(tail) == 0:
        return float("nan")
    mean_val = tail.mean()
    return mean_val

def plot_returns(returns, ticker="AAPL"):
    """Plots the histogram of daily returns."""
    plt.figure(figsize=(8,4))
    plt.hist(returns, bins=50)
    plt.title(f"Daily Returns Distribution - {ticker}")
    plt.xlabel("Return")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ---------- main ----------
def main():
    ticker = "AAPL"
    try:
        # Passing auto_adjust=True to silence warning, although yfinance default is changing
        close = download_close_series(ticker, period="1y") 
    except Exception as e:
        print("Error downloading data:", e)
        sys.exit(1)

    print("DEBUG: type(close) =", type(close))
    if isinstance(close, (pd.Series, pd.DataFrame, np.ndarray)):
        try:
            print("DEBUG: close.shape/size:", getattr(close, "shape", None), " size:", getattr(close, "size", None))
        except:
            pass

    returns = compute_returns(close)
    print("DEBUG: type(returns) =", type(returns))
    if isinstance(returns, (pd.Series, pd.DataFrame, np.ndarray)):
        try:
            print("DEBUG: returns.shape/size:", getattr(returns, "shape", None), " size:", getattr(returns, "size", None))
        except:
            pass

    # compute raw values
    var95_raw = historical_var(returns, 95)
    var99_raw = historical_var(returns, 99)
    es95_raw = expected_shortfall(returns, var95_raw)
    es99_raw = expected_shortfall(returns, var99_raw)

    # DEBUG: print raw types & reprs (first few elements if container)
    def debug_show(name, v):
        t = type(v)
        print(f"DEBUG: {name} type = {t}")
        try:
            if isinstance(v, pd.Series) or isinstance(v, pd.DataFrame):
                print(f"DEBUG: {name} head:\n{v.head(5)}")
            elif isinstance(v, np.ndarray):
                print(f"DEBUG: {name} ndarray shape {v.shape} first elements {v.ravel()[:5]}")
            else:
                print(f"DEBUG: {name} repr: {repr(v)}")
        except Exception as e:
            print(f"DEBUG: could not show {name} contents: {e}")

    debug_show("var95_raw", var95_raw)
    debug_show("var99_raw", var99_raw)
    debug_show("es95_raw", es95_raw)
    debug_show("es99_raw", es99_raw)

    # Now convert strictly to scalar floats
    # This step is critical for stability and is where your issue occurs if raw values are not scalar
    var95 = float("nan")
    var99 = float("nan")
    es95 = float("nan")
    es99 = float("nan")
    
    # Use to_scalar_strict to get final float values
    try:
        var95 = to_scalar_strict(var95_raw)
    except Exception as e:
        print(f"ERROR converting var95 to scalar: {e}. Keeping as NaN.")
    
    try:
        var99 = to_scalar_strict(var99_raw)
    except Exception as e:
        print(f"ERROR converting var99 to scalar: {e}. Keeping as NaN.")
    
    # *** If es95_raw is a Series, this conversion should succeed ***
    try:
        es95 = to_scalar_strict(es95_raw)
    except Exception as e:
        print(f"ERROR converting es95 to scalar: {e}. Keeping as NaN.")
        
    try:
        es99 = to_scalar_strict(es99_raw)
    except Exception as e:
        print(f"ERROR converting es99 to scalar: {e}. Keeping as NaN.")

    # Print final results safely using safe_pct_str for all
    print("\nRESULTS:")
    print(f"TICKER: {ticker}")
    print(f"Data points (close prices): {len(close)}")
    print("Final types after conversion:",
          type(var95), type(var99), type(es95), type(es99))
    print(f"VaR 95% (daily return): {safe_pct_str(var95)}")
    print(f"VaR 99% (daily return): {safe_pct_str(var99)}")
    print(f"ES 95% (daily return): {safe_pct_str(es95)}") # Now passing the converted scalar
    print(f"ES 99% (daily return): {safe_pct_str(es99)}") # Now passing the converted scalar

    print("\nLast 5 daily returns:")
    print(returns.tail())

    # show plot
    try:
        plot_returns(returns, ticker)
    except Exception as e:
        print("Plot failed:", e)
        # fallback: save figure instead
        try:
            plt.figure(figsize=(8,4))
            plt.hist(returns, bins=50)
            plt.title(f"Daily Returns Distribution - {ticker}")
            plt.tight_layout()
            plt.savefig("returns_hist.png")
            print("Saved histogram to returns_hist.png")
        except Exception as e2:
            print("Also failed to save histogram:", e2)


if __name__ == "__main__":
    main()