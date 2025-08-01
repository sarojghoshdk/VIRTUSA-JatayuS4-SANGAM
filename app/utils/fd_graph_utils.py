import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_fd_graphs(interest_rate, summary_table):
    # Scoring Distribution by Parameter
    param_scores = {}
    for row in summary_table:
        param = row['parameter']
        score = 1 if row['score'] == '+1' else (-1 if row['score'] == '-1' else 0)
        param_scores[param] = param_scores.get(param, 0) + score

    parameters = list(param_scores.keys())
    scores = list(param_scores.values())
    palette = ['#1E88E5' if s > 0 else '#EF5350' for s in scores]
    sns.set(style='white')
    plt.figure(figsize=(10, 6))
    bars = plt.bar(parameters, scores, color=palette, width=0.6)
    plt.xlabel("Parameter", fontsize=12)
    plt.ylabel("Score", fontsize=12)
    plt.title("Scoring Distribution by Parameter", fontsize=14, fontweight='bold')
    plt.ylim(-1.2, 1.2)
    plt.yticks([-1, 0, 1])
    plt.xticks(rotation=45, ha='right')

    for bar in bars:
        yval = bar.get_height()
        if yval != 0:
            plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05 * (1 if yval > 0 else -1), f'{yval:+}',
                     ha='center', va='bottom' if yval > 0 else 'top', fontsize=10, fontweight='bold')

    plt.axhline(0, color='gray', linewidth=1)
    plt.tight_layout()
    plt.savefig('app/static/reasoning_chart.png', dpi=900)
    plt.close()

    # Radial Gauge Chart
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ['#ff4d4d', '#ffa500', '#4CAF50']
    labels = ['Low Rate', 'Medium Rate', 'High Rate']
    ax.pie([1, 1, 1], colors=colors, labels=labels, startangle=180, counterclock=False,
           wedgeprops={'linewidth': 2, 'edgecolor': 'white'})
    theta = np.pi * (1 - (interest_rate / 10))
    x, y = np.cos(theta), np.sin(theta)
    ax.arrow(0, 0, x * 0.7, y * 0.7, head_width=0.12, head_length=0.25, fc='white', ec='white', linewidth=4, alpha=1)
    ax.text(0, 0, f"{interest_rate:.2f}%", ha='center', va='center', fontsize=24, fontweight='bold', color='black')
    plt.title('FD Interest Rate Gauge', fontsize=18, fontweight='bold', color='#333')
    plt.axis('off')
    plt.savefig('app/static/fd_graphs/gauge_chart.png')
    plt.close()

    # Interest Rate Trend
    past_rates = [6.5, 7.0, 7.2, 7.8, 8.0, interest_rate]
    time_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Prediction']
    plt.figure(figsize=(12, 6))
    plt.plot(time_labels, past_rates, marker='o', color='#4CAF50', linewidth=3, label='FD Rate Trend')
    plt.fill_between(time_labels, past_rates, color='#90EE90', alpha=0.3)
    for i, rate in enumerate(past_rates):
        plt.text(i, rate + 0.05, f"{rate:.2f}%", ha='center', va='bottom', fontsize=10, color='#333')
    plt.title('FD Interest Rate Trend Over Time', fontsize=18, fontweight='bold', color='#333')
    plt.xlabel('Time Period', fontsize=14)
    plt.ylabel('Interest Rate (%)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.savefig('app/static/fd_graphs/trend_chart.png')
    plt.close()

    # Comparison Chart
    plt.figure(figsize=(8, 5))
    plt.bar(['Customer Rate', 'Market Avg. Rate'], [interest_rate, 7.5], color=['#4CAF50', '#FF9800'])
    plt.title('Customer vs. Market Rate', fontsize=16)
    plt.ylabel('Interest Rate (%)')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.savefig('app/static/fd_graphs/comparison_chart.png')
    plt.close()

    # Customer Profile Pie Chart
    contribution = {'Credit History': 40, 'Risk Rating': 30, 'Customer Relationship': 20, 'Market Trends': 10}
    plt.figure(figsize=(7, 7))
    plt.pie(contribution.values(), labels=contribution.keys(), autopct='%1.1f%%', startangle=140,
            colors=sns.color_palette('pastel'))
    plt.title('Customer Profile Contribution', fontsize=16)
    plt.savefig('app/static/fd_graphs/pie_chart.png')
    plt.close()
