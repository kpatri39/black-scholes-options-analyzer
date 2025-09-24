# pylint: disable=all
# type: ignore

import math
import numpy as np
from scipy.stats import norm
from options_pricing import BlackScholesCalculator

class GreeksCalculator:
    """
    Calculate the Greeks (risk sensitivities) for Black-Scholes options
    """
    
    def __init__(self, risk_free_rate=0.05):
        """
        Initialize Greeks calculator
        
        Parameters:
        risk_free_rate: Annual risk-free interest rate
        """
        self.bs_calculator = BlackScholesCalculator(risk_free_rate)
        self.risk_free_rate = risk_free_rate
    
    def calculate_d1_d2(self, S, K, T, sigma, r=None):
        """
        Helper method to calculate d1 and d2 values used in Greeks formulas
        
        Parameters:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        sigma: Volatility (annualized)
        r: Risk-free rate
        
        Returns:
        Tuple of (d1, d2)
        """
        if r is None:
            r = self.risk_free_rate
            
        if T <= 0:
            return None, None
            
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        return d1, d2
    
    def calculate_delta(self, S, K, T, sigma, option_type='call', r=None):
        """
        Calculate Delta: ∂V/∂S (sensitivity to stock price changes)
        
        Parameters:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        sigma: Volatility (annualized)
        option_type: 'call' or 'put'
        r: Risk-free rate
        
        Returns:
        Delta value
        """
        if r is None:
            r = self.risk_free_rate
            
        if T <= 0:
            if option_type.lower() == 'call':
                return 1.0 if S > K else 0.0
            else:  # put
                return -1.0 if S < K else 0.0
        
        d1, d2 = self.calculate_d1_d2(S, K, T, sigma, r)
        
        if option_type.lower() == 'call':
            delta = norm.cdf(d1)
        elif option_type.lower() == 'put':
            delta = norm.cdf(d1) - 1
        else:
            raise ValueError("option_type must be 'call' or 'put'")
            
        return delta
    
    def calculate_gamma(self, S, K, T, sigma, r=None):
        """
        Calculate Gamma: ∂²V/∂S² (rate of change of delta)
        
        Parameters:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        sigma: Volatility (annualized)
        r: Risk-free rate
        
        Returns:
        Gamma value (same for calls and puts)
        """
        if r is None:
            r = self.risk_free_rate
            
        if T <= 0:
            return 0.0
        
        d1, d2 = self.calculate_d1_d2(S, K, T, sigma, r)
        
        # Gamma = φ(d1) / (S * σ * √T)
        # where φ(d1) is the standard normal probability density function
        gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
        
        return gamma
    
    def calculate_theta(self, S, K, T, sigma, option_type='call', r=None):
        """
        Calculate Theta: ∂V/∂T (time decay)
        
        Parameters:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        sigma: Volatility (annualized)
        option_type: 'call' or 'put'
        r: Risk-free rate
        
        Returns:
        Theta value (per year, divide by 365 for daily theta)
        """
        if r is None:
            r = self.risk_free_rate
            
        if T <= 0:
            return 0.0
        
        d1, d2 = self.calculate_d1_d2(S, K, T, sigma, r)
        
        # Common terms
        term1 = -S * norm.pdf(d1) * sigma / (2 * math.sqrt(T))
        
        if option_type.lower() == 'call':
            term2 = -r * K * math.exp(-r * T) * norm.cdf(d2)
            theta = term1 + term2
        elif option_type.lower() == 'put':
            term2 = r * K * math.exp(-r * T) * norm.cdf(-d2)
            theta = term1 + term2
        else:
            raise ValueError("option_type must be 'call' or 'put'")
            
        return theta
    
    def calculate_vega(self, S, K, T, sigma, r=None):
        """
        Calculate Vega: ∂V/∂σ (sensitivity to volatility changes)
        
        Parameters:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        sigma: Volatility (annualized)
        r: Risk-free rate
        
        Returns:
        Vega value (same for calls and puts)
        """
        if r is None:
            r = self.risk_free_rate
            
        if T <= 0:
            return 0.0
        
        d1, d2 = self.calculate_d1_d2(S, K, T, sigma, r)
        
        # Vega = S * φ(d1) * √T
        vega = S * norm.pdf(d1) * math.sqrt(T)
        
        return vega / 100  # Convention: vega per 1% change in volatility
    
    def calculate_rho(self, S, K, T, sigma, option_type='call', r=None):
        """
        Calculate Rho: ∂V/∂r (sensitivity to interest rate changes)
        
        Parameters:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        sigma: Volatility (annualized)
        option_type: 'call' or 'put'
        r: Risk-free rate
        
        Returns:
        Rho value
        """
        if r is None:
            r = self.risk_free_rate
            
        if T <= 0:
            return 0.0
        
        d1, d2 = self.calculate_d1_d2(S, K, T, sigma, r)
        
        if option_type.lower() == 'call':
            rho = K * T * math.exp(-r * T) * norm.cdf(d2)
        elif option_type.lower() == 'put':
            rho = -K * T * math.exp(-r * T) * norm.cdf(-d2)
        else:
            raise ValueError("option_type must be 'call' or 'put'")
            
        return rho / 100  # Convention: rho per 1% change in interest rate
    
    def calculate_all_greeks(self, S, K, T, sigma, option_type='call', r=None):
        """
        Calculate all Greeks for an option
        
        Parameters:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        sigma: Volatility (annualized)
        option_type: 'call' or 'put'
        r: Risk-free rate
        
        Returns:
        Dictionary containing all Greeks
        """
        if r is None:
            r = self.risk_free_rate
        
        # Calculate option price for reference
        if option_type.lower() == 'call':
            option_price = self.bs_calculator.calculate_call_price(S, K, T, sigma, r)
        else:
            option_price = self.bs_calculator.calculate_put_price(S, K, T, sigma, r)
        
        greeks = {
            'option_price': option_price,
            'delta': self.calculate_delta(S, K, T, sigma, option_type, r),
            'gamma': self.calculate_gamma(S, K, T, sigma, r),
            'theta': self.calculate_theta(S, K, T, sigma, option_type, r),
            'vega': self.calculate_vega(S, K, T, sigma, r),
            'rho': self.calculate_rho(S, K, T, sigma, option_type, r)
        }
        
        return greeks
    
    def analyze_option_risk(self, ticker, strike, days_to_expiration, option_type='call'):
        """
        Complete risk analysis for a real option
        
        Parameters:
        ticker: Stock ticker symbol
        strike: Strike price
        days_to_expiration: Days until expiration
        option_type: 'call' or 'put'
        
        Returns:
        Dictionary with current data and all Greeks
        """
        # Get current market data
        current_price = self.bs_calculator.get_current_price(ticker)
        volatility = self.bs_calculator.calculate_volatility(ticker, days=30)
        
        if current_price is None or volatility is None:
            return None
        
        T = days_to_expiration / 365  # Convert to years
        
        # Calculate all Greeks
        greeks = self.calculate_all_greeks(current_price, strike, T, volatility, option_type)
        
        # Add market context
        analysis = {
            'ticker': ticker,
            'current_price': current_price,
            'strike_price': strike,
            'days_to_expiration': days_to_expiration,
            'time_to_expiration': T,
            'volatility': volatility,
            'option_type': option_type,
            'moneyness': current_price / strike,  # S/K ratio
            'greeks': greeks
        }
        
        return analysis

