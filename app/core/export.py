from fpdf import FPDF
from .analysis import sales_summary

def export_report(filename="sales_report.pdf"):
    summary = sales_summary()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Sales Report", ln=True, align="C")

    for region, row in summary.iterrows():
        pdf.cell(200, 10, txt=f"{region}: Quantity={row['quantity']}, Price={row['price']}", ln=True)

    pdf.output(filename)
    print(f"✅ Report saved as {filename}")
