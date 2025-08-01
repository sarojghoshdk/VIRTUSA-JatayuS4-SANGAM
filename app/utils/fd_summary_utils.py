import numpy as np
def generate_summary_table(data):
    positive_reasons = []
    negative_reasons = []

    if data["Credit_History"] >= 800:
        positive_reasons.append("Excellent credit history, indicating strong financial discipline.")
    elif data["Credit_History"] >= 500:
        positive_reasons.append("Good credit history with minor issues.")
    else:
        negative_reasons.append("Low credit history, considered a risk factor.")

    if data["Risk_Rating"] <= 10:
        positive_reasons.append("Low risk rating, considered a safe investor.")
    elif data["Risk_Rating"] <= 30:
        positive_reasons.append("Moderate risk rating, acceptable for investment.")
    else:
        negative_reasons.append("High risk rating, may reduce interest rate benefits.")

    if data["Age"] <= 30:
        positive_reasons.append("Young investor, potentially longer investment horizon.")
    elif data["Age"] <= 60:
        positive_reasons.append("Middle-aged investor with steady financial behavior.")
    else:
        positive_reasons.append("Senior citizen, eligible for higher interest rates in some cases.")

    if data["Customer_Relationship_Years"] >= 10:
        positive_reasons.append("Long-term relationship with the bank.")
    else:
        negative_reasons.append("Relatively new customer.")

    if data["Past_Transactions"] == "Positive":
        positive_reasons.append("Positive transaction history indicating good account management.")
    else:
        negative_reasons.append("Negative transaction history may affect trust level.")

    if data["Market_Trends"] == "Favorable":
        positive_reasons.append("Favorable market trends contribute to better FD rates.")
    elif data["Market_Trends"] == "Neutral":
        positive_reasons.append("Neutral market trends have a balanced effect.")
    else:
        negative_reasons.append("Unfavorable market trends may limit the interest rate.")

    reason_to_parameter = {
        "Excellent credit history, indicating strong financial discipline.": "Credit History",
        "Good credit history with minor issues.": "Credit History",
        "Low credit history, considered a risk factor.": "Credit History",

        "Low risk rating, considered a safe investor.": "Risk Rating",
        "Moderate risk rating, acceptable for investment.": "Risk Rating",
        "High risk rating, may reduce interest rate benefits.": "Risk Rating",

        "Young investor, potentially longer investment horizon.": "Age",
        "Middle-aged investor with steady financial behavior.": "Age",
        "Senior citizen, eligible for higher interest rates in some cases.": "Age",

        "Long-term relationship with the bank.": "Customer Relationship Years",
        "Relatively new customer.": "Customer Relationship Years",

        "Positive transaction history indicating good account management.": "Past Transactions",
        "Negative transaction history may affect trust level.": "Past Transactions",

        "Favorable market trends contribute to better FD rates.": "Market Trends",
        "Neutral market trends have a balanced effect.": "Market Trends",
        "Unfavorable market trends may limit the interest rate.": "Market Trends"
    }

    is_new_customer = (
        data["Credit_History"] == 0 and 
        data["Risk_Rating"] == 0 and 
        data["Customer_Relationship_Years"] == 0
    )

    summary_table = []
    for reason in positive_reasons:
        parameter = reason_to_parameter.get(reason, "Unknown")
        score = '0' if is_new_customer and parameter in ['Credit History', 'Risk Rating', 'Customer Relationship Years'] else '+1'
        summary_table.append({'parameter': parameter, 'reason': reason, 'score': score})

    for reason in negative_reasons:
        parameter = reason_to_parameter.get(reason, "Unknown")
        score = '0' if is_new_customer and parameter in ['Credit History', 'Risk Rating', 'Customer Relationship Years'] else '-1'
        summary_table.append({'parameter': parameter, 'reason': reason, 'score': score})

    total_score = sum(
        1 if row['score'] == '+1' else (-1 if row['score'] == '-1' else 0)
        for row in summary_table
    )

    positive_count = sum(1 for row in summary_table if row['score'] == '+1')
    negative_count = sum(1 for row in summary_table if row['score'] == '-1')
    total_factors = len(positive_reasons) + len(negative_reasons)
    favorability = (positive_count / total_factors) * 100 if (positive_count + negative_count) != 0 else 0

    if favorability >= 70:
        overall_profile = "Excellent"
    elif favorability >= 50:
        overall_profile = "Good"
    elif favorability >= 30:
        overall_profile = "Average"
    else:
        overall_profile = "Poor"

    return positive_reasons, negative_reasons, summary_table, total_score, favorability, overall_profile
