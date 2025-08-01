import os
import base64
import numpy as np
import matplotlib.pyplot as plt

def create_loan_graphs(data, result, graph_dir="app/static/loan_graphs", impact_chart_path="app/static/numerical_impact_chart.png"):
    os.makedirs(graph_dir, exist_ok=True)

    graph_data = {
        "Credit History": data["Credit_History"],
        "Family Credit History": data["Family_Credit_History"],
        "Risk Rating": data["Risk_Rating"],
        "Age": data["Age"],
        "Customer Relationship": data["Customer_Relationship_Years"],
        "Past Transactions": 1 if data["Past_Transactions"] == "Positive" else 0,
        "Market Trends": {"Favorable": 2, "Neutral": 1, "Unfavorable": 0}.get(data["Market_Trends"], 0)
    }

    # --- Customer Profile Parameters Bar Chart ---
    plt.figure(figsize=(10, 6))
    labels, values = list(graph_data.keys()), list(graph_data.values())
    plt.barh(labels, values, color='royalblue', alpha=0.85)
    for i, v in enumerate(values):
        plt.text(v + 0.1, i, str(v), color='black', fontsize=12, va='center')
    plt.title("Customer Profile Parameters", fontsize=16)
    bar_chart_path = os.path.join(graph_dir, "customer_profile_chart.png")
    plt.savefig(bar_chart_path)
    plt.close()

    # --- Donut Chart for Eligibility ---
    eligibility_status = "Eligible for Loan" if result['eligible'].lower() == "yes" else "Not Eligible for Loan"
    eligibility_color = '#006600' if result['eligible'].lower() == "yes" else '#800000'
    plt.figure(figsize=(8, 8))
    wedges, texts = plt.pie(
        [1],
        labels=[eligibility_status],
        colors=[eligibility_color],
        startangle=90,
        wedgeprops={'linewidth': 2, 'edgecolor': 'black'}
    )
    plt.gca().add_artist(plt.Circle((0, 0), 0.6, color='white'))
    plt.title(f"Loan Eligibility: {eligibility_status}", fontsize=16)
    donut_chart_path = os.path.join(graph_dir, "loan_eligibility_chart.png")
    plt.savefig(donut_chart_path)
    plt.close()

    # --- Loan Distribution Pie Chart ---
    plt.figure(figsize=(8, 8))
    plt.pie([60, 30, 10], labels=["Principal", "Interest", "Other Charges"],
            autopct='%1.1f%%', startangle=140,
            colors=['#4CAF50', '#FF9800', '#E91E63'],
            wedgeprops={'edgecolor': 'black'})
    plt.title('Loan Distribution Pie Chart')
    loan_pie_chart_path = os.path.join(graph_dir, "loan_pie_chart.png")
    plt.savefig(loan_pie_chart_path)
    plt.close()

    # --- Risk & Relationship Trends Line Chart ---
    plt.figure(figsize=(10, 6))
    x = ["Credit History", "Risk Rating", "Customer Relationship", "Age"]
    y = [data["Credit_History"], data["Risk_Rating"], data["Customer_Relationship_Years"], data["Age"]]
    plt.plot(x, y, marker='o', color='orange')
    plt.title("Risk & Relationship Trends")
    risk_relationship_path = os.path.join(graph_dir, "risk_relationship_chart.png")
    plt.savefig(risk_relationship_path)
    plt.close()

    # --- Loan Interest Rate Trend ---
    plt.figure(figsize=(10, 6))
    market_rates = [6.5, 6.7, 6.9, 7.2, 7.5, result["interest_rate"]]
    time = ['2019', '2020', '2021', '2022', '2023', '2024']
    plt.plot(time, market_rates, marker='o', color='royalblue', linewidth=2)
    plt.fill_between(time, market_rates, color='skyblue', alpha=0.3)
    plt.title("Loan Interest Rate Trend")
    interest_trend_path = os.path.join(graph_dir, "interest_trend.png")
    plt.savefig(interest_trend_path)
    plt.close()

    # --- Loan Amount Bar Chart ---
    plt.figure(figsize=(8, 6))
    bars = plt.bar(["Loan Amount"], [result["max_loan"]], color="#4CAF50", edgecolor='black')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f"₹{yval:,.2f}", ha='center', fontsize=12)
    plt.title("Eligible Loan Amount")
    loan_bar_chart_path = os.path.join(graph_dir, "loan_bar_chart.png")
    plt.savefig(loan_bar_chart_path)
    plt.close()

    # --- Scatter Plot ---
    scatter_x = np.array(["Past Transactions", "Market Trends"])
    scatter_y = np.array([
        1 if data["Past_Transactions"] == "Positive" else 0,
        {"Favorable": 2, "Neutral": 1, "Unfavorable": 0}.get(data["Market_Trends"], 0)
    ])
    plt.figure(figsize=(8, 6))
    plt.scatter(scatter_x, scatter_y, s=200, c='royalblue', edgecolors='black')
    plt.title("Past Transactions vs. Market Trends")
    scatter_path = os.path.join(graph_dir, "past_transactions_trends_chart.png")
    plt.savefig(scatter_path)
    plt.close()

    # --- Encode Impact Chart as Base64 ---
    with open(impact_chart_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    return {
        "bar_chart_path": bar_chart_path,
        "donut_chart_path": donut_chart_path,
        "loan_pie_chart_path": loan_pie_chart_path,
        "risk_relationship_path": risk_relationship_path,
        "interest_trend_path": interest_trend_path,
        "loan_bar_chart_path": loan_bar_chart_path,
        "scatter_plot_path": scatter_path,
        "bar_chart_base64": encoded_image
    }
