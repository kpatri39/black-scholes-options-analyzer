# pylint: disable=all
# type: ignore

from flask import Flask, render_template, request, jsonify
from market_analyzer import MarketOptionsAnalyzer

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_option():
    # Get data from the form
    ticker = request.form['ticker']
    strike_price = float(request.form['strike_price'])
    days_to_expiration = int(request.form['days_to_expiration'])
    market_price = float(request.form['market_price'])
    option_type = request.form['option_type']
    
    # Run your analysis
    analyzer = MarketOptionsAnalyzer()
    result = analyzer.analyze_option(ticker, strike_price, days_to_expiration, market_price, option_type)
    
    if result:
        return render_template('results.html', result=result)
    else:
        return "Analysis failed - could not retrieve stock data"

@app.route('/3d-visualization')
def visualization():
    return render_template('3d_visualization.html')

@app.route('/api/surface-data', methods=['POST'])
def get_surface_data():
    # Get parameters from the form
    ticker = request.form['ticker']
    strike_price = float(request.form['strike_price'])
    option_type = request.form['option_type']
    
    # Get current stock data
    analyzer = MarketOptionsAnalyzer()
    current_price = analyzer.greeks_calculator.bs_calculator.get_current_price(ticker)
    volatility = analyzer.greeks_calculator.bs_calculator.calculate_volatility(ticker)
    
    if current_price and volatility:
        # Generate surface data
        surface_data = analyzer.generate_option_surface(
            current_price=current_price,
            strike_price=strike_price,
            volatility=volatility,
            option_type=option_type
        )
        
        # Convert numpy arrays to lists for JSON
        return jsonify({
            'stock_prices': surface_data['stock_prices'].tolist(),
            'times': surface_data['times'].tolist(),
            'option_values': surface_data['option_values'].tolist(),
            'current_price': current_price,
            'strike_price': strike_price,
            'volatility': volatility,
            'ticker': ticker,
            'option_type': option_type
        })
    else:
        return jsonify({'error': 'Could not retrieve stock data'})
    
@app.route('/theory')
def theory():
    return render_template('theory.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)