from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Global variables
df = None
cities = []
states = []

def load_data():
    """Load the climate dataset from data folder"""
    global df, cities, states
    
    # Look for CSV in data folder (based on your file structure)
    csv_path = os.path.join('data', 'Indian_Climate_Dataset_2024_2025.csv')
    
    print(f"Looking for file at: {csv_path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"File exists: {os.path.exists(csv_path)}")
    
    if os.path.exists(csv_path):
        print(f"✅ Loading data from: {csv_path}")
        try:
            df = pd.read_csv(csv_path)
            df['Date'] = pd.to_datetime(df['Date'])
            print(f"✅ Successfully loaded {len(df)} records")
            print(f"✅ Columns: {list(df.columns)[:5]}...")
            print(f"✅ Cities: {df['City'].unique().tolist()[:5]}...")
            return df
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return create_sample_data()
    else:
        print(f"❌ CSV file not found at {csv_path}")
        print("Creating sample data for demonstration...")
        return create_sample_data()

def create_sample_data():
    """Create sample data if CSV not found"""
    print("Creating sample climate data...")
    dates = pd.date_range(start='2024-01-01', end='2025-12-31', freq='D')
    cities_list = ['Mumbai', 'Delhi', 'Bengaluru', 'Chennai', 'Kolkata', 'Hyderabad', 
                   'Ahmedabad', 'Jaipur', 'Lucknow', 'Bhopal']
    states_list = ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal', 
                   'Telangana', 'Gujarat', 'Rajasthan', 'Uttar Pradesh', 'Madhya Pradesh']
    aqi_categories = ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor']
    
    data = []
    for date in dates:
        for i, city in enumerate(cities_list):
            month = date.month
            
            # Seasonal patterns
            if month in [5, 6]:  # Summer
                temp_base = 38
                humidity_base = 45
                rainfall_base = 10
            elif month in [12, 1, 2]:  # Winter
                temp_base = 22
                humidity_base = 65
                rainfall_base = 5
            elif month in [7, 8, 9]:  # Monsoon
                temp_base = 30
                humidity_base = 80
                rainfall_base = 30
            else:  # Post-monsoon
                temp_base = 32
                humidity_base = 60
                rainfall_base = 15
            
            # City-specific adjustments
            if city in ['Delhi', 'Lucknow']:
                temp_base += 2
            elif city in ['Bengaluru', 'Mumbai']:
                temp_base -= 2
            
            temp_avg = round(temp_base + np.random.uniform(-5, 5), 1)
            temp_max = round(temp_avg + np.random.uniform(2, 8), 1)
            temp_min = round(temp_avg - np.random.uniform(5, 12), 1)
            humidity = round(humidity_base + np.random.uniform(-20, 20), 1)
            rainfall = round(max(0, rainfall_base + np.random.exponential(10)), 1)
            wind_speed = round(np.random.uniform(5, 25), 1)
            aqi = round(np.random.uniform(50, 400), 1)
            aqi_category = np.random.choice(aqi_categories, p=[0.1, 0.2, 0.3, 0.25, 0.15])
            pressure = round(np.random.uniform(990, 1025), 1)
            cloud_cover = round(np.random.uniform(0, 100), 1)
            
            data.append({
                'Date': date,
                'City': city,
                'State': states_list[i],
                'Temperature_Max (°C)': temp_max,
                'Temperature_Min (°C)': temp_min,
                'Temperature_Avg (°C)': temp_avg,
                'Humidity (%)': humidity,
                'Rainfall (mm)': rainfall,
                'Wind_Speed (km/h)': wind_speed,
                'AQI': aqi,
                'AQI_Category': aqi_category,
                'Pressure (hPa)': pressure,
                'Cloud_Cover (%)': cloud_cover
            })
    
    df = pd.DataFrame(data)
    print(f"✅ Created {len(df)} sample records")
    return df

# Load the data
df = load_data()
cities = df['City'].unique().tolist()
states = df['State'].unique().tolist()

