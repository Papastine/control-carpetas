import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from st_keyup import st_keyup

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA (Estricta y Corporativa)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Control TOP QA", layout="wide")

st.markdown("""
    <style>
    /* Ajustes de espaciado y diseño corporativo */
    .main .block-container { padding-top: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-weight: 600; text-transform: uppercase; color: #555; }
    hr { margin-top: 1em; margin-bottom: 1em; }
    </style>
""", unsafe_allow_html=True)

st.title("SISTEMA DE CONTROL DE CARPETAS TOP")
st.markdown("Plataforma Estricta de Auditoría y Trazabilidad Documental")

# -----------------------------------------------------------------------------
# MATRIZ DE SUBSISTEMAS ESTANDARIZADA
# -----------------------------------------------------------------------------
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
estados_oficiales = ["OK", "Falta firma", "En revision", "Faltan PRT", "Falta escanear"]
empresas_oficiales = ["TECHINT", "IDE", "BELFI", "Syncore"]
tipos_oficiales = ["CRP", "PRECOM"]

# -----------------------------------------------------------------------------
# CONEXIÓN Y EXTRACCIÓN DE DATOS
# -----------------------------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    return conn.read(ttl=0)

try:
    data = cargar_datos()
except Exception as e:
    st.error(f"Falla crítica de conexión con la base de datos: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# CONTROLADOR DE NAVEGACIÓN
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("NAVEGACIÓN")
    modo = st.radio("MÓDULO DE OPERACIÓN:", ["Ingreso Documental", "Auditoría y Edición"])
    st.markdown("---")
    if st.button("Forzar Sincronización", use_container_width=True):
        st.rerun()

# -----------------------------------------------------------------------------
# MÓDULO 1: INGRESO DOCUMENTAL
# -----------------------------------------------------------------------------
if modo == "Ingreso Documental":
    
    with st.container(border=True):
        st.subheader("REGISTRO DE NUEVO LOTE")
        st.caption("Los campos Subsistema, Tomo y Responsable son obligatorios para validar el ingreso.")
        
        with st.form("registro_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                subsistema_sel = st.selectbox("ID Subsistema", ss_master)
                subsistema_manual = st.text_input("Ingreso Manual (Restringido a 'OTRO')")
                tipo = st.selectbox("Categoría", tipos_oficiales)
                tomo = st.text_input("Tomo N° / Rango")
                
            with col2:
                subcontrato = st.selectbox("Empresa Emisora", empresas_oficiales)
                responsable = st.text_input("Responsable a cargo")
                estado = st.selectbox("Estado Operativo", estados_oficiales)
                
            comentario = st.text_area("Observaciones Adicionales", height=100)
                
            submit = st.form_submit_button("Guardar Registro", type="primary")

        if submit:
            subsistema_final = subsistema_manual.strip().upper() if subsistema_sel == "OTRO (Ingreso Manual)" else subsistema_sel
            
            if not subsistema_final or not responsable or not tomo:
                st.error("Operación denegada: Faltan campos obligatorios.")
            else:
                nuevo_registro = pd.DataFrame([{
                    "Subsistema": subsistema_final,
                    "Tipo": tipo,
                    "Tomo": str(tomo).strip(),
                    "Subcontrato": subcontrato,
                    "Responsable": str(responsable).strip().upper(),
                    "Estado": estado,
                    "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Comentarios": str(comentario).strip()
                }])
                df_base = data.dropna(how="all") if data is not None else pd.DataFrame()
                df_actualizado = pd.concat([df_base, nuevo_registro], ignore_index=True)
                conn.update(data=df_actualizado)
                st.success("Lote registrado exitosamente.")
                st.rerun()

# -----------------------------------------------------------------------------
# MÓDULO 2: AUDITORÍA Y EDICIÓN
# -----------------------------------------------------------------------------
else:
    df_limpio = data.dropna(subset=["Subsistema"]) if data is not None and not data.empty else pd.DataFrame()
    
    if df_limpio.empty:
        st.info("Base de datos sin registros. Ejecute el ingreso en el Módulo 1.")
    else:
        # Sanitización metódica de datos
        df_limpio = df_limpio.fillna("").astype(str).replace(["nan", "None"], "")
        
        # --- PANEL DE MÉTRICAS ---
        st.subheader("RESUMEN GERENCIAL")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TOTAL REGISTROS", len(df_limpio))
        c2.metric("CARPETAS OK", len(df_limpio[df_limpio["Estado"] == "OK"]))
        c3.metric("EN REVISIÓN", len(df_limpio[df_limpio["Estado"] == "En revision"]))
        c4.metric("FALTA ESCANEAR", len(df_limpio[df_limpio["Estado"] == "Falta escanear"]))

        st.markdown("---")

        # --- MOTOR DE FILTRADO MULTIVARIABLE ---
        st.subheader("CONTROL Y FILTRADO DE DATOS")
        
        with st.container(border=True):
            f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1, 1, 1])
            
            with f_col1:
                buscador_txt = st_keyup("Buscar por TAG Subsistema", key="buscador_ss", placeholder="Escriba aquí...")
            with f_col2:
                filtro_estado = st.selectbox("Filtrar por Estado", ["TODOS"] + estados_oficiales)
            with f_col3:
                filtro_empresa = st.selectbox("Filtrar por Empresa", ["TODOS"] + empresas_oficiales)
            with f_col4:
                filtro_tipo = st.selectbox("Filtrar por Tipo", ["TODOS"] + tipos_oficiales)

        # Aplicación estricta de filtros sobre la vista de datos
        df_vis = df_limpio.copy()
        
        if buscador_txt:
            df_vis = df_vis[df_vis["Subsistema"].str.contains(buscador_txt.upper(), na=False)]
        if filtro_estado != "TODOS":
            df_vis = df_vis[df_vis["Estado"] == filtro_estado]
        if filtro_empresa != "TODOS":
            df_vis = df_vis[df_vis["Subcontrato"] == filtro_empresa]
        if filtro_tipo != "TODOS":
            df_vis = df_vis[df_vis["Tipo"] == filtro_tipo]

        # --- INTERFAZ DE EDICIÓN Y EXPORTACIÓN ---
        st.write("") # Espaciador
        
        if not df_vis.empty:
            df_editado = st.data_editor(
                df_vis,
                use_container_width=True,
                num_rows="fixed", # Restringe inserción manual para mantener integridad
                hide_index=True,
                column_config={
                    "Subsistema": st.column_config.SelectboxColumn("Subsistema", options=ss_master, required=True),
                    "Tipo": st.column_config.SelectboxColumn("Tipo", options=tipos_oficiales, required=True),
                    "Tomo": st.column_config.TextColumn("Tomo", required=True),
                    "Subcontrato": st.column_config.SelectboxColumn("Emisor", options=empresas_oficiales, required=True),
                    "Responsable": st.column_config.TextColumn("Responsable", required=True),
                    "Estado": st.column_config.SelectboxColumn("Estado", options=estados_oficiales, required=True),
                    "Fecha_Registro": st.column_config.TextColumn("Última Act.", disabled=True),
                    "Comentarios": st.column_config.TextColumn("Observaciones")
                }
            )

            # Botones de Acción inferior
            col_save, col_empty, col_export = st.columns([2, 2, 1])
            
            with col_save:
                if st.button("Sincronizar Cambios Auditados", type="primary", use_container_width=True):
                    df_editado = df_editado.fillna("").astype(str).replace(["nan", "None"], "")
                    hubo_cambios = False
                    
                    for idx in df_editado.index:
                        if idx in df_limpio.index:
                            if not df_limpio.loc[idx].equals(df_editado.loc[idx]):
                                df_limpio.loc[idx] = df_editado.loc[idx]
                                df_limpio.loc[idx, "Fecha_Registro"] = datetime.now().strftime("%Y-%m-%d %H:%M") + " (Editado)"
                                hubo_cambios = True

                    if hubo_cambios:
                        conn.update(data=df_limpio)
                        st.success("Base de datos maestra sincronizada.")
                        st.rerun()
                    else:
                        st.info("No se detectaron modificaciones para sincronizar.")
                        
            with col_export:
                csv_data = df_vis.to_csv(index=False, sep=";", encoding="utf-8-sig")
                st.download_button("Exportar Vista a Excel", csv_data, f"Reporte_TOP_{datetime.now().strftime('%d-%m-%Y')}.csv", "text/csv", use_container_width=True)
                
        else:
            st.warning("Los parámetros de filtrado no arrojaron resultados en la base de datos.")
