import pandas as pd
from fpdf import FPDF, XPos, YPos
import os

ARCHIVO_EXCEL = r'C:\BUSQUEDA_SECOP\INTELIGENCIA_INDECAP_20260319.xlsx'
ARCHIVO_PDF = r'C:\BUSQUEDA_SECOP\REPORTE_EJECUTIVO_PRO.pdf'

def safe_text(txt):
    return str(txt).encode('latin-1', 'replace').decode('latin-1')

class PDF(FPDF):
    def header(self):
        self.set_fill_color(31, 119, 180)
        self.rect(0, 0, 210, 30, 'F')
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'INFORME ESTRATEGICO DE LICITACIONES VIP', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 10, f'Generado para INDECAP - {pd.Timestamp.now().strftime("%Y-%m-%d")}', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

    def chapter_title(self, label):
        self.set_font('helvetica', 'B', 14)
        self.set_fill_color(230, 230, 230)
        self.set_text_color(31, 119, 180)
        self.cell(0, 10, f" SECCION: {label}", border=0, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

try:
    df = pd.read_excel(ARCHIVO_EXCEL, sheet_name='ATACAR_YA')
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Agrupar por categoría para el PDF
    categorias = df['Categoria'].unique()
    
    for cat in categorias:
        pdf.add_page()
        pdf.chapter_title(cat)
        
        df_cat = df[df['Categoria'] == cat].head(10) # Top 10 por categoría
        
        for i, row in df_cat.iterrows():
            pdf.set_font('helvetica', 'B', 10)
            pdf.set_text_color(0, 0, 0)
            
            # Encabezado del contrato
            entidad = safe_text(row['Entidad'])[:55]
            valor = f"${row['Presupuesto']:,.0f}"
            score = f"SCORE: {row['Match_Score']}/10"
            
            pdf.set_fill_color(245, 245, 245)
            pdf.cell(110, 8, f" {entidad}", border=1, fill=True)
            pdf.cell(40, 8, score, border=1, fill=True, align='C')
            pdf.cell(40, 8, valor, border=1, fill=True, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Objeto y Ubicación
            pdf.set_font('helvetica', '', 9)
            pdf.multi_cell(190, 6, f"OBJETO: {safe_text(row['Objeto'])[:180]}...", border=1)
            pdf.set_font('helvetica', 'I', 8)
            pdf.cell(190, 6, f"Ubicacion: {safe_text(row['Municipio'])} | Cierra en: {row['Dias_Cierre']} dias", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)

    pdf.output(ARCHIVO_PDF)
    print(f"✅ REPORTE PDF CATEGORIZADO GENERADO: {ARCHIVO_PDF}")

except Exception as e:
    print(f"❌ Error: {e}")