print(f"\n📊 Data Summary:")
print(f"   - Total Records: {len(df)}")
print(f"   - Date Range: {df['Date'].min()} to {df['Date'].max()}")
print(f"   - Cities: {len(cities)}")
print(f"   - States: {len(states)}")
print(f"   - Temperature Range: {df['Temperature_Avg (°C)'].min()}°C to {df['Temperature_Avg (°C)'].max()}°C")

@app.route('/')
def index():
    return render_template('index.html', cities=cities, states=states)

@app.route('/analysis')
def analysis():
    return render_template('analysis.html', cities=cities, states=states)

@app.route('/predict')
def predict():
    return render_template('predict.html', cities=cities)

@app.route('/api/summary')
def get_summary():
    """Get overall climate summary"""
    try:
        summary = {
            'total_records': len(df),
            'date_range': {
                'start': df['Date'].min().strftime('%Y-%m-%d'),
                'end': df['Date'].max().strftime('%Y-%m-%d')
            },
            'avg_temperature': round(df['Temperature_Avg (°C)'].mean(), 1),
            'max_temperature': round(df['Temperature_Max (°C)'].max(), 1),
            'min_temperature': round(df['Temperature_Min (°C)'].min(), 1),
            'avg_humidity': round(df['Humidity (%)'].mean(), 1),
            'total_rainfall': round(df['Rainfall (mm)'].sum(), 1),
            'avg_aqi': round(df['AQI'].mean(), 1),
            'cities_count': len(cities),
            'states_count': len(states)
        }
        return jsonify(summary)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cities')
def get_cities():
    return jsonify(cities)

@app.route('/api/city-data/<city>')
def get_city_data(city):
    """Get climate data for a specific city"""
    try:
        city_df = df[df['City'] == city].copy()
        if city_df.empty:
            return jsonify({'error': 'City not found'}), 404
        
        city_df['Date_str'] = city_df['Date'].dt.strftime('%Y-%m-%d')
        recent_data = city_df.tail(90)
        
        result = {
            'city': city,
            'state': city_df['State'].iloc[0],
            'data': recent_data[['Date_str', 'Temperature_Avg (°C)', 'Humidity (%)', 
                                'Rainfall (mm)', 'AQI', 'Wind_Speed (km/h)']].to_dict('records'),
            'stats': {
                'avg_temp': round(city_df['Temperature_Avg (°C)'].mean(), 1),
                'max_temp': round(city_df['Temperature_Max (°C)'].max(), 1),
                'min_temp': round(city_df['Temperature_Min (°C)'].min(), 1),
                'avg_humidity': round(city_df['Humidity (%)'].mean(), 1),
                'total_rainfall': round(city_df['Rainfall (mm)'].sum(), 1),
                'avg_aqi': round(city_df['AQI'].mean(), 1)
            }
        }
        return jsonify(result)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/seasonal-trends')
def get_seasonal_trends():
    """Get seasonal trends analysis"""
    try:
        df_copy = df.copy()
        
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Summer'
            elif month in [6, 7, 8, 9]:
                return 'Monsoon'
            else:
                return 'Post-Monsoon'
        
        df_copy['Season'] = df_copy['Date'].dt.month.apply(get_season)
        
        seasonal_data = {
            'seasons': ['Winter', 'Summer', 'Monsoon', 'Post-Monsoon'],
            'temperature': [],
            'humidity': [],
            'rainfall': [],
            'aqi': []
        }
        
        for season in seasonal_data['seasons']:
            season_df = df_copy[df_copy['Season'] == season]
            if not season_df.empty:
                seasonal_data['temperature'].append(round(season_df['Temperature_Avg (°C)'].mean(), 1))
                seasonal_data['humidity'].append(round(season_df['Humidity (%)'].mean(), 1))
                seasonal_data['rainfall'].append(round(season_df['Rainfall (mm)'].sum(), 1))
                seasonal_data['aqi'].append(round(season_df['AQI'].mean(), 1))
            else:
                seasonal_data['temperature'].append(0)
                seasonal_data['humidity'].append(0)
                seasonal_data['rainfall'].append(0)
                seasonal_data['aqi'].append(0)
        
        return jsonify(seasonal_data)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/aqi-distribution')
def get_aqi_distribution():
    """Get AQI category distribution"""
    try:
        aqi_counts = df['AQI_Category'].value_counts().to_dict()
        return jsonify(aqi_counts)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({}), 500

