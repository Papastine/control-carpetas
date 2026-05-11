import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control TOP/PRECOM", layout="wide")
st.title("📦 Sistema de Control de Carpetas y Subsistemas")

conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read() 

with st.sidebar:
    st.header("Acciones Rápidas")
    modo = st.radio("Selecciona modo:", ["Visualizar", "Ingresar/Modificar"])

if modo == "Ingresar/Modificar":
    with st.form("registro_form"):
        st.subheader("Registrar nuevo movimiento")
        col1, col2 = st.columns(2)
        
        with col1:
            subsistema = st.text_input("ID Subsistema (Tag, ej: 100-PIP-001)")
            tipo = st.selectbox("Categoría", ["TOP", "PRECOM"])
            tomo = st.number_input("Número de Tomo", min_value=1, step=1)
            
        with col2:
            estado = st.selectbox("Estado Actual", ["Pendiente Entrega", "Recibido", "En Revisión", "Falta Escanear", "OK"])
            comentario = st.text_area("Notas / Modificaciones")
            
        submit = st.form_submit_button("Guardar en Nube")

        if submit:
            if subsistema == "":
                st.error("⚠️ El ID del Subsistema es obligatorio.")
            else:
                nuevo_registro = pd.DataFrame([{
                    "Subsistema": subsistema,
                    "Tipo": tipo,
                    "Tomo": str(tomo),
                    "Estado": estado,
                    "Fecha_Update": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Comentarios": comentario
                }])
                
                df_actualizado = pd.concat([data, nuevo_registro], ignore_index=True)
                conn.update(data=df_actualizado)
                
                st.success("✅ Registro guardado exitosamente.")
                st.rerun() 

else:
    st.subheader("Estado General de Carpetas")
    
    if data.empty:
        st.info("No hay registros aún. Ve a Ingresar/Modificar para agregar el primero.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Registros", len(data))
        c2.metric("Subsistemas OK", len(data[data["Estado"] == "OK"]))
        c3.metric("En Revisión / Pendientes", len(data[data["Estado"] != "OK"]))

        st.dataframe(data, use_container_width=True)