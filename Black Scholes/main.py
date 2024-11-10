import numpy as np
from scipy.stats import norm
import yfinance as yf
from flask import Flask, render_template, request

<<<<<<< HEAD
app = Flask(__name__)
=======
# Function to get validated float input     just testing something here again
def get_float(prompt, min_value=None):
    while True:
        try:
            value = float(input(prompt))
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}. Please try again.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

# Function to get validated option type input
def get_option_type(prompt):
    while True:
        option_type = input(prompt).strip().upper()
        if option_type in ('C', 'P'):
            return option_type
        else:
            print("Invalid option type. Please enter 'C' for Call or 'P' for Put.")

# User inputs with validation
ticker_symbol = input("Enter the stock ticker symbol (e.g., AAPL for Apple Inc.): ").upper()
K = get_float("Enter the strike/exercise price (K): ", min_value=0.0)
T_input = input("Enter the time to expiration (T) in days (e.g., 30 for 30 days): ")
while not T_input.isdigit() or int(T_input) <= 0:
    print("Please enter a positive integer for the number of days.")
    T_input = input("Enter the time to expiration (T) in days (e.g., 30 for 30 days): ")
T_days = int(T_input)
r = get_float("Enter the risk-free interest rate (as decimal, e.g., 0.05 for 5%): ", min_value=0.0)
option_type = get_option_type("Enter 'C' for Call option or 'P' for Put option: ")

# Fetch current stock price using yfinance
try:
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(period="1d")
    if hist.empty:
        raise ValueError("No data found for the given ticker symbol.")
    S = hist['Close'][0]
    print(f"Current stock price (S) for {ticker_symbol} is: {S}")
except Exception as e:
    print("Error fetching stock price:", e)
    exit()

# Calculate time to expiration in years
T = T_days / 365

# Fetch historical stock data for volatility calculation
try:
    hist = stock.history(period="1y")
    if hist.empty:
        raise ValueError("No historical data available for volatility calculation.")
    hist['Log Returns'] = np.log(hist['Close'] / hist['Close'].shift(1))
    volatility = hist['Log Returns'].std() * np.sqrt(252)  # Annualize the volatility
    sigma = volatility
    print(f"Calculated historical volatility (sigma) is: {sigma:.4f}")
except Exception as e:
    print("Error fetching historical data for volatility calculation:", e)
    sigma = get_float("Enter the volatility (sigma) manually (as decimal, e.g., 0.3 for 30%): ", min_value=0.0)
>>>>>>> 74955a61d24fcde03f43f40aa098eafb6c396e95

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
