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
from pytrends.exceptions import TooManyRequestsError

# 👉 Reinicio total (antes de widgets)
if st.session_state.get("reset_app", False):
    st.session_state.clear()
    st.rerun()

# Configuración inicial
st.set_page_config(page_title="Tendencias en Google", page_icon="📈", layout="centered")
st.markdown("""
    <div style='text-align: center;'>
        <div style='font-size: 70px;'>📈</div>
        <h1 style='margin-top: 0; font-size: 40px;'>Explorador de Tendencias de Búsqueda<br>(Google Trends)</h1>
    </div>
""", unsafe_allow_html=True)

# Diccionario de países (ordenado)
PAISES = {
    "Global": "",
    **dict(sorted({
        "Alemania": "DE", "Arabia Saudita": "SA", "Argentina": "AR", "Australia": "AU", "Austria": "AT",
        "Bélgica": "BE", "Brasil": "BR", "Canadá": "CA", "Chile": "CL", "Colombia": "CO",
        "Corea del Sur": "KR", "Dinamarca": "DK", "Egipto": "EG", "Emiratos Árabes Unidos": "AE",
        "España": "ES", "Estados Unidos": "US", "Finlandia": "FI", "Francia": "FR", "Grecia": "GR",
        "Hong Kong": "HK", "Hungría": "HU", "India": "IN", "Indonesia": "ID", "Irlanda": "IE",
        "Israel": "IL", "Italia": "IT", "Japón": "JP", "Malasia": "MY", "México": "MX",
        "Noruega": "NO", "Nueva Zelanda": "NZ", "Países Bajos": "NL", "Polonia": "PL",
        "Portugal": "PT", "Reino Unido": "GB", "República Checa": "CZ", "Rumanía": "RO",
        "Rusia": "RU", "Singapur": "SG", "Sudáfrica": "ZA", "Suecia": "SE", "Suiza": "CH",
        "Tailandia": "TH", "Taiwán": "TW", "Turquía": "TR", "Ucrania": "UA", "Venezuela": "VE"
    }.items()))
}

# Diccionario de categorías (ordenado)
CATEGORIAS = {
    "Todas": 0,
    **dict(sorted({
        "Aficiones y tiempo libre": 11,
        "Alimentos y bebidas": 71,
        "Arte y entretenimiento": 3,
        "Automóviles y vehículos": 47,
        "Belleza y fitness": 44,
        "Bienes raíces": 29,
        "Ciencia": 174,
        "Compras": 18,
        "Deportes": 20,
        "Finanzas": 7,
        "Hogar y jardín": 19,
        "Internet y telecomunicaciones": 13,
        "Juegos": 8,
        "Ley y gobierno": 14,
        "Libros y literatura": 22,
        "Mascotas y animales": 66,
        "Negocios e industria": 12,
        "Noticias": 16,
        "Ordenadores y electrónica": 5,
        "Personas y sociedad": 24,
        "Referencia": 533,
        "Salud": 45,
        "Viajes": 67
    }.items()))
}

# Clase PDF con pie de página
class PDFConPie(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        fecha = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 10, f"Exportado el {fecha}", align="C")

# Inputs
if "keyword_val" not in st.session_state:
    st.session_state["keyword_val"] = ""

st.markdown("💡 Puedes comparar múltiples palabras clave separándolas por comas (máximo 5). Ejemplo: `Burger, pizza, sushi`")

keyword = st.text_input("Introduce una o varias palabras clave:", value=st.session_state["keyword_val"], key="keyword_input")

# Selectores en una sola fila
with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        geo_legible = st.selectbox("🌍 País", list(PAISES.keys()), index=0)
        geo = PAISES[geo_legible]

    with col2:
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

    with col3:
        categoria_legible = st.selectbox("📚 Categoría", list(CATEGORIAS.keys()), index=0)
        categoria = CATEGORIAS[categoria_legible]

# Botón buscar centrado
st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
buscar = st.button("🔍 Buscar")
st.markdown("</div>", unsafe_allow_html=True)

