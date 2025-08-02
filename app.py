import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from flask import Flask, request, render_template, url_for, flash, redirect
from werkzeug.utils import secure_filename
import uuid
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_data(df):
    required_columns = ['Player', 'Points']
    alternative_columns = {
        'Points': ['PTS', 'Pts', 'points', 'pts', 'POINTS'],
        'Player': ['Name', 'name', 'player', 'PLAYER', 'PLAYER_NAME']
    }
    
    df_columns = df.columns.tolist()
    
    for required_col in required_columns:
        if required_col not in df_columns:
            for alt_col in alternative_columns.get(required_col, []):
                if alt_col in df_columns:
                    df = df.rename(columns={alt_col: required_col})
                    break
            else:
                raise ValueError(f"Required column '{required_col}' not found. Available columns: {', '.join(df_columns)}")
    
    if not pd.api.types.is_numeric_dtype(df['Points']):
        df['Points'] = pd.to_numeric(df['Points'], errors='coerce')
        df = df.dropna(subset=['Points'])
    
    return df

def create_visualization(df, top_n=20):
    df_sorted = df.nlargest(top_n, 'Points')
    
    plt.figure(figsize=(14, 8))
    
    bars = plt.bar(range(len(df_sorted)), df_sorted['Points'], 
                   color='#FF6B35', alpha=0.8, edgecolor='#2C3E50', linewidth=1)
    
    plt.xlabel('Players', fontsize=14, fontweight='bold', color='#2C3E50')
    plt.ylabel('Points Scored', fontsize=14, fontweight='bold', color='#2C3E50')
    plt.title(f'Top {top_n} WNBA Players by Points Scored', 
              fontsize=16, fontweight='bold', color='#2C3E50', pad=20)
    
    plt.xticks(range(len(df_sorted)), df_sorted['Player'], 
               rotation=45, ha='right', fontsize=11)
    
    for i, (bar, points) in enumerate(zip(bars, df_sorted['Points'])):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(df_sorted['Points']) * 0.01,
                str(int(points)), ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.tight_layout()
    
    chart_filename = f'chart_{uuid.uuid4().hex}.png'
    chart_path = os.path.join(app.config['STATIC_FOLDER'], chart_filename)
    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return chart_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error='No file selected')
    
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error='No file selected')
    
    if not allowed_file(file.filename):
        return render_template('index.html', error='Please upload a CSV file')
    
    try:
        top_n = int(request.form.get('top_n', 20))
        if top_n < 5 or top_n > 50:
            top_n = 20
    except ValueError:
        top_n = 20
    
    try:
        df = pd.read_csv(file)
        
        if df.empty:
            return render_template('index.html', error='The CSV file is empty')
        
        df = validate_data(df)
        
        if len(df) == 0:
            return render_template('index.html', error='No valid data found in the CSV file')
        
        chart_filename = create_visualization(df, top_n)
        chart_url = url_for('static', filename=chart_filename)
        
        top_10 = df.nlargest(10, 'Points')[['Player', 'Points']]
        top_players = [{'name': row['Player'], 'points': int(row['Points'])} 
                      for _, row in top_10.iterrows()]
        
        return render_template('index.html', 
                             chart_url=chart_url, 
                             top_n=top_n,
                             top_players=top_players)
    
    except pd.errors.EmptyDataError:
        return render_template('index.html', error='The CSV file is empty or corrupted')
    except ValueError as e:
        return render_template('index.html', error=str(e))
    except Exception as e:
        return render_template('index.html', error=f'Error processing file: {str(e)}')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)
    app.run(debug=True, host='127.0.0.1', port=5000)