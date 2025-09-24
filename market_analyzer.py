# pylint: disable=all
# type: ignore

import numpy as np
from options_pricing import BlackScholesCalculator
from the_greeks import GreeksCalculator

class MarketOptionsAnalyzer:
    """
    Compares theoretical Black-Scholes option prices with real market prices.
    Analyzes discrepancies between model predictions and actual trading data
    to identify potential mispricing and market sentiment.
    """

    def __init__(self, risk_free_rate=0.05):
        """
        Initialize options analyzer
        
        Parameters:
        risk_free_rate: Annual risk-free interest rate
        """
        self.greeks_calculator = GreeksCalculator(risk_free_rate)
        
    def analyze_option(self, ticker, strike_price, days_to_expiration, market_price, option_type='call'):
        """
        Compare theoretical Black-Scholes price with actual market price for an option

        Parameters:
        ticker: Stock ticker symbol (e.g., 'NVDA')
        strike_price: Option strike price 
        days_to_expiration: Days until option expires
        market_price: Actual market price of the option
        option_type: 'call' or 'put' (default: 'call')

        Returns:
        Dictionary containing theoretical price, market price, difference, and Greeks analysis
        """

        stock_price = self.greeks_calculator.bs_calculator.get_current_price(ticker)
        volatility = self.greeks_calculator.bs_calculator.calculate_volatility(ticker)
        t = days_to_expiration / 365

        if option_type == 'call':
            bs_price = self.greeks_calculator.bs_calculator.calculate_call_price(stock_price, strike_price, t, volatility)
        
        elif option_type == 'put':
            bs_price = self.greeks_calculator.bs_calculator.calculate_put_price(stock_price, strike_price, t, volatility)
        
        difference = market_price - bs_price # positive = market overpriced, negative = market overpriced
        percent_diff = (difference / bs_price) * 100

        greeks = self.greeks_calculator.calculate_all_greeks(stock_price, strike_price, t, volatility, option_type)

        if stock_price is None or volatility is None:
            return None  # or some error message
        
        return {
            'ticker': ticker,
            'theoretical_price': bs_price,
            'market_price': market_price,  
            'difference': difference,
            'percentage_diff': percent_diff,
            'stock_price': stock_price,
            'volatility': volatility,
            'greeks': greeks,
            'option_type': option_type
        }
    
    def generate_option_surface(self, current_price, strike_price, volatility, option_type='call', r=None):
        """
        Generate 3D surface data for Black-Scholes option pricing
        
        Parameters:
        current_price: Current stock price (center point)
        strike_price: Strike price of the option
        volatility: Volatility to use
        option_type: 'call' or 'put'
        r: Risk-free rate
        
        Returns:
        Dictionary with stock_prices, times, and option_values arrays for 3D plotting
        """
        if r is None:
            r = self.greeks_calculator.risk_free_rate
        
        # Create ranges for the surface
        # Stock price range: 50% to 150% of current price
        min_stock = current_price * 0.5
        max_stock = current_price * 1.5
        stock_prices = np.linspace(min_stock, max_stock, 50)
        
        # Time range: 1 day to 1 year
        min_time = 1/365  # 1 day
        max_time = 1.0    # 1 year
        times = np.linspace(min_time, max_time, 30)
        
        # Create meshgrid for 3D surface
        S_mesh, T_mesh = np.meshgrid(stock_prices, times)
        
        # Calculate option values for each point
        option_values = np.zeros_like(S_mesh)
        
        for i in range(len(times)):
            for j in range(len(stock_prices)):
                S = S_mesh[i, j]
                T = T_mesh[i, j]
                
                if option_type.lower() == 'call':
                    option_values[i, j] = self.greeks_calculator.bs_calculator.calculate_call_price(
                        S, strike_price, T, volatility, r
                    )
                else:
                    option_values[i, j] = self.greeks_calculator.bs_calculator.calculate_put_price(
                        S, strike_price, T, volatility, r
                    )
        
        return {
            'stock_prices': stock_prices,
            'times': times,
            'S_mesh': S_mesh,
            'T_mesh': T_mesh,
            'option_values': option_values,
            'current_price': current_price,
            'strike_price': strike_price,
            'volatility': volatility,
            'option_type': option_type
        }

if __name__ == "__main__":
    analyzer = MarketOptionsAnalyzer()
    
    result_call = analyzer.analyze_option(
        ticker="NVDA",
        strike_price=182.50, 
        days_to_expiration=4,
        market_price=3.99,  # or whatever you used
        option_type='call'
    )

    result_put = analyzer.analyze_option(
        ticker="NVDA",
        strike_price=182.50, 
        days_to_expiration=4,
        market_price=2.76,  # or whatever you used
        option_type='put'
    )
    
    if result_call:
        print("\n\n\n")
        print("=== NVDA Call Option Analysis ===")
        print(f"Stock Price: ${result_call['stock_price']:.2f}")
        print(f"\n--- PRICING ---")
        print(f"Theoretical Price: ${result_call['theoretical_price']:.2f}")
        print(f"Market Price: ${result_call['market_price']:.2f}")
        print(f"Difference: ${result_call['difference']:.2f} ({result_call['percentage_diff']:.1f}%)")
        
        print(f"\n--- GREEKS ---")
        greeks = result_call['greeks']
        print(f"Delta: {greeks['delta']:.4f}")
        print(f"Gamma: {greeks['gamma']:.4f}")
        print(f"Theta: ${greeks['theta']:.2f} per year (${greeks['theta']/365:.2f} per day)")
        print(f"Vega: ${greeks['vega']:.4f}")
        print(f"Rho: ${greeks['rho']:.4f}")
        print("\n")
    else:
        print("Analysis failed")

    if result_put:
        print("\n=== NVDA Put Option Analysis ===")
        print(f"Stock Price: ${result_put['stock_price']:.2f}")
        print(f"\n--- PRICING ---")
        print(f"Theoretical Price: ${result_put['theoretical_price']:.2f}")
        print(f"Market Price: ${result_put['market_price']:.2f}")
        print(f"Difference: ${result_put['difference']:.2f} ({result_put['percentage_diff']:.1f}%)")
        
        print(f"\n--- GREEKS ---")
        greeks = result_put['greeks']
        print(f"Delta: {greeks['delta']:.4f}")
        print(f"Gamma: {greeks['gamma']:.4f}")
        print(f"Theta: ${greeks['theta']:.2f} per year (${greeks['theta']/365:.2f} per day)")
        print(f"Vega: ${greeks['vega']:.4f}")
        print(f"Rho: ${greeks['rho']:.4f}")
        print("\n")
    
    current_price = 400  # Example Tesla price
    strike_price = 400   # At-the-money
    volatility = 0.4     # 40% volatility (high for Tesla)
    
    print("Generating 3D surface data...")
    surface_data = analyzer.generate_option_surface(
        current_price=current_price,
        strike_price=strike_price, 
        volatility=volatility,
        option_type='call'
    )
    
    print(f"Surface generated successfully!")
    print(f"Stock price range: ${surface_data['stock_prices'][0]:.2f} to ${surface_data['stock_prices'][-1]:.2f}")
    print(f"Time range: {surface_data['times'][0]:.3f} to {surface_data['times'][-1]:.1f} years")
    print(f"Option values shape: {surface_data['option_values'].shape}")
    print(f"Sample option values:")
    print(f"  Near expiry, ITM: ${surface_data['option_values'][0, -1]:.2f}")
    print(f"  Long term, ATM: ${surface_data['option_values'][-1, 25]:.2f}")