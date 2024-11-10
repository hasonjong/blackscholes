import numpy as np
from scipy.stats import norm
import yfinance as yf
from flask import Flask, render_template, request

app = Flask(__name__)

# Black-Scholes function to calculate option price
def blackScholes(r, S, K, T, sigma, type="C"):
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if type == "C":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif type == "P":
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        price = None
    return round(price, 2)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Fetch form data
            ticker = request.form["ticker"]
            strike = float(request.form["strike"])
            time = int(request.form["time"])
            rate = float(request.form["rate"])
            option_type = request.form["option_type"]

            # Map option type to full name for display
            option_type_full = "Call" if option_type == "C" else "Put"

            # Fetch current stock price
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if hist.empty:
                raise ValueError("No data found for the given ticker symbol.")
            S = hist['Close'][0]

            # Calculate time to expiration in years
            T = time / 365

            # Fetch historical stock data for volatility calculation
            hist = stock.history(period="1y")
            if hist.empty:
                raise ValueError("No historical data available for volatility calculation.")
            hist['Log Returns'] = np.log(hist['Close'] / hist['Close'].shift(1))
            volatility = hist['Log Returns'].std() * np.sqrt(252)  # Annualize the volatility
            sigma = volatility

            # Calculate the option price using Black-Scholes formula
            price = blackScholes(rate, S, strike, T, sigma, type=option_type)

            # Render result page with the calculated price and option type
            return render_template("result.html", price=price, option_type_full=option_type_full)

        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
