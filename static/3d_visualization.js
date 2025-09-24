document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('surface-form');
    const loadingDiv = document.getElementById('loading');
    const plotDiv = document.getElementById('3d-plot');
    const infoPanel = document.getElementById('info-panel');
    const generateBtn = document.getElementById('generate-btn');

    form.addEventListener('submit', function(e) {
        e.preventDefault(); // Don't reload the page
        
        // Show loading, hide previous results
        loadingDiv.style.display = 'block';
        infoPanel.style.display = 'none';
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
        
        // Get form data
        const formData = new FormData(form);
        
        // Send request to Flask backend
        fetch('/api/surface-data', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            // Create the 3D surface plot
            createSurfacePlot(data);
            
            // Update info panel
            updateInfoPanel(data);
            
            // Hide loading
            loadingDiv.style.display = 'none';
            infoPanel.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to generate surface. Please try again.');
        })
        .finally(() => {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate 3D Surface';
        });
    });

    function createSurfacePlot(data) {
        // Create the 3D surface trace
        const surfaceTrace = {
            x: data.stock_prices,
            y: data.times,
            z: data.option_values,
            type: 'surface',
            colorscale: 'Viridis',
            showscale: true,
            colorbar: {
                title: 'Option Price ($)',
                titleside: 'right'
            }
        };

        // Calculate position for current stock price
        console.log('Current Price:', data.current_price);
        console.log('Stock Price Range:', data.stock_prices[0], 'to', data.stock_prices[data.stock_prices.length-1]);

        // Find the closest stock price in our range to the current price
        let closestIndex = 0;
        let minDifference = Math.abs(data.stock_prices[0] - data.current_price);

        for (let i = 1; i < data.stock_prices.length; i++) {
            const difference = Math.abs(data.stock_prices[i] - data.current_price);
            if (difference < minDifference) {
                minDifference = difference;
                closestIndex = i;
            }
        }

        const midTimeIndex = Math.floor(data.times.length / 2);
        const actualOptionValue = data.option_values[midTimeIndex][closestIndex];

        console.log('Marker at Stock Price:', data.stock_prices[closestIndex], 'Option Value:', actualOptionValue);

        const currentPriceTrace = {
            x: [data.current_price],  // Use actual current price
            y: [data.times[midTimeIndex]], 
            z: [actualOptionValue + 5],  // Lift slightly above surface for visibility
            mode: 'markers',
            marker: {
                size: 10,
                color: 'red',
                symbol: 'circle'
            },
            type: 'scatter3d',
            name: 'Current Price'
        };

        const plotData = [surfaceTrace, currentPriceTrace];

        // Layout configuration
        const layout = {
            title: {
                text: `${data.ticker} ${data.option_type.toUpperCase()} Option Surface (Strike: $${data.strike_price})`,
                font: { color: '#00b894', size: 18 }
            },
            scene: {
                xaxis: {
                    title: 'Stock Price ($)',
                    titlefont: { color: '#00b894' },
                    tickfont: { color: '#ffffff' }
                },
                yaxis: {
                    title: 'Time to Expiration (Years)',
                    titlefont: { color: '#00b894' },
                    tickfont: { color: '#ffffff' }
                },
                zaxis: {
                    title: 'Option Value ($)',
                    titlefont: { color: '#00b894' },
                    tickfont: { color: '#ffffff' }
                },
                bgcolor: 'rgba(45, 52, 54, 0.8)',
                camera: {
                    eye: { x: 1.5, y: 1.5, z: 1.5 }
                }
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' },
            margin: { l: 0, r: 0, t: 40, b: 0 }
        };

        // Create the plot
        Plotly.newPlot(plotDiv, plotData, layout, {
            displayModeBar: true,
            responsive: true
        });
    }

    function updateInfoPanel(data) {
        document.getElementById('info-ticker').textContent = data.ticker;
        document.getElementById('info-current-price').textContent = data.current_price.toFixed(2);
        document.getElementById('info-strike-price').textContent = data.strike_price.toFixed(2);
        document.getElementById('info-volatility').textContent = (data.volatility * 100).toFixed(1);
        document.getElementById('info-option-type').textContent = data.option_type.toUpperCase();
    }
});