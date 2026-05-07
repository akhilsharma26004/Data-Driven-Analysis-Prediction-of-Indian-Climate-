import pandas as pd
import os

# Check if CSV exists in data folder
csv_path = 'data/Indian_Climate_Dataset_2024_2025.csv'

print(f"Checking for file: {csv_path}")
print(f"File exists: {os.path.exists(csv_path)}")
print(f"Current directory: {os.getcwd()}")

if os.path.exists(csv_path):
    try:
        df = pd.read_csv(csv_path)
        print(f"\n✅ Successfully loaded CSV!")
        print(f"   - Number of rows: {len(df)}")
        print(f"   - Number of columns: {len(df.columns)}")
        print(f"   - Columns: {list(df.columns)}")
        print(f"\nFirst 5 rows:")
        print(df.head())
        
        # Check if Date column exists
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            print(f"\n✅ Date column converted successfully")
            print(f"   - Date range: {df['Date'].min()} to {df['Date'].max()}")
        
        # Check unique cities
        if 'City' in df.columns:
            print(f"\n✅ Cities found: {df['City'].unique().tolist()}")
            print(f"   - Total unique cities: {len(df['City'].unique())}")
            
    except Exception as e:
        print(f"\n❌ Error reading CSV: {e}")
else:
    print(f"\n❌ CSV file not found!")
    print("\nPlease check:")
    print("1. Is the file name exactly 'Indian_Climate_Dataset_2024_2025.csv'?")
    print("2. Is it in the 'data' folder?")
    
    # List contents of current directory
    print("\nFiles in current directory:")
    for item in os.listdir('.'):
        print(f"  - {item}")
    
    # List contents of data folder if it exists
    if os.path.exists('data'):
        print("\nFiles in 'data' folder:")
        for item in os.listdir('data'):
            print(f"  - {item}")
    else:
        print("\n❌ 'data' folder not found!")