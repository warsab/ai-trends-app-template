"""
LiveBench Data Fetcher with HTML Visualizations
Retrieves LiveBench data and creates interactive HTML charts
Styled to match Smart Trendz Dashboard
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os

# -*- coding: utf-8 -*-
import sys
import io

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def fetch_livebench_data(offset=0, length=100):
    """
    Fetch LiveBench data from Hugging Face API
    Maximum length is 100 per request
    Returns: (DataFrame, dataset_last_modified)
    """
    print("\n" + "="*80)
    print("🔥 FETCHING LIVEBENCH DATA")
    print("="*80)
    
    all_data = []
    dataset_last_modified = None
    max_requests = 10  # Fetch up to 1000 records (10 * 100)
    
    # First, try to get dataset metadata for last modified date
    try:
        metadata_url = "https://huggingface.co/api/datasets/livebench/model_judgment"
        meta_response = requests.get(metadata_url, timeout=10)
        if meta_response.status_code == 200:
            metadata = meta_response.json()
            if 'lastModified' in metadata:
                dataset_last_modified = metadata['lastModified']
                print(f"📅 Dataset last modified: {dataset_last_modified}")
    except Exception as e:
        print(f"⚠️ Could not fetch dataset metadata: {e}")
    
    for i in range(max_requests):
        current_offset = offset + (i * length)
        url = f"https://datasets-server.huggingface.co/rows?dataset=livebench%2Fmodel_judgment&config=default&split=leaderboard&offset={current_offset}&length={length}"
        
        print(f"\n🔍 Request {i+1}/{max_requests}")
        print(f"   Offset: {current_offset}, Length: {length}")
        print("   ⏳ Sending request...")
        
        try:
            response = requests.get(url, timeout=30)
            
            print(f"   ✅ Status: {response.status_code}, Size: {len(response.text):,} bytes")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'rows' in data and data['rows']:
                    rows = data['rows']
                    row_data = [item['row'] for item in rows]
                    all_data.extend(row_data)
                    print(f"   ✅ Retrieved {len(rows)} records (Total: {len(all_data)})")
                    
                    if len(rows) < length:
                        print(f"\n✅ Reached end of dataset")
                        break
                else:
                    print(f"   ⚠ No more data available")
                    break
            elif response.status_code == 422:
                print(f"   ⚠ 422 Error - Invalid parameters or no more data")
                print(f"   Response: {response.text}")
                break
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:200]}")
                break
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            break
    
    if all_data:
        df = pd.DataFrame(all_data)
        print(f"\n✅ Total retrieved: {len(df)} records")
        print(f"📋 Columns: {df.columns.tolist()}")
        return df, dataset_last_modified
    
    return None, None


def aggregate_model_scores(df):
    """
    Aggregate scores by model and category
    """
    print("\n" + "="*80)
    print("📊 AGGREGATING MODEL SCORES")
    print("="*80)
    
    model_avg = df.groupby('model').agg({
        'score': ['mean', 'count'],
    }).reset_index()
    
    model_avg.columns = ['model', 'avg_score', 'num_questions']
    model_avg = model_avg.sort_values('avg_score', ascending=False)
    
    print(f"✅ Aggregated {len(model_avg)} unique models")
    
    category_scores = df.groupby(['model', 'category'])['score'].mean().reset_index()
    category_pivot = category_scores.pivot(index='model', columns='category', values='score').fillna(0)
    
    print(f"✅ Found {len(category_pivot.columns)} categories: {category_pivot.columns.tolist()}")
    
    return model_avg, category_pivot


def create_html_bar_chart(model_avg, top_n=20, dataset_last_modified=None):
    """
    Create an HTML bar chart using Chart.js with Smart Trendz theme
    """
    print(f"\n📊 Creating HTML bar chart for top {top_n} models...")
    
    top_models = model_avg.head(top_n)
    
    labels = top_models['model'].tolist()
    scores = top_models['avg_score'].tolist()
    counts = top_models['num_questions'].tolist()
    
    # Format dataset last modified date
    data_freshness_html = ""
    if dataset_last_modified:
        try:
            from dateutil import parser
            last_modified_dt = parser.parse(dataset_last_modified)
            formatted_date = last_modified_dt.strftime('%B %d, %Y at %H:%M UTC')
            data_freshness_html = f"""
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 15px; border-radius: 10px; margin-bottom: 30px; text-align: center;">
                <p style="margin: 0; color: #d1fae5;">
                    <i class="fas fa-database"></i> <strong>Dataset Last Updated:</strong> {formatted_date}
                </p>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #ccfbf1;">
                    <i class="fas fa-info-circle"></i> LiveBench updates monthly with new evaluation questions
                </p>
            </div>
            """
        except:
            data_freshness_html = """
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 15px; border-radius: 10px; margin-bottom: 30px; text-align: center;">
                <p style="margin: 0; color: #fef3c7;">
                    <i class="fas fa-exclamation-triangle"></i> Data freshness information unavailable
                </p>
            </div>
            """
    else:
        data_freshness_html = """
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 15px; border-radius: 10px; margin-bottom: 30px; text-align: center;">
            <p style="margin: 0; color: #fef3c7;">
                <i class="fas fa-exclamation-triangle"></i> Data freshness information unavailable
            </p>
        </div>
        """
    
    # Emerald/teal color scheme to match dashboard
    colors = []
    for score in scores:
        if score >= 0.8:
            colors.append('rgba(16, 185, 129, 0.8)')  # Emerald
        elif score >= 0.6:
            colors.append('rgba(20, 184, 166, 0.8)')  # Teal
        elif score >= 0.4:
            colors.append('rgba(245, 158, 11, 0.8)')  # Orange
        else:
            colors.append('rgba(239, 68, 68, 0.8)')  # Red
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LiveBench Leaderboard - Top {top_n} Models</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a1f1a 0%, #0d2d27 50%, #1a2820 100%);
            min-height: 100vh;
            padding: 20px;
            color: white;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(10, 31, 26, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            color: white;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
        }}
        
        .header .emoji {{
            font-size: 3em;
            filter: drop-shadow(0 0 10px rgba(16, 185, 129, 0.5));
        }}
        
        .header p {{
            color: #d1fae5;
            font-size: 1.1em;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: rgba(16, 185, 129, 0.1);
            border: 2px solid rgba(16, 185, 129, 0.3);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .stat-card:hover {{
            border-color: #10b981;
            box-shadow: 
                0 0 20px rgba(16, 185, 129, 0.4),
                0 0 40px rgba(16, 185, 129, 0.2);
            transform: translateY(-4px);
        }}
        
        .stat-card h3 {{
            font-size: 2em;
            margin-bottom: 5px;
            color: #10b981;
            text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
        }}
        
        .stat-card p {{
            opacity: 0.9;
            color: #d1fae5;
        }}
        
        .chart-container {{
            position: relative;
            margin-bottom: 40px;
            background: rgba(0, 0, 0, 0.3);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}
        
        .chart-title {{
            font-size: 1.5em;
            color: white;
            margin-bottom: 20px;
            text-align: center;
            text-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
        }}
        
        .table-container {{
            overflow-x: auto;
            margin-top: 40px;
            border-radius: 15px;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: rgba(0, 0, 0, 0.3);
        }}
        
        th {{
            background: rgba(16, 185, 129, 0.2);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #d1fae5;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid rgba(16, 185, 129, 0.1);
            color: white;
        }}
        
        tr:hover {{
            background: rgba(16, 185, 129, 0.1);
        }}
        
        .rank {{
            font-weight: bold;
            color: #10b981;
            text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
        }}
        
        .score {{
            font-weight: bold;
        }}
        
        .score.high {{
            color: #10b981;
            text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
        }}
        
        .score.medium {{
            color: #14b8a6;
        }}
        
        .score.low {{
            color: #f59e0b;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid rgba(16, 185, 129, 0.2);
            color: #d1fae5;
        }}
        
        .footer a {{
            color: #10b981;
            text-decoration: none;
            transition: all 0.3s ease;
        }}
        
        .footer a:hover {{
            color: #d1fae5;
            text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
        }}
        
        /* Floating particles animation */
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-20px); }}
        }}
        
        .floating-particle {{
            position: fixed;
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            opacity: 0.3;
            animation: float 6s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }}
    </style>
</head>
<body>
    <!-- Floating particles for atmosphere -->
    <div class="floating-particle" style="top: 10%; left: 10%;"></div>
    <div class="floating-particle" style="top: 20%; right: 15%; animation-delay: 1s;"></div>
    <div class="floating-particle" style="bottom: 15%; left: 20%; animation-delay: 2s;"></div>
    <div class="floating-particle" style="top: 60%; right: 25%; animation-delay: 3s;"></div>

    <div class="container">
        <div class="header">
            <div class="emoji">🏆</div>
            <h1>LiveBench AI Leaderboard</h1>
            <p>Top {top_n} AI Models Performance Analysis</p>
            <p style="font-size: 0.9em; color: #ccfbf1; margin-top: 10px;">
                <i class="fas fa-clock"></i> Report Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
            </p>
            <div style="margin-top: 15px;">
                <a href="https://livebench.ai" target="_blank" style="color: #10b981; text-decoration: none; margin: 0 10px; transition: all 0.3s ease;" onmouseover="this.style.color='#d1fae5'; this.style.textShadow='0 0 10px rgba(16, 185, 129, 0.5)'" onmouseout="this.style.color='#10b981'; this.style.textShadow='none'">
                    <i class="fas fa-external-link-alt"></i> Official LiveBench Website
                </a>
                <span style="color: #ccfbf1;">|</span>
                <a href="https://huggingface.co/datasets/livebench/model_judgment" target="_blank" style="color: #10b981; text-decoration: none; margin: 0 10px; transition: all 0.3s ease;" onmouseover="this.style.color='#d1fae5'; this.style.textShadow='0 0 10px rgba(16, 185, 129, 0.5)'" onmouseout="this.style.color='#10b981'; this.style.textShadow='none'">
                    <i class="fas fa-database"></i> View Dataset on Hugging Face
                </a>
            </div>
        </div>
        
        {data_freshness_html}
        
        <div class="stats">
            <div class="stat-card">
                <h3><i class="fas fa-robot"></i> {len(labels)}</h3>
                <p>Top Models</p>
            </div>
            <div class="stat-card">
                <h3><i class="fas fa-trophy"></i> {scores[0]:.1%}</h3>
                <p>Highest Score</p>
            </div>
            <div class="stat-card">
                <h3><i class="fas fa-chart-line"></i> {sum(counts):,}</h3>
                <p>Total Evaluations</p>
            </div>
        </div>
        
        <div class="chart-container">
            <h2 class="chart-title"><i class="fas fa-chart-bar"></i> Model Performance Comparison</h2>
            <canvas id="barChart"></canvas>
        </div>
        
        <div class="table-container">
            <h2 class="chart-title"><i class="fas fa-list"></i> Detailed Rankings</h2>
            <table>
                <thead>
                    <tr>
                        <th><i class="fas fa-hashtag"></i> Rank</th>
                        <th><i class="fas fa-robot"></i> Model</th>
                        <th><i class="fas fa-star"></i> Average Score</th>
                        <th><i class="fas fa-tasks"></i> Questions Answered</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add table rows
    for idx, (_, row) in enumerate(top_models.iterrows(), 1):
        score = row['avg_score']
        score_class = 'high' if score >= 0.8 else 'medium' if score >= 0.6 else 'low'
        
        html_content += f"""
                    <tr>
                        <td class="rank">#{idx}</td>
                        <td>{row['model']}</td>
                        <td class="score {score_class}">{score:.1%}</td>
                        <td>{int(row['num_questions'])} questions</td>
                    </tr>
