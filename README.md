# 📈 Explorador de Tendencias de Búsqueda (Google Trends)

Esta aplicación web, desarrollada con [Streamlit](https://streamlit.io/) y [pytrends](https://github.com/GeneralMills/pytrends), permite consultar, visualizar y comparar el interés a lo largo del tiempo de una o varias palabras clave utilizando datos de Google Trends.

## 🚀 ¿Para qué sirve?

Con esta herramienta puedes:

- Consultar tendencias de búsqueda para una o varias palabras clave (hasta 5).
- Comparar el interés entre varios términos de búsqueda.
- Filtrar por país, rango de tiempo y categoría temática.
- Visualizar los datos en una gráfica y tabla interactiva.
- Exportar los resultados a un archivo PDF que incluye el gráfico y los datos en tabla.

Ideal para periodistas, investigadores, analistas de mercado, marketers o cualquier persona interesada en el análisis de tendencias online.

---

## 🛠️ Requisitos e instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/jcarranza71/GoogleTrendsBasico.git
cd GoogleTrendsBasico
```

### 2. Crear un entorno virtual (opcional pero recomendable)

```bash
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Si no tienes `requirements.txt`, instala manualmente:

```bash
pip install streamlit pytrends pandas matplotlib fpdf
```

---

## ▶️ Ejecución local

```bash
streamlit run app.py
```

---

## 🌍 Versión online

Puedes usar la app directamente en Streamlit Cloud:

👉 [Acceder a la app en línea](https://jcarranza71-googletrendsbasico.streamlit.app)

---

## ✏️ Uso

1. Escribe una o varias palabras clave (separadas por comas, máximo 5).
2. Selecciona país, rango de tiempo y categoría.
3. Pulsa el botón 🔍 **Buscar**.
4. Visualiza los datos en gráfica y tabla.
5. Opcionalmente, pulsa 📄 **Exportar a PDF** para descargar un informe.

---

## 🧾 Ejemplo

```plaintext
Palabras clave: Messi, Ronaldo, Mbappé
País: España
Rango: últimos 12 meses
Categoría: Deportes
```

---

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y compartirlo libremente.

---

## 🙌 Autor

Desarrollado por [Jesús Carranza](https://github.com/jcarranza71).
