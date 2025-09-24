# Black-Scholes Options Analyzer

Interactive web application for options pricing analysis using the Black-Scholes model with 3D visualization and real-time market data comparison.

## 🌐 Live Demo
[Try it here: https://black-scholes-options-analyzer.onrender.com/]

## Features
- Real-time options pricing using Black-Scholes model
- Interactive 3D surface visualization of option values
- Greeks calculation (Delta, Gamma, Theta, Vega, Rho)
- Market price vs theoretical price analysis
- Comprehensive mathematical theory section
- Professional dark trading interface

## Technology Stack
- **Backend**: Python, Flask
- **Mathematical Libraries**: NumPy, SciPy, pandas
- **Data Source**: yfinance for real market data
- **Frontend**: HTML, CSS, JavaScript
- **Visualization**: Plot.ly for 3D graphics
- **Deployment**: Render.com

## Mathematical Implementation
Implements the complete Black-Scholes partial differential equation: ∂V/∂t + ½σ²S²∂²V/∂S² + rS∂V/∂S - rV = 0

## Local Development
```bash
git clone https://github.com/yourusername/black-scholes-options-analyzer
cd black-scholes-options-analyzer
pip install -r requirements.txt
python options_app.py
