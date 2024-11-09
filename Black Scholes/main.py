import numpy as np
from scipy.stats import norm

# Function to get validated float input
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

def get_option_type(prompt):
    while True:
        option_type = input(prompt).strip().upper()
        if option_type in ('C', 'P'):
            return option_type
        else:
            print("Invalid option type. Please enter 'C' for Call or 'P' for Put.")

r = get_float("Enter the interest rate (as decimal, e.g., 0.05 for 5%): ", min_value=0.0)
S = get_float("Enter the current stock price (S): ", min_value=0.0)
K = get_float("Enter the strike/exercise price (K): ", min_value=0.0)
T = get_float("Enter the time to expiration (T) in years (e.g., 0.5 for half a year): ", min_value=0.0)
sigma = get_float("Enter the volatility (sigma) (as decimal, e.g., 0.3 for 30%): ", min_value=0.0)
option_type = get_option_type("Enter 'C' for Call option or 'P' for Put option: ")

def blackScholes(r, S, K, T, sigma, type="C"):
    "Calculate Black Scholes option price for a call/put"
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
    print("Option Price is: ", round(price, 2))
else:
    print("Option price could not be calculated due to input errors.")
