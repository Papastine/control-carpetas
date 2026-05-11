import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control Documental QA", layout="wide")
st.title("📦 Sistema Estricto de Control de Carpetas")

# 1. MATRIZ DE SUBSISTEMAS ESTANDARIZADA
ss_ide = [
    "7114-A01-000", "7114-A01-001", "7114-A01-002", "7114-A01-003", "7114-A01-005", "7114-A01-006", "7114-A01-007", "7114-A01-008", 
    "7210-B01-001", "7210-B01-002", "7210-B01-003", "7210-B01-004", "7210-B01-005", "7210-B01-006", "7210-B01-007", "7210-B01-008", 
    "7210-B01-009", "7210-B01-010", "7210-B01-011", "7210-B01-012", "7212-B01-013", "7212-B01-014", "7212-B01-015", "7212-B01-018", 
    "7212-B01-019", "7212-B01-020", "7212-B01-021", "7212-B01-022", "7212-B01-023", "7212-B01-024", "7213-B01-025", "7213-B01-026", 
    "7213-B01-027", "7213-B01-028", "7213-B01-029", "7213-B01-030", "7213-B01-031", "7213-B01-032", "7213-B01-033", "7213-B01-034", 
    "7213-B01-035", "7213-B01-036", "7213-B01-038", "7213-B01-039", "7213-B01-040", "7213-B01-041", "7213-B01-042", "7221-C01-001", 
    "7221-C01-002", "7221-C01-003", "7221-C01-004", "7221-C01-005", "7221-C01-006", "7221-C01-007", "7221-D01-006", "7221-D01-008", 
    "7221-D02-001", "7221-D02-002", "7221-D02-003", "7221-D02-004", "7221-D02-006", "7221-D02-007", "7221-D02-008", "7221-D02-009", 
    "7221-D02-010", "7221-D02-011", "7230-F01-001", "7230-F01-002", "7240-G01-001", "7240-G01-002", "7240-G02-001", "7240-G03-001", 
    "7240-G03-002", "7240-G04-001", "7240-G04-002", "7240-G04-003", "7240-G04-004", "7240-G04-005", "7240-G04-010", "7240-G04-011", 
    "7240-G04-013", "7240-G04-014", "7240-G05-001", "7240-G05-003", "7240-G05-004", "7240-G05-005", "7240-G05-006", "7240-G05-007", 
    "7240-G05-008", "7240-G05-010", "7240-G05-011", "7240-G05-014", "7240-G05-015", "7240-G05-018", "7240-G06-001", "7250-I01-001", 
    "7250-I01-002", "7250-I01-003", "7260-W01-001", "7261-B01-037", "7264-Z01-001", "7270-E01-001", "7270-E02-001", "7270-E02-002", 
    "7270-E02-003", "7270-E02-004", "7270-E02-005", "7270-E02-006", "7270-E02-007", "7270-E02-008", "7270-E02-009", "7270-E02-010", 
    "7270-E02-011", "7270-E02-012", "7270-S01-001", "7270-S01-002", "7270-S01-003", "7270-S01-004", "7270-S01-005", "7270-S01-006", 
    "7270-S01-007", "7270-S01-008", "7270-S01-009", "7270-S01-010", "7270-S01-011", "7270-S01-012", "7270-S01-013", "7200-FTS-09", 
    "7200-FTS-12", "7200-FTS-02", "7200-FTS-08", "7200-FTS-01", "7200-FTS-03", "7200-FTS-04", "7200-FTS-05", "7200-FTS-06", 
    "7200-FTS-07", "7200-FTS-10", "7200-FTS-11", "7200-FTS-13", "7200-FTS-14", "7200-FTS-15", "7200-FTS-16", "7200-FTS-17", 
    "7200-FTS-20", "7200-FTS-21", "7200-FTS-22", "7200-FTS-18", "7200-FTS-19"
]

ss_techint_belfi = [
    "7111-F01-001", "7113-F01-001-A1", "7113-F01-001-B2", "7114-F01-001", "7121-F01-001", "7122-F01-001", "7123-F01-001", 
    "7130-F01-001", "7130-F01-002"
]

ss_master = sorted(list(set(ss_ide + ss_techint_belfi))) + ["OTRO (Ingreso Manual)"]

# 2. CONEXIÓN Y EXTRACCIÓN DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    return conn.read(ttl=0)

try:
    data = cargar_datos()
except Exception as e:
    st.error(f"Falla de conexión de lectura: {e}")
    st.stop()

# 3. CONTROLADOR DE INTERFAZ
with st.sidebar:
    st.header("Panel de Operaciones")
    modo = st.radio("Fase de trabajo:", ["1. Ingreso Documental", "2. Panel de Auditoría y Edición"])
    if st.button("🔄 Forzar Sincronización"):
        st.rerun()

