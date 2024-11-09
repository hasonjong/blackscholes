import numpy as np
from scipy.stats import norm
import yfinance as yf

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

def blackScholes(r, S, K, T, sigma, type="C"):
    "Calculate Black-Scholes option price for a call/put"
    try:
        d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        if type == "C":  # Call option
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        elif type == "P":  # Put option
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        else:
            raise ValueError("Invalid option type. Enter 'C' for Call or 'P' for Put.")
        return price
    except Exception as e:
        print("Error in calculating option price:", e)
        return None

price = blackScholes(r, S, K, T, sigma, type=option_type)
if price is not None:
    print(f"The {option_type} option price is: {round(price, 2)}")
else:
    print("Option price could not be calculated due to input errors.")
