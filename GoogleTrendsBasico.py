# archivo: app.py
# instalar: pip install streamlit pytrends pandas matplotlib fpdf

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import tempfile
from datetime import datetime
from fpdf import FPDF
from pytrends.request import TrendReq

# 👉 Reinicio total (antes de widgets)
if st.session_state.get("reset_app", False):
    st.session_state.clear()
    st.rerun()

# Configuración inicial
st.set_page_config(page_title="Tendencias de Google", layout="centered")
st.markdown("""
    <div style='text-align: center;'>
        <div style='font-size: 70px;'>📈</div>
        <h1 style='margin-top: 0; font-size: 40px;'>Explorador de Tendencias de Búsqueda<br>(Google Trends)</h1>
    </div>
""", unsafe_allow_html=True)



# Diccionario de países (ISO)
PAISES = {
    "Global": "", "Argentina": "AR", "Australia": "AU", "Austria": "AT", "Bélgica": "BE",
    "Brasil": "BR", "Canadá": "CA", "Chile": "CL", "Colombia": "CO", "República Checa": "CZ",
    "Dinamarca": "DK", "Egipto": "EG", "Finlandia": "FI", "Francia": "FR", "Alemania": "DE",
    "Grecia": "GR", "Hong Kong": "HK", "Hungría": "HU", "India": "IN", "Indonesia": "ID",
    "Irlanda": "IE", "Israel": "IL", "Italia": "IT", "Japón": "JP", "Corea del Sur": "KR",
    "Malasia": "MY", "México": "MX", "Países Bajos": "NL", "Nueva Zelanda": "NZ", "Noruega": "NO",
    "Polonia": "PL", "Portugal": "PT", "Rumanía": "RO", "Rusia": "RU", "Arabia Saudita": "SA",
    "Singapur": "SG", "Sudáfrica": "ZA", "España": "ES", "Suecia": "SE", "Suiza": "CH",
    "Taiwán": "TW", "Tailandia": "TH", "Turquía": "TR", "Ucrania": "UA", "Emiratos Árabes Unidos": "AE",
    "Reino Unido": "GB", "Estados Unidos": "US", "Venezuela": "VE"
}

# Clase PDF con pie de página
class PDFConPie(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        fecha = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 10, f"Exportado el {fecha} | Autor: JESÚS CARRANZA", align="C")

# Inputs
if "keyword_val" not in st.session_state:
    st.session_state["keyword_val"] = ""

keyword = st.text_input("Introduce una palabra clave:", value=st.session_state["keyword_val"], key="keyword_input")

geo_legible = st.selectbox("🌍 País", list(PAISES.keys()), index=list(PAISES.keys()).index("España"))
geo = PAISES[geo_legible]

rango_legible = st.selectbox("📅 Rango de tiempo", [
    "últimos 12 meses", "últimos 6 meses", "últimos 3 meses", "último mes"
], index=0)

timeframe_map = {
    "últimos 12 meses": "today 12-m",
    "últimos 6 meses": "today 6-m",
    "últimos 3 meses": "today 3-m",
    "último mes": "today 1-m"
}
timeframe = timeframe_map[rango_legible]

# Buscar tendencias
if st.button("Buscar") and keyword:
    with st.spinner("🔄 Consultando Google Trends..."):
        pytrends = TrendReq(hl='es-ES', tz=360)
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo)
        df = pytrends.interest_over_time()

    if not df.empty:
        df_clean = df.drop(columns=["isPartial"], errors="ignore")
        st.session_state["df"] = df_clean
        st.session_state["keyword_val"] = keyword
        st.session_state["geo"] = geo_legible
        st.session_state["rango"] = rango_legible
        st.session_state["descarga_realizada"] = False

        st.success("✅ Datos encontrados")
        st.subheader("📊 Interés a lo largo del tiempo")
        st.line_chart(df_clean[keyword])

        st.subheader("📋 Datos en tabla")
        st.dataframe(df_clean.reset_index())
    else:
        st.warning("❌ No se encontraron datos para esta palabra clave.")
        st.session_state.clear()

# Exportar PDF
if all(k in st.session_state for k in ["df", "keyword_val", "geo", "rango"]) and not st.session_state.get("descarga_realizada", False):
    if st.button("📄 Exportar gráfico + tabla a PDF"):
        with st.spinner("📄 Generando PDF..."):
            df_export = st.session_state["df"]
            keyword_export = st.session_state["keyword_val"]
            geo_export = st.session_state["geo"]
            rango_export = st.session_state["rango"]

            fig, ax = plt.subplots()
            df_export.reset_index().plot(x="date", y=keyword_export, ax=ax, legend=False)
            ax.set_title(f"Tendencia: {keyword_export}")
            ax.set_ylabel("Interés")
            ax.set_xlabel("Fecha")
            temp_image = os.path.join(tempfile.gettempdir(), "grafico.png")
            fig.savefig(temp_image, bbox_inches='tight')
            plt.close(fig)

            pdf = PDFConPie()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Tendencia de búsqueda: {keyword_export}", ln=True, align="C")
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 10, f"País: {geo_export} | Rango: {rango_export}", ln=True, align="C")
            pdf.image(temp_image, x=10, y=40, w=190)

            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Datos de búsqueda: {keyword_export}", ln=True)
            pdf.ln(5)

            col_widths = [60, 40]
            table_width = sum(col_widths)
            page_width = pdf.w - 2 * pdf.l_margin
            x_start = (page_width - table_width) / 2 + pdf.l_margin

            pdf.set_x(x_start)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(col_widths[0], 10, "Fecha", border=1, align="C")
            pdf.cell(col_widths[1], 10, "Interés", border=1, align="C")
            pdf.ln()

            pdf.set_font("Arial", "", 10)
            for _, row in df_export.reset_index().iterrows():
                date_str = row["date"].strftime("%Y-%m-%d")
                value = row[keyword_export]
                pdf.set_x(x_start)
                pdf.cell(col_widths[0], 8, date_str, border=1, align="C")
                pdf.cell(col_widths[1], 8, str(value), border=1, align="C")
                pdf.ln()

            pdf_path = os.path.join(tempfile.gettempdir(), "tendencia_export.pdf")
            pdf.output(pdf_path)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=f.read(),
                    file_name=f"{keyword_export}_tendencia.pdf",
                    mime="application/pdf",
                    key="download_pdf",
                    on_click=lambda: st.session_state.update({"descarga_realizada": True})
                )

# Mensaje final
if st.session_state.get("descarga_realizada", False):
    st.success("✅ El PDF se ha descargado correctamente.")
    if st.button("Aceptar"):
        st.session_state["reset_app"] = True
        st.rerun()
