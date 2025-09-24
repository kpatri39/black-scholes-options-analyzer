# pylint: disable=all
# type: ignore

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm
import math
from datetime import datetime, timedelta

class BlackScholesCalculator:
    """
    A comprehensive Black-Scholes options pricing calculator
    """
    
    def __init__(self, risk_free_rate=0.05):
        """
        Initialize the calculator with a default risk-free rate
        
        Parameters:
        risk_free_rate: Annual risk-free interest rate (default 5%)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_call_price(self, S, K, T, sigma, r=None):
        """
        Calculate Black-Scholes price for a European call option
        
        Parameters:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        sigma: Volatility (annualized)
        r: Risk-free rate (uses instance default if None)
        
        Returns:
        Call option price
        """
        if r is None:
            r = self.risk_free_rate
            
        if T <= 0:
            return max(S - K, 0)  # Intrinsic value at expiration
        
        # Calculate d1 and d2
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        # Calculate call price
        call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        
        return call_price
    
    def calculate_put_price(self, S, K, T, sigma, r=None):
        """
        Calculate Black-Scholes price for a European put option using put-call parity
        
        Parameters:
        S: Current stock price
        K: Strike price  
        T: Time to expiration (in years)
        sigma: Volatility (annualized)
        r: Risk-free rate (uses instance default if None)
        
        Returns:
        Put option price
        """
        if r is None:
            r = self.risk_free_rate
            
        if T <= 0:
            return max(K - S, 0)  # Intrinsic value at expiration
            
        # Use put-call parity: P = C - S + K*e^(-rT)
        call_price = self.calculate_call_price(S, K, T, sigma, r)
        put_price = call_price - S + K * math.exp(-r * T)
        
        return put_price
    
    def calculate_volatility(self, ticker, days=30):
        """
        Calculate historical volatility for a stock
        
        Parameters:
        ticker: Stock ticker symbol
        days: Number of days of historical data to use
        
        Returns:
        Annualized volatility
        """
        try:
            # Download historical data
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{days + 5}d")  # Get a few extra days
            
            if hist.empty:
                raise ValueError(f"No data found for ticker {ticker}")
            
            # Calculate daily returns
            hist['Daily_Return'] = np.log(hist['Close'] / hist['Close'].shift(1))
            
            # Calculate volatility (annualized)
            daily_volatility = hist['Daily_Return'].std()
            annual_volatility = daily_volatility * math.sqrt(252)  # 252 trading days per year
            
            return annual_volatility
            
        except Exception as e:
            print(f"Error calculating volatility for {ticker}: {e}")
            return None
    
    def get_current_price(self, ticker):
        """
        Get current stock price
        
        Parameters:
        ticker: Stock ticker symbol
        
        Returns:
        Current stock price
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            
            if hist.empty:
                raise ValueError(f"No data found for ticker {ticker}")
                
            return hist['Close'].iloc[-1]
            
        except Exception as e:
            print(f"Error getting current price for {ticker}: {e}")
            return None
    
    def price_option_chain(self, S, strikes, T, sigma, option_type='call', r=None):
        """
        Price multiple options with different strike prices
        
        Parameters:
        S: Current stock price
        strikes: List of strike prices
        T: Time to expiration (in years)
        sigma: Volatility (annualized)
        option_type: 'call' or 'put'
        r: Risk-free rate (uses instance default if None)
        
        Returns:
        Dictionary with strike prices as keys and option prices as values
        """
        if r is None:
            r = self.risk_free_rate
            
        option_prices = {}
        
        for strike in strikes:
            if option_type.lower() == 'call':
                price = self.calculate_call_price(S, strike, T, sigma, r)
            elif option_type.lower() == 'put':
                price = self.calculate_put_price(S, strike, T, sigma, r)
            else:
                raise ValueError("option_type must be 'call' or 'put'")
                
            option_prices[strike] = price
            
        return option_prices
    
    def verify_put_call_parity(self, S, K, T, sigma, r=None):
        """
        Verify put-call parity relationship
        
        Parameters:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)  
        sigma: Volatility (annualized)
        r: Risk-free rate (uses instance default if None)
        
        Returns:
        Parity check value (should be close to 0)
        """
        if r is None:
            r = self.risk_free_rate
            
        call_price = self.calculate_call_price(S, K, T, sigma, r)
        put_price = self.calculate_put_price(S, K, T, sigma, r)
        
        # Put-call parity: C - P = S - K*e^(-rT)
        parity_check = call_price - put_price - S + K * math.exp(-r * T)
        
        return parity_check

# Example usage
if __name__ == "__main__":
    # Create calculator instance
    calculator = BlackScholesCalculator(risk_free_rate=0.05)
    
    # Example: Price options for Apple (AAPL)
    ticker = "AAPL"
    
    # Get current stock price and volatility
    current_price = calculator.get_current_price(ticker)
    volatility = calculator.calculate_volatility(ticker, days=30)
    
    if current_price is not None and volatility is not None:
        # Option parameters
        strike_price = current_price  # At-the-money option
        time_to_expiration = 30 / 365  # 30 days in years
        
        # Calculate option prices
        call_price = calculator.calculate_call_price(current_price, strike_price, time_to_expiration, volatility)
        put_price = calculator.calculate_put_price(current_price, strike_price, time_to_expiration, volatility)
        
        # Display results
        print("\n\n\n")
        print(f"=== Black-Scholes Options Pricing for {ticker} ===")
        print(f"Current Stock Price: ${current_price:.2f}")
        print(f"Strike Price: ${strike_price:.2f}")
        print(f"Time to Expiration: {time_to_expiration*365:.0f} days")
        print(f"Risk-free Rate: {calculator.risk_free_rate*100:.1f}%")
        print(f"Volatility: {volatility*100:.1f}%")
        print(f"\nCall Option Price: ${call_price:.2f}")
        print(f"Put Option Price: ${put_price:.2f}")
        print("\n\n\n")
        
        # Verify put-call parity
        parity_check = calculator.verify_put_call_parity(current_price, strike_price, time_to_expiration, volatility)
        print(f"\nPut-Call Parity Check: {abs(parity_check):.6f} (should be ~0)")
        
        # Example: Price option chain
        strikes = [current_price * 0.9, current_price * 0.95, current_price, current_price * 1.05, current_price * 1.1]
        call_chain = calculator.price_option_chain(current_price, strikes, time_to_expiration, volatility, 'call')
        
        print(f"\n=== Call Option Chain ===")
        for strike, price in call_chain.items():
            print(f"Strike ${strike:.2f}: ${price:.2f}")
    else:
        print(f"Could not retrieve data for {ticker}")