"""
    
    html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <div style="margin-bottom: 15px;">
                <strong style="color: #10b981;"><i class="fas fa-info-circle"></i> About LiveBench</strong>
                <p style="margin: 10px 0; color: #d1fae5; font-size: 0.95em;">
                    LiveBench is a benchmark for LLMs designed with test set contamination and objective evaluation in mind. 
                    It releases new questions monthly after model training cutoffs to prevent data contamination.
                </p>
            </div>
            <p><i class="fas fa-database"></i> Data source: <a href="https://huggingface.co/datasets/livebench/model_judgment" target="_blank">LiveBench Model Judgment Dataset</a></p>
            <p style="margin-top: 10px;"><i class="fas fa-globe"></i> Official website: <a href="https://livebench.ai" target="_blank">livebench.ai</a></p>
            <p style="margin-top: 10px;"><i class="fas fa-book"></i> Research paper: <a href="https://arxiv.org/abs/2406.19314" target="_blank">arXiv:2406.19314</a></p>
            <p style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(16, 185, 129, 0.2); font-size: 0.9em; color: #ccfbf1;">
                <i class="fas fa-dove"></i> Powered by FreedomWings AI
            </p>
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('barChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'Average Score',
                    data: {json.dumps(scores)},
                    backgroundColor: {json.dumps(colors)},
                    borderColor: {json.dumps([c.replace('0.8', '1') for c in colors])},
                    borderWidth: 2
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 1.5,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(10, 31, 26, 0.9)',
                        titleColor: '#10b981',
                        bodyColor: '#d1fae5',
                        borderColor: '#10b981',
                        borderWidth: 1,
                        callbacks: {{
                            label: function(context) {{
                                const score = context.parsed.x;
                                const count = {json.dumps(counts)}[context.dataIndex];
                                return [
                                    'Score: ' + (score * 100).toFixed(1) + '%',
                                    'Questions: ' + count
                                ];
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        beginAtZero: true,
                        max: 1,
                        ticks: {{
                            color: '#d1fae5',
                            callback: function(value) {{
                                return (value * 100).toFixed(0) + '%';
                            }}
                        }},
                        grid: {{
                            color: 'rgba(16, 185, 129, 0.1)'
                        }}
                    }},
                    y: {{
                        ticks: {{
                            color: '#d1fae5'
                        }},
                        grid: {{
                            display: false
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Get the script's directory and go up to ai-trends-app folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(script_dir)

    filename = f"livebench_leaderboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(app_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Created HTML bar chart: {filename}")
    return filename


def main():
    """
    Main execution
    """
    print("="*80)
    print("🏆 LIVEBENCH VISUALIZER - Smart Trendz Theme")
    print("="*80)
    
    # Fetch data
    df, dataset_last_modified = fetch_livebench_data(offset=0, length=100)
    
    if df is None or df.empty:
        print("\n❌ Failed to fetch data")
        return
    
    # Aggregate scores
    model_avg, category_pivot = aggregate_model_scores(df)
    
    # Create visualizations
    print("\n" + "="*80)
    print("🎨 CREATING HTML VISUALIZATIONS")
    print("="*80)
    
    # Bar chart
    bar_file = create_html_bar_chart(model_avg, top_n=20, dataset_last_modified=dataset_last_modified)
    
    # Summary
    print("\n" + "="*80)
    print("✅ VISUALIZATION CREATED!")
    print("="*80)
    print(f"\n🌐 File created: {bar_file}")
    print("\n💡 The leaderboard will open automatically when you click the button in the dashboard!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()