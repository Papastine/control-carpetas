import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control Documental", layout="wide")
st.title("📦 Sistema Estricto de Control de Carpetas")

# Conexión estandarizada con ttl=0 para forzar lectura fresca
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # ttl=0 evita que Streamlit guarde una versión antigua en memoria
    return conn.read(ttl=0)

try:
    data = cargar_datos()
except Exception as e:
    st.error(f"Falla de conexión de lectura a la base de datos: {e}")
    st.stop()

with st.sidebar:
    st.header("Panel de Control")
    modo = st.radio("Acción requerida:", ["Panel de Visualización", "Ingresar/Auditar Carpeta"])
    if st.button("🔄 Forzar Sincronización"):
        st.rerun()

if modo == "Ingresar/Auditar Carpeta":
    with st.form("registro_form", clear_on_submit=True):
        st.subheader("Ingreso de Trazabilidad Documental")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subsistema = st.text_input("ID Subsistema")
            tipo = st.selectbox("Categoría de Carpeta", ["CRP", "PRECOM"])
            tomo = st.text_input("Tomo N° / Rango (ej: 1 al 4, 5, 6-7)")
            
        with col2:
            subcontrato = st.selectbox("Empresa Subcontrato (Emisor)", ["TECHINT", "IDE", "Syncore"])
            responsable = st.text_input("Responsable (Receptor/Revisor)")
            estado = st.selectbox("Estado Operativo", ["Entregado por Subcliente", "Falta Escanear", "En Revisión QA", "Observado/Rechazado", "OK"])
            
        with col3:
            comentario = st.text_area("Registro de Modificaciones / Faltantes")
            
        submit = st.form_submit_button("Registrar en Base de Datos")

    if submit:
        if not subsistema or not responsable or not tomo:
            st.error("⚠️ Error Crítico: Los campos Subsistema, Tomo(s) y Responsable son obligatorios.")
        else:
            nuevo_registro = pd.DataFrame([{
                "Subsistema": subsistema.strip().upper(),
                "Tipo": tipo,
                "Tomo": tomo.strip(),
                "Subcontrato": subcontrato,
                "Responsable": responsable.strip().upper(),
                "Estado": estado,
                "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Comentarios": comentario.strip()
            }])
            
            # Limpiar datos nulos antes de concatenar para evitar errores visuales
            df_base = data.dropna(how="all") if data is not None else pd.DataFrame()
            df_actualizado = pd.concat([df_base, nuevo_registro], ignore_index=True)
            
            conn.update(data=df_actualizado)
            st.success("✅ Protocolo registrado. Cambia a 'Panel de Visualización' para ver los cambios.")
            st.balloons()

else:
    st.subheader("Auditoría de Subsistemas Pendientes y OK")
    
    # Limpieza preventiva de filas vacías que Google Sheets a veces genera
    df_limpio = data.dropna(subset=["Subsistema"]) if data is not None and not data.empty else pd.DataFrame()
    
    if df_limpio.empty:
        st.warning("La base de datos parece estar vacía o no tiene el formato correcto en la primera fila.")
        st.info("Asegúrate de que la primera fila del Sheet tenga estos nombres: Subsistema, Tipo, Tomo, Subcontrato, Responsable, Estado, Fecha_Registro, Comentarios")
    else:
        # Métricas
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Movimientos", len(df_limpio))
        c2.metric("Lotes OK", len(df_limpio[df_limpio["Estado"] == "OK"]))
        c3.metric("Lotes en QA", len(df_limpio[df_limpio["Estado"] == "En Revisión QA"]))
        c4.metric("Lotes sin Escanear", len(df_limpio[df_limpio["Estado"] == "Falta Escanear"]))

        st.markdown("---")
        filtro_sub = st.text_input("🔍 Filtrar por ID de Subsistema:")
        if filtro_sub:
            df_vis = df_limpio[df_limpio["Subsistema"].astype(str).str.contains(filtro_sub.upper(), na=False)]
        else:
            df_vis = df_limpio

        st.dataframe(df_vis, use_container_width=True, hide_index=True)
