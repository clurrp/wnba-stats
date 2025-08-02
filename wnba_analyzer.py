import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import sys
from pathlib import Path

def load_csv_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: File '{file_path}' is empty.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

def validate_data(df):
    required_columns = ['Player', 'Points']
    alternative_columns = {
        'Points': ['PTS', 'Pts', 'points', 'pts'],
        'Player': ['Name', 'name', 'player', 'PLAYER']
    }
    
    df_columns = df.columns.tolist()
    
    for required_col in required_columns:
        if required_col not in df_columns:
            for alt_col in alternative_columns.get(required_col, []):
                if alt_col in df_columns:
                    df = df.rename(columns={alt_col: required_col})
                    break
            else:
                print(f"Error: Required column '{required_col}' not found in CSV.")
                print(f"Available columns: {', '.join(df_columns)}")
                sys.exit(1)
    
    return df

def create_top_scorers_visualization(df, top_n=20):
    df_sorted = df.nlargest(top_n, 'Points')
    
    plt.figure(figsize=(12, 8))
    
    bars = plt.bar(range(len(df_sorted)), df_sorted['Points'], 
                   color='purple', alpha=0.7, edgecolor='black', linewidth=0.5)
    
    plt.xlabel('Players', fontsize=12, fontweight='bold')
    plt.ylabel('Points Scored', fontsize=12, fontweight='bold')
    plt.title(f'Top {top_n} WNBA Players by Points Scored', fontsize=14, fontweight='bold')
    
    plt.xticks(range(len(df_sorted)), df_sorted['Player'], 
               rotation=45, ha='right', fontsize=10)
    
    for i, (bar, points) in enumerate(zip(bars, df_sorted['Points'])):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                str(int(points)), ha='center', va='bottom', fontsize=9)
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    return plt

def main():
    parser = argparse.ArgumentParser(description='Analyze WNBA player statistics from CSV file')
    parser.add_argument('csv_file', help='Path to the CSV file containing WNBA stats')
    parser.add_argument('-n', '--top', type=int, default=20, 
                       help='Number of top players to display (default: 20)')
    parser.add_argument('-o', '--output', type=str, default='wnba_top_scorers.png',
                       help='Output filename for the visualization (default: wnba_top_scorers.png)')
    
    args = parser.parse_args()
    
    if not Path(args.csv_file).exists():
        print(f"Error: File '{args.csv_file}' does not exist.")
        sys.exit(1)
    
    print(f"Loading data from {args.csv_file}...")
    df = load_csv_data(args.csv_file)
    
    print("Validating data...")
    df = validate_data(df)
    
    print(f"Found {len(df)} players in the dataset.")
    
    print(f"Creating visualization for top {args.top} scorers...")
    plt = create_top_scorers_visualization(df, args.top)
    
    plt.savefig(args.output, dpi=300, bbox_inches='tight')
    print(f"Visualization saved as '{args.output}'")
    
    plt.show()
    
    print("\nTop 10 Scorers:")
    top_10 = df.nlargest(10, 'Points')[['Player', 'Points']]
    for i, (_, row) in enumerate(top_10.iterrows(), 1):
        print(f"{i:2d}. {row['Player']}: {row['Points']} points")

if __name__ == "__main__":
    main()