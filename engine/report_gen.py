from fpdf import FPDF

def create_pdf_report(gaps, humanized, cover_letter):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Career Optimization Report", 0, 1, 'C')
    pdf.ln(10)
    
    sections = [("Detailed Gaps Analysis", gaps), ("Optimized STAR Projects", humanized), ("Tailored Cover Letter", cover_letter)]
    for title, body in sections:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, title, 0, 1)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 8, body.encode('latin-1', 'ignore').decode('latin-1'))
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')