# Buscar tendencias
if buscar:
    keywords = [kw.strip() for kw in keyword.split(",") if kw.strip()]
    if not keywords:
        st.warning("⚠️ Por favor, introduce al menos una palabra clave.")
    elif len(keywords) > 5:
        st.warning("⚠️ Solo puedes comparar hasta 5 palabras clave.")
    else:
        with st.spinner("🔄 Consultando Google Trends..."):
            try:
                pytrends = TrendReq(hl='es-ES', tz=360)
                pytrends.build_payload(keywords, cat=categoria, timeframe=timeframe, geo=geo)
                df = pytrends.interest_over_time()
            except TooManyRequestsError:
                st.error("🚫 Has realizado demasiadas consultas en poco tiempo. Google ha bloqueado temporalmente las peticiones.\n\n🔁 Espera unos minutos y vuelve a intentarlo.")
                st.stop()
            except Exception as e:
                st.error(f"❌ Ocurrió un error inesperado: {str(e)}")
                st.stop()

        if not df.empty:
            df_clean = df.drop(columns=["isPartial"], errors="ignore")
            st.session_state["df"] = df_clean
            st.session_state["keyword_val"] = keyword
            st.session_state["geo"] = geo_legible
            st.session_state["rango"] = rango_legible
            st.session_state["categoria"] = categoria_legible
            st.session_state["descarga_realizada"] = False

            st.success("✅ Datos encontrados")
            st.subheader("📊 Interés a lo largo del tiempo")
            st.line_chart(df_clean[keywords])

            st.subheader("📋 Datos en tabla")
            st.dataframe(df_clean.reset_index())
        else:
            st.warning("❌ No se encontraron datos para esas palabras clave.")
            st.session_state.clear()

# Exportar PDF
if all(k in st.session_state for k in ["df", "keyword_val", "geo", "rango", "categoria"]) and not st.session_state.get("descarga_realizada", False):
    if st.button("📄 Exportar gráfico + tabla a PDF"):
        with st.spinner("📄 Generando PDF..."):
            df_export = st.session_state["df"]
            keyword_export = st.session_state["keyword_val"]
            geo_export = st.session_state["geo"]
            rango_export = st.session_state["rango"]
            categoria_export = st.session_state["categoria"]

            fig, ax = plt.subplots()
            df_export.reset_index().plot(x="date", y=[kw.strip() for kw in keyword_export.split(",")], ax=ax)
            ax.set_title(f"Tendencias de búsqueda")
            ax.set_ylabel("Interés")
            ax.set_xlabel("Fecha")
            temp_image = os.path.join(tempfile.gettempdir(), "grafico.png")
            fig.savefig(temp_image, bbox_inches='tight')
            plt.close(fig)

            pdf = PDFConPie()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.multi_cell(0, 10, f"Tendencias de búsqueda: {keyword_export}", align="C")
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 10, f"País: {geo_export} | Rango: {rango_export}", ln=True, align="C")
            pdf.cell(0, 10, f"Categoría: {categoria_export}", ln=True, align="C")
            pdf.image(temp_image, x=10, y=50, w=190)

            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Datos de búsqueda: {keyword_export}", ln=True)
            pdf.ln(5)

            headers = ["Fecha"] + [kw.strip() for kw in keyword_export.split(",")]
            col_width = 190 / len(headers)

            pdf.set_font("Arial", "B", 10)
            for h in headers:
                pdf.cell(col_width, 8, h, border=1, align="C")
            pdf.ln()

            pdf.set_font("Arial", "", 9)
            for _, row in df_export.reset_index().iterrows():
                pdf.cell(col_width, 8, row["date"].strftime("%Y-%m-%d"), border=1, align="C")
                for kw in headers[1:]:
                    pdf.cell(col_width, 8, str(row.get(kw, "")), border=1, align="C")
                pdf.ln()

            pdf_path = os.path.join(tempfile.gettempdir(), "tendencia_export.pdf")
            pdf.output(pdf_path)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=f.read(),
                    file_name="tendencias.pdf",
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
