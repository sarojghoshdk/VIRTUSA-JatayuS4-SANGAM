from flask import request, session, jsonify, render_template
import smtplib, os
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template

def send_fd_result_email():
    try:
        recipient = request.form['email']
        # Get data from session
        name = session.get('customer_name', 'Customer')
        cid = session.get('customer_id', 'N/A')
        interest_rate = session.get('interest_rate', 'N/A')
        pos_reasons = session.get('positive_reasons', [])
        neg_reasons = session.get('negative_reasons', [])

        subject = f"FD Interest Rate Prediction for {name}"

        summary_table = session.get('summary_table', [])
        total_score = session.get('total_score', 0)
        favorability = session.get('favorability', '0.00%')
        profile_status = session.get('profile_status', 'Unknown')

        # Render HTML from template
        html_content = render_template(
            'email_template.html',
            name=name,
            cid=cid,
            interest_rate=interest_rate,
            pos_reasons=pos_reasons,
            neg_reasons=neg_reasons,
            summary_table=summary_table,
            total_score=total_score,
            favorability=favorability,
            profile_status=profile_status
        )

        # Fallback plain text
        plain_body = f"""Hello {name},

Here are your FD Interest Rate Prediction details:

- Customer ID: {cid}
- Predicted Interest Rate: {interest_rate}

✅ Favorable Factors:
{chr(10).join(['- ' + reason for reason in pos_reasons])}

❌ Unfavorable Factors:
{chr(10).join(['- ' + reason for reason in neg_reasons])}

Regards,
FD Prediction Team
"""

        # Email setup
        sender_email = "ecesarojghoshdk@gmail.com"
        sender_password = "vehr eanq ewdj hcbd"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient

        # Add text and HTML versions
        msg.attach(MIMEText(plain_body, 'plain'))

        # Add HTML with embedded images
        related_part = MIMEMultipart('related')
        related_part.attach(MIMEText(html_content, 'html'))

        for cid, path in [('reasoning_chart', 'app/static/reasoning_chart.png'), ('reason_distribution_chart', 'static/reason_distribution_chart.png')]:
            if os.path.exists(path):
                with open(path, 'rb') as img:
                    mime_img = MIMEBase('image', 'png', name=os.path.basename(path))
                    mime_img.add_header('Content-ID', f'<{cid}>')
                    mime_img.add_header('Content-Disposition', 'inline', filename=os.path.basename(path))
                    mime_img.set_payload(img.read())
                    encoders.encode_base64(mime_img)
                    related_part.attach(mime_img)

        msg.attach(related_part)

        # Attach additional charts
        for filename in ['static/gauge_chart.png', 'static/trend_chart.png', 'static/comparison_chart.png']:
            if os.path.exists(filename):
                with open(filename, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(filename)}')
                    msg.attach(part)

        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return jsonify({'success': True, 'message': '✅ Result email sent successfully!'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Failed to send email: {e}'})

def send_loan_result_email():
    try:
        recipient = request.form['email']
        name = session.get('customer_name', 'Customer')
        cid = session.get('customer_id', 'N/A')
        eligible = session.get('eligible', 'No')
        interest_rate = session.get('interest_rate', 'N/A')
        max_loan = session.get('max_loan', 'N/A')
        reasons_table = session.get('reasons_table', [])
        suggestions = session.get('suggestions', []) if eligible != "Yes" else []

        subject = f"Loan Evaluation Report for {name}"

        image_paths = [
            ('numerical_impact', 'app/static/numerical_impact_chart.png'),
        ]

        html_body = render_template(
            'loan_email_template.html',
            name=name,
            cid=cid,
            eligible=eligible,
            interest_rate=interest_rate,
            max_loan=max_loan,
            reasons_table=reasons_table,
            suggestions=suggestions,
            image_cids=[cid for cid, _ in image_paths]
        )

        plain_text = f"""Hi {name},

Loan Evaluation Report:
- Eligibility: {eligible}
- Interest Rate: {interest_rate}%
- Maximum Loan Amount: ₹{max_loan}

Regards,
Loan Evaluation Team
"""
        sender_email = "ecesarojghoshdk@gmail.com"
        sender_password = "vehr eanq ewdj hcbd"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient

        msg.attach(MIMEText(plain_text, 'plain'))

        related = MIMEMultipart('related')
        related.attach(MIMEText(html_body, 'html'))

        for cid, path in image_paths:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    img = MIMEBase('image', 'png', name=os.path.basename(path))
                    img.add_header('Content-ID', f'<{cid}>')
                    img.add_header('Content-Disposition', 'inline', filename=os.path.basename(path))
                    img.set_payload(f.read())
                    encoders.encode_base64(img)
                    related.attach(img)

        msg.attach(related)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return jsonify({'success': True, 'message': '✅ Loan report sent successfully!'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Failed to send loan report: {e}'})
#------------------------------------------