# ==========================================
# MÓDULO 1: INGRESO NUEVO
# ==========================================
if modo == "1. Ingreso Documental":
    with st.form("registro_form", clear_on_submit=True):
        st.subheader("Ingreso Inicial de Trazabilidad")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subsistema_sel = st.selectbox("ID Subsistema (Matriz Oficial)", ss_master)
            subsistema_manual = st.text_input("Ingreso Manual (Solo si elegiste 'OTRO')")
            tipo = st.selectbox("Categoría de Carpeta", ["CRP", "PRECOM"])
            tomo = st.text_input("Tomo N° / Rango (ej: 1 al 4, 5, 6-7)")
            
        with col2:
            subcontrato = st.selectbox("Empresa Subcontrato (Emisor)", ["TECHINT", "IDE", "BELFI", "Syncore"])
            responsable = st.text_input("Responsable (Receptor/Revisor)")
            estado = st.selectbox("Estado Operativo", ["Entregado por Subcliente", "Falta Escanear", "En Revisión QA", "Observado/Rechazado", "OK"])
            
        with col3:
            comentario = st.text_area("Registro de Modificaciones / Faltantes")
            
        submit = st.form_submit_button("Registrar Nuevo Lote")

    if submit:
        subsistema_final = subsistema_manual.strip().upper() if subsistema_sel == "OTRO (Ingreso Manual)" else subsistema_sel
        
        if not subsistema_final or not responsable or not tomo:
            st.error("⚠️ Error Crítico: Los campos Subsistema, Tomo(s) y Responsable son obligatorios.")
        else:
            nuevo_registro = pd.DataFrame([{
                "Subsistema": subsistema_final,
                "Tipo": tipo,
                "Tomo": tomo.strip(),
                "Subcontrato": subcontrato,
                "Responsable": responsable.strip().upper(),
                "Estado": estado,
                "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Comentarios": comentario.strip()
            }])
            
            df_base = data.dropna(how="all") if data is not None else pd.DataFrame()
            df_actualizado = pd.concat([df_base, nuevo_registro], ignore_index=True)
            conn.update(data=df_actualizado)
            st.success("✅ Protocolo inicial registrado con éxito.")
            st.balloons()

# ==========================================
# MÓDULO 2: PANEL MAESTRO (Visualización, Edición y Eliminación)
# ==========================================
elif modo == "2. Panel de Auditoría y Edición":
    st.subheader("Auditoría General y Control de Registros")
    
    df_limpio = data.dropna(subset=["Subsistema"]) if data is not None and not data.empty else pd.DataFrame()
    
    if df_limpio.empty:
        st.warning("La base de datos está vacía.")
    else:
        # Métricas
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Movimientos", len(df_limpio))
        c2.metric("Lotes OK", len(df_limpio[df_limpio["Estado"] == "OK"]))
        c3.metric("Lotes en QA", len(df_limpio[df_limpio["Estado"] == "En Revisión QA"]))
        c4.metric("Lotes sin Escanear", len(df_limpio[df_limpio["Estado"] == "Falta Escanear"]))

        st.markdown("---")
        st.info("💡 **Instrucción de eliminación:** Para borrar una fila, selecciónala marcando el cuadro a su izquierda y presiona 'Delete' en tu teclado. Luego presiona el botón de guardado abajo.")
        
        # Data Editor con num_rows="dynamic" para permitir ELIMINAR filas
        df_editado = st.data_editor(
            df_limpio,
            use_container_width=True,
            num_rows="dynamic", # Permite borrar filas existentes
            hide_index=True,
            column_config={
                "Subsistema": st.column_config.SelectboxColumn("Subsistema", options=ss_master, required=True),
                "Tipo": st.column_config.SelectboxColumn("Tipo", options=["CRP", "PRECOM"], required=True),
                "Tomo": st.column_config.TextColumn("Tomo N° / Rango", required=True),
                "Subcontrato": st.column_config.SelectboxColumn("Subcontrato", options=["TECHINT", "IDE", "BELFI", "Syncore"], required=True),
                "Responsable": st.column_config.TextColumn("Responsable", required=True),
                "Estado": st.column_config.SelectboxColumn("Estado Operativo", options=["Entregado por Subcliente", "Falta Escanear", "En Revisión QA", "Observado/Rechazado", "OK"], required=True),
                "Fecha_Registro": st.column_config.TextColumn("Última Actualización", disabled=True),
                "Comentarios": st.column_config.TextColumn("Comentarios")
            }
        )

        if st.button("💾 Auditar y Guardar Cambios en la Nube", type="primary"):
            # Lógica de detección de cambios o eliminación
            if len(df_editado) != len(df_limpio):
                # Caso: Se eliminaron registros
                conn.update(data=df_editado)
                st.success(f"✅ Se eliminaron {len(df_limpio) - len(df_editado)} registro(s). Base de datos sincronizada.")
                st.rerun()
            else:
                # Caso: Solo se editaron valores
                df_limpio_str = df_limpio.astype(str)
                df_editado_str = df_editado.astype(str)
                cambios = df_limpio_str.compare(df_editado_str)
                
                if not cambios.empty:
                    indices_modificados = cambios.index
                    df_editado.loc[indices_modificados, "Fecha_Registro"] = datetime.now().strftime("%Y-%m-%d %H:%M") + " (Editado)"
                    conn.update(data=df_editado)
                    st.success(f"✅ Se guardaron {len(indices_modificados)} modificaciones.")
                    st.rerun()
                else:
                    st.info("No se detectaron variaciones.")
