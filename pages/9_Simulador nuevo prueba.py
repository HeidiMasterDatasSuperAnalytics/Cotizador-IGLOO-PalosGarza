import streamlit as st
import pandas as pd
import os

RUTA_RUTAS = "rutas_guardadas.csv"

st.title("🔁 Simulador de Vuelta Redonda")

def safe_number(x):
    return 0 if (x is None or (isinstance(x, float) and pd.isna(x))) else x

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)

    impo_rutas = df[df["Tipo"] == "IMPO"]
    expo_rutas = df[df["Tipo"] == "EXPO"]
    vacio_rutas = df[df["Tipo"] == "VACIO"]

    st.subheader("📌 Paso 1: Selección de ruta principal")
    tipo_principal = st.selectbox("¿Qué tipo de ruta deseas seleccionar primero?", ["IMPO", "EXPO"])

    ruta_principal = None
    ruta_vacio = None
    ruta_secundaria = None
    rutas_seleccionadas = []

    if tipo_principal == "IMPO":
        cliente = st.selectbox("Cliente IMPO", impo_rutas["Cliente"].dropna().unique())
        rutas = impo_rutas[impo_rutas["Cliente"] == cliente]
        idx = st.selectbox("Ruta IMPO", rutas.index.tolist(), format_func=lambda x: f"{rutas.loc[x, 'Origen']} → {rutas.loc[x, 'Destino']}")
        ruta_principal = rutas.loc[idx]
        rutas_seleccionadas.append(ruta_principal)

        st.markdown("---")
        st.subheader("📌 Paso 2: Ruta VACÍA sugerida (opcional)")
        destino_impo = ruta_principal["Destino"]
        vacio_candidatos = vacio_rutas[vacio_rutas["Origen"] == destino_impo]
        if not vacio_candidatos.empty:
            vacio_idx = st.selectbox("Ruta VACÍA (Origen = " + destino_impo + ")", vacio_candidatos.index.tolist(),
                                     format_func=lambda x: f"{vacio_candidatos.loc[x, 'Origen']} → {vacio_candidatos.loc[x, 'Destino']}")
            ruta_vacio = vacio_candidatos.loc[vacio_idx]
            rutas_seleccionadas.append(ruta_vacio)

        st.markdown("---")
        st.subheader("📌 Paso 3: Ruta EXPO sugerida (opcional)")
        if ruta_vacio is not None:
            destino_vacio = ruta_vacio["Destino"]
            candidatos = expo_rutas[expo_rutas["Origen"] == destino_vacio].copy()
        else:
            candidatos = expo_rutas[expo_rutas["Origen"] == destino_impo].copy()

        if not candidatos.empty:
            candidatos["Utilidad"] = candidatos["Ingreso Total"] - candidatos["Costo_Total_Ruta"]
            candidatos = candidatos.sort_values(by="Utilidad", ascending=False)
            expo_idx = st.selectbox("Ruta EXPO sugerida", candidatos.index.tolist(),
                                    format_func=lambda x: f"{candidatos.loc[x, 'Origen']} → {candidatos.loc[x, 'Destino']} (${candidatos.loc[x, 'Utilidad']:.2f})")
            ruta_secundaria = candidatos.loc[expo_idx]
            rutas_seleccionadas.append(ruta_secundaria)

    else:  # tipo_principal == "EXPO"
        cliente = st.selectbox("Cliente EXPO", expo_rutas["Cliente"].dropna().unique())
        rutas = expo_rutas[expo_rutas["Cliente"] == cliente]
        idx = st.selectbox("Ruta EXPO", rutas.index.tolist(), format_func=lambda x: f"{rutas.loc[x, 'Origen']} → {rutas.loc[x, 'Destino']}")
        ruta_principal = rutas.loc[idx]
        rutas_seleccionadas.append(ruta_principal)

        st.markdown("---")
        st.subheader("📌 Paso 2: Ruta VACÍA sugerida (opcional)")
        destino_expo = ruta_principal["Destino"]
        vacio_candidatos = vacio_rutas[vacio_rutas["Origen"] == destino_expo]
        if not vacio_candidatos.empty:
            vacio_idx = st.selectbox("Ruta VACÍA (Origen = " + destino_expo + ")", vacio_candidatos.index.tolist(),
                                     format_func=lambda x: f"{vacio_candidatos.loc[x, 'Origen']} → {vacio_candidatos.loc[x, 'Destino']}")
            ruta_vacio = vacio_candidatos.loc[vacio_idx]
            rutas_seleccionadas.append(ruta_vacio)

        st.markdown("---")
        st.subheader("📌 Paso 3: Ruta IMPO sugerida (opcional)")
        if ruta_vacio is not None:
            destino_vacio = ruta_vacio["Destino"]
            candidatos = impo_rutas[impo_rutas["Origen"] == destino_vacio].copy()
        else:
            candidatos = impo_rutas[impo_rutas["Origen"] == destino_expo].copy()

        if not candidatos.empty:
            candidatos["Utilidad"] = candidatos["Ingreso Total"] - candidatos["Costo_Total_Ruta"]
            candidatos = candidatos.sort_values(by="Utilidad", ascending=False)
            impo_idx = st.selectbox("Ruta IMPO sugerida", candidatos.index.tolist(),
                                    format_func=lambda x: f"{candidatos.loc[x, 'Origen']} → {candidatos.loc[x, 'Destino']} (${candidatos.loc[x, 'Utilidad']:.2f})")
            ruta_secundaria = candidatos.loc[impo_idx]
            rutas_seleccionadas.append(ruta_secundaria)

    if st.button("🚛 Simular Vuelta Redonda"):
        ingreso_total = sum(safe_number(r.get("Ingreso Total", 0)) for r in rutas_seleccionadas)
        costo_total_general = sum(safe_number(r.get("Costo_Total_Ruta", 0)) for r in rutas_seleccionadas)

        utilidad_bruta = ingreso_total - costo_total_general
        costos_indirectos = ingreso_total * 0.35
        utilidad_neta = utilidad_bruta - costos_indirectos
        porcentaje_utilidad_bruta = (utilidad_bruta / ingreso_total * 100) if ingreso_total > 0 else 0
        porcentaje_utilidad_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

        # 🗂️ Detalle de Rutas
        st.markdown("---")
        st.subheader("🗂️ Detalle de Rutas")
        for r in rutas_seleccionadas:
            st.markdown(f"""
**{r['Tipo']} — {r.get('Cliente', 'Sin cliente')}**  
- {r['Origen']} → {r['Destino']}  
- Ingreso Total: ${safe_number(r.get('Ingreso Total')):,.2f}  
- Costo Total Ruta: ${safe_number(r.get('Costo_Total_Ruta')):,.2f}
""")

        # 📊 Resultado General
        st.markdown("---")
        st.subheader("📊 Resultado General")
        color_bruta = "green" if utilidad_bruta >= 0 else "red"
        color_neta = "green" if utilidad_neta >= 0 else "red"
        color_pct_bruta = "green" if porcentaje_utilidad_bruta >= 50 else "red"
        color_pct_neta = "green" if porcentaje_utilidad_neta >= 15 else "red"

        st.markdown(f"**Ingreso Total:** ${ingreso_total:,.2f}")
        st.markdown(f"**Costo Total:** ${costo_total_general:,.2f}")
        st.markdown(f"<strong>Utilidad Bruta:</strong> <span style='color:{color_bruta}; font-weight:bold'>${utilidad_bruta:,.2f}</span>", unsafe_allow_html=True)
        st.markdown(f"<strong>% Utilidad Bruta:</strong> <span style='color:{color_pct_bruta}; font-weight:bold'>{porcentaje_utilidad_bruta:.2f}%</span>", unsafe_allow_html=True)
        st.markdown(f"**Costos Indirectos (35%):** ${costos_indirectos:,.2f}")
        st.markdown(f"<strong>Utilidad Neta:</strong> <span style='color:{color_neta}; font-weight:bold'>${utilidad_neta:,.2f}</span>", unsafe_allow_html=True)
        st.markdown(f"<strong>% Utilidad Neta:</strong> <span style='color:{color_pct_neta}; font-weight:bold'>{porcentaje_utilidad_neta:.2f}%</span>", unsafe_allow_html=True)

        # 📋 Resumen de Rutas
        st.markdown("---")
        st.subheader("📋 Resumen de Rutas")
        tipos = ["IMPO", "VACIO", "EXPO"]
        cols = st.columns(len(tipos))

        def resumen_ruta(r):
            return [
                f"KM: {safe_number(r.get('KM')):,.2f}",
                f"Diesel Camión: ${safe_number(r.get('Costo_Diesel_Camion')):,.2f}",
                f"Diesel Termo: ${safe_number(r.get('Costo_Diesel_Termo')):,.2f}",
                f"Sueldo: ${safe_number(r.get('Sueldo_Operador')):,.2f}",
                f"Casetas: ${safe_number(r.get('Casetas')):,.2f}",
                f"Costo Cruce Convertido: ${safe_number(r.get('Costo Cruce Convertido')):,.2f}",
                "**Extras detallados:**",
                f"Lavado Termo: ${safe_number(r.get('Lavado_Termo')):,.2f}",
                f"Movimiento Local: ${safe_number(r.get('Movimiento_Local')):,.2f}",
                f"Puntualidad: ${safe_number(r.get('Puntualidad')):,.2f}",
                f"Pensión: ${safe_number(r.get('Pension')):,.2f}",
                f"Estancia: ${safe_number(r.get('Estancia')):,.2f}",
                f"Fianza Termo: ${safe_number(r.get('Fianza_Termo')):,.2f}",
                f"Renta Termo: ${safe_number(r.get('Renta_Termo')):,.2f}"
            ]

        for i, tipo in enumerate(tipos):
            with cols[i]:
                st.markdown(f"**{tipo}**")
                ruta = next((r for r in rutas_seleccionadas if r["Tipo"] == tipo), None)
                if ruta is not None:
                    for line in resumen_ruta(ruta):
                        st.write(line)
                else:
                    st.write("No aplica")

else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
