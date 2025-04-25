import streamlit as st

st.markdown("""
    <style>
    .logo-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 300px;
    }

    @media (prefers-color-scheme: dark) {
        .logo-light { display: none; }
        .logo-dark { display: block; }
    }

    @media (prefers-color-scheme: light) {
        .logo-light { display: block; }
        .logo-dark { display: none; }
    }
    </style>

    <div>
        <img src="Igloo Original.png" class="logo-img logo-light">
        <img src="Igloo White.png" class="logo-img logo-dark">
    </div>
""", unsafe_allow_html=True)

st.markdown("""
# Bienvenido al Cotizador de Rutas 🚛📊

Esta herramienta te permitirá capturar, gestionar y simular rutas de forma eficiente y precisa.  
Utiliza el menú lateral para comenzar con:

- 📋 **Datos Generales**
- 🛣️ **Captura de Ruta**
- 📁 **Gestión de Rutas**
- 🔁 **Simulador Vuelta Redonda**

---
""")
