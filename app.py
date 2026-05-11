import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control TOP/PRECOM", layout="wide")
st.title("📦 Sistema de Control de Carpetas y Subsistemas")

# Conexión estandarizada a la base de datos
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    data = conn.read()
except Exception as e:
    st.error(f"Falla de conexión a la base de datos: {e}")
    st.stop()

with st.sidebar:
    st.header("Panel de Control")
    modo = st.radio("Acción requerida:", ["Panel de Visualización", "Ingresar/Auditar Carpeta"])

if modo == "Ingresar/Auditar Carpeta":
    with st.form("registro_form"):
        st.subheader("Ingreso de Trazabilidad Documental")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subsistema = st.text_input("ID Subsistema (Tag)")
            tipo = st.selectbox("Categoría", ["TOP", "PRECOM"])
            tomo = st.number_input("Tomo N°", min_value=1, step=1)
            
        with col2:
            subcontrato = st.text_input("Empresa Subcontrato (Emisor)")
            responsable = st.text_input("Responsable (Receptor/Revisor)")
            estado = st.selectbox("Estado Operativo", ["Entregado por Subcliente", "Falta Escanear", "En Revisión QA", "Observado/Rechazado", "OK"])
            
        with col3:
            comentario = st.text_area("Registro de Modificaciones / Faltantes")
            
        submit = st.form_submit_button("Registrar en Base de Datos")

    if submit:
        if not subsistema or not subcontrato or not responsable:
            st.error("⚠️ Error Crítico: Los campos Subsistema, Subcontrato y Responsable son obligatorios para la trazabilidad.")
        else:
            nuevo_registro = pd.DataFrame([{
                "Subsistema": subsistema.strip().upper(),
                "Tipo": tipo,
                "Tomo": str(tomo),
                "Subcontrato": subcontrato.strip().upper(),
                "Responsable": responsable.strip().upper(),
                "Estado": estado,
                "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Comentarios": comentario.strip()
            }])
            
            df_actualizado = pd.concat([data, nuevo_registro], ignore_index=True)
            conn.update(data=df_actualizado)
            
            st.success("✅ Protocolo registrado correctamente.")
            st.rerun()

else:
    st.subheader("Auditoría de Subsistemas Pendientes y OK")
    
    if data is None or data.empty:
        st.warning("Base de datos vacía. No hay variables para analizar.")
    else:
        # Métricas de control estricto
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Registros", len(data))
        c2.metric("Carpetas OK", len(data[data["Estado"] == "OK"]))
        c3.metric("En Revisión QA", len(data[data["Estado"] == "En Revisión QA"]))
        c4.metric("Pendientes de Escaneo", len(data[data["Estado"] == "Falta Escanear"]))

        st.markdown("---")
        st.write("**Matriz de Trazabilidad Histórica**")
        
        # Filtro analítico
        filtro_sub = st.text_input("Filtrar por ID de Subsistema (Presiona Enter):")
        if filtro_sub:
            df_filtrado = data[data["Subsistema"].str.contains(filtro_sub.upper(), na=False)]
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        else:
            st.dataframe(data, use_container_width=True, hide_index=True)
