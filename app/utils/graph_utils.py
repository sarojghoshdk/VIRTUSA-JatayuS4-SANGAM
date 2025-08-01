# app/utils/graph_utils.py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64


def generate_loan_graph(loan_amount, interest_payable, total_repayment, output_file='app/static/repayment_graph/loan_graph.png'):
    fig, ax = plt.subplots(figsize=(8, 8))

    # Data for the graph
    labels = ['Interest Payable', 'Loan Amount']
    sizes = [interest_payable, loan_amount]
    colors = ['#007bff', '#ff6600']

    # Plotting donut chart
    wedges, _ = ax.pie(sizes, labels=labels, colors=colors, startangle=140, wedgeprops={'width': 0.3})

    # Center text for total repayment
    ax.text(0, 0.15, 'Total Re-payment', ha='center', va='center', fontsize=14, color='#555')
    ax.text(0, -0.1, f'₹ {total_repayment:,.0f}', ha='center', va='center', fontsize=24, fontweight='bold', color='#000')

    # Legend
    ax.legend(wedges, labels, title="Legend", loc="lower left", bbox_to_anchor=(1, 0, 0.5, 1))

    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
    plt.tight_layout()

    # Save the graph as an image
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