# Example usage
if __name__ == "__main__":
    # Create Greeks calculator
    greeks_calc = GreeksCalculator(risk_free_rate=0.05)
    
    # Example: Analyze Apple call option
    ticker = "AAPL"
    current_price = greeks_calc.bs_calculator.get_current_price(ticker)
    
    if current_price is not None:
        strike_price = current_price  # At-the-money
        days_to_expiration = 30
        T = days_to_expiration / 365
        volatility = greeks_calc.bs_calculator.calculate_volatility(ticker, days=30)
        
        if volatility is not None:
            print("\n\n\n")
            print(f"=== Greeks Analysis for {ticker} ===")
            print(f"Current Price: ${current_price:.2f}")
            print(f"Strike Price: ${strike_price:.2f}")
            print(f"Days to Expiration: {days_to_expiration}")
            print(f"Volatility: {volatility*100:.1f}%")
            
            # Calculate Greeks for both call and put
            for option_type in ['call', 'put']:
                print(f"\n--- {option_type.upper()} OPTION ---")
                greeks = greeks_calc.calculate_all_greeks(current_price, strike_price, T, volatility, option_type)
                
                print(f"Option Price: ${greeks['option_price']:.2f}")
                print(f"Delta: {greeks['delta']:.4f}")
                print(f"Gamma: {greeks['gamma']:.4f}")
                print(f"Theta: ${greeks['theta']:.4f} per year (${greeks['theta']/365:.4f} per day)")
                print(f"Vega: ${greeks['vega']:.4f} per 1% volatility change")
                print(f"Rho: ${greeks['rho']:.4f} per 1% interest rate change")
                print("\n\n\n")
    else:
        print(f"Could not retrieve data for {ticker}")