@app.route('/api/top-cities')
def get_top_cities():
    """Get top cities by temperature"""
    try:
        metric = request.args.get('metric', 'Temperature_Avg (°C)')
        limit = int(request.args.get('limit', 5))
        
        city_stats = df.groupby('City')['Temperature_Avg (°C)'].mean().round(1)
        top_cities = city_stats.nlargest(limit).to_dict()
        return jsonify(top_cities)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({}), 500

@app.route('/api/predict-temperature', methods=['POST'])
def predict_temperature():
    """Temperature prediction"""
    try:
        data = request.json
        city = data.get('city')
        days_ahead = int(data.get('days_ahead', 7))
        
        city_df = df[df['City'] == city].copy()
        if city_df.empty:
            return jsonify({'error': 'City not found'}), 404
        
        city_df = city_df.sort_values('Date')
        recent_data = city_df.tail(30)
        
        if len(recent_data) < 7:
            return jsonify({'error': 'Insufficient data for prediction'}), 400
        
        x = np.arange(len(recent_data))
        y = recent_data['Temperature_Avg (°C)'].values
        
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        
        last_date = recent_data['Date'].max()
        last_temp = recent_data['Temperature_Avg (°C)'].iloc[-1]
        
        predictions = []
        for i in range(1, days_ahead + 1):
            future_date = last_date + timedelta(days=i)
            trend_pred = p(len(recent_data) + i)
            
            month = future_date.month
            if month in [5, 6]:
                seasonal_factor = 2
            elif month in [12, 1]:
                seasonal_factor = -3
            elif month in [7, 8]:
                seasonal_factor = -1
            else:
                seasonal_factor = 0
            
            predicted_temp = round(trend_pred + seasonal_factor, 1)
            
            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'predicted_temp': predicted_temp,
                'trend': 'up' if predicted_temp > last_temp else 'down'
            })
        
        return jsonify({
            'city': city,
            'current_temp': last_temp,
            'predictions': predictions
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rainfall-prediction', methods=['POST'])
def predict_rainfall():
    """Rainfall prediction based on historical patterns"""
    try:
        data = request.json
        city = data.get('city')
        month = int(data.get('month', datetime.now().month))
        
        city_df = df[df['City'] == city].copy()
        if city_df.empty:
            return jsonify({'error': 'City not found'}), 404
        
        historical = city_df[city_df['Date'].dt.month == month]
        
        if len(historical) == 0:
            return jsonify({'error': 'No historical data for this month'}), 400
        
        avg_rainfall = historical['Rainfall (mm)'].mean()
        max_rainfall = historical['Rainfall (mm)'].max()
        rainy_days = (historical['Rainfall (mm)'] > 0).sum()
        
        probability = min(100, int((rainy_days / len(historical)) * 100))
        
        if avg_rainfall == 0:
            intensity = "No Rainfall"
        elif avg_rainfall < 10:
            intensity = "Light Rainfall"
        elif avg_rainfall < 50:
            intensity = "Moderate Rainfall"
        else:
            intensity = "Heavy Rainfall"
        
        return jsonify({
            'city': city,
            'month': month,
            'predicted_rainfall': round(avg_rainfall, 1),
            'max_expected': round(max_rainfall, 1),
            'probability': probability,
            'intensity': intensity
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/correlation-analysis')
def get_correlation():
    """Get correlation between different climate factors"""
    try:
        correlation_data = df[['Temperature_Avg (°C)', 'Humidity (%)', 
                              'Rainfall (mm)', 'Wind_Speed (km/h)', 'AQI']].corr().round(2)
        
        correlation_list = []
        for i in correlation_data.index:
            for j in correlation_data.columns:
                correlation_list.append({
                    'x': i,
                    'y': j,
                    'value': correlation_data.loc[i, j]
                })
        
        return jsonify(correlation_list)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([]), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌤️  Climate Analysis Web Application")
    print("="*50)
    print(f"📊 Data loaded: {len(df)} records")
    print(f"📍 Cities: {', '.join(cities[:5])}...")
    print(f"🌐 Server running at: http://127.0.0.1:5001")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5001)  