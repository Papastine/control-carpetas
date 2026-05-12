import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from st_keyup import st_keyup

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Control TOP QA", layout="wide")

st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; max-width: 98%; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-weight: 600; text-transform: uppercase; color: #555; }
    hr { margin-top: 1em; margin-bottom: 1em; }
    </style>
""", unsafe_allow_html=True)

st.title("Sistema de Control de Carpetas TOP")
st.caption("Plataforma Estricta de Auditoría y Trazabilidad Documental")
st.divider()

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

ss_master = sorted(list(set(ss_ide + ss_techint_belfi))) + ["OTRO (INGRESO MANUAL)"]
estados_oficiales = ["OK", "Falta firma", "En revision", "Faltan PRT", "Falta escanear"]
empresas_oficiales = ["TECHINT", "IDE", "BELFI", "Syncore"]
tipos_oficiales = ["CRP", "PRECOM"]

# -----------------------------------------------------------------------------
# CONEXIÓN A BASE DE DATOS
# -----------------------------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    return conn.read(ttl=0)

try:
    data = cargar_datos()
except Exception as e:
    st.error(f"Falla crítica de conexión a la base de datos: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# NAVEGACIÓN LATERAL
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("Módulos de Operación")
    modo = st.radio("Seleccione Acción:", ["01. Ingreso Documental", "02. Auditoría y Edición"])
    st.divider()
    if st.button("Forzar Sincronización", use_container_width=True):
        st.rerun()

# -----------------------------------------------------------------------------
# MÓDULO 1: INGRESO DOCUMENTAL
# -----------------------------------------------------------------------------
if modo == "01. Ingreso Documental":
    
    st.subheader("Registro de Nuevo Lote")
    st.caption("Complete los campos obligatorios. El motor de base de datos rechazará automáticamente ingresos duplicados.")
    
    with st.form("registro_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            subsistema_sel = st.selectbox("ID Subsistema", ss_master)
            
            # Compuerta lógica: Despliega input manual si se requiere
            if subsistema_sel == "OTRO (INGRESO MANUAL)":
                subsistema_manual = st.text_input("Ingreso Manual de Subsistema")
            else:
                subsistema_manual = ""
                
            tipo = st.selectbox("Categoría Documental", tipos_oficiales)
            tomo = st.text_input("Tomo N° / Rango")
            
        with col2:
            subcontrato = st.selectbox("Empresa Emisora", empresas_oficiales)
            responsable = st.text_input("Responsable QA")
            estado = st.selectbox("Estado Operativo", estados_oficiales)
            
            # Selector de fecha real de recepción forzado a formato DD/MM/YYYY
            fecha_recepcion = st.date_input("Fecha de Recepción", datetime.today(), format="DD/MM/YYYY")
            
        comentario = st.text_area("Observaciones Adicionales", height=100)
            
        submit = st.form_submit_button("Guardar Registro", type="primary")

    if submit:
        subsistema_final = subsistema_manual.strip().upper() if subsistema_sel == "OTRO (INGRESO MANUAL)" else subsistema_sel
        
        if not subsistema_final or not responsable or not tomo:
            st.error("Operación Abortada: Existen campos obligatorios vacíos.")
        else:
            df_base = data.dropna(subset=["Subsistema"]).fillna("").astype(str) if data is not None else pd.DataFrame()
            
            # BLOQUEO DE DUPLICIDAD
            if not df_base.empty:
                duplicado = df_base[
                    (df_base["Subsistema"] == subsistema_final) & 
                    (df_base["Tipo"] == tipo) & 
                    (df_base["Tomo"] == str(tomo).strip())
                ]
            else:
                duplicado = pd.DataFrame()

            if not duplicado.empty:
                st.error("Infracción de Integridad: Este lote (Subsistema, Tipo y Tomo) ya figura en los registros.")
            else:
                nuevo_registro = pd.DataFrame([{
                    "Subsistema": subsistema_final,
                    "Tipo": tipo,
                    "Tomo": str(tomo).strip(),
                    "Subcontrato": subcontrato,
                    "Responsable": str(responsable).strip().upper(),
                    "Estado": estado,
                    "Fecha_Registro": fecha_recepcion.strftime("%d/%m/%Y"),
                    "Comentarios": str(comentario).strip()
                }])
                df_actualizado = pd.concat([data.dropna(how="all"), nuevo_registro], ignore_index=True)
                conn.update(data=df_actualizado)
                st.success("Lote ingresado exitosamente al repositorio maestro.")
                st.rerun()

# -----------------------------------------------------------------------------
# MÓDULO 2: AUDITORÍA Y EDICIÓN
# -----------------------------------------------------------------------------
else:
    df_limpio = data.dropna(subset=["Subsistema"]) if data is not None and not data.empty else pd.DataFrame()
    
    if df_limpio.empty:
        st.info("El repositorio de datos se encuentra vacío.")
    else:
        df_limpio = df_limpio.fillna("").astype(str).replace(["nan", "None"], "")
        
        # --- BUSCADOR TÁCTICO INMEDIATO ---
        st.subheader("Buscador de Subsistemas")
        buscador_txt = st_keyup("Escriba el Subsistema para aislar el registro:", key="buscador_ss")
        st.divider()

        # --- PANEL MÉTRICO ---
        total_reg = len(df_limpio)
        total_ok = len(df_limpio[df_limpio["Estado"] == "OK"])
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Registros Totales", total_reg)
        c2.metric("Carpetas OK", total_ok)
        c3.metric("En Revisión QA", len(df_limpio[df_limpio["Estado"] == "En revision"]))
        c4.metric("Falta Escanear", len(df_limpio[df_limpio["Estado"] == "Falta escanear"]))
        st.write("")

        # --- FILTROS DE VISTA SECUNDARIOS ---
        with st.expander("Desplegar Filtros Secundarios (Estado, Empresa, Tipo)"):
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                filtro_estado = st.selectbox("Filtrar por Estado", ["TODOS"] + estados_oficiales)
            with f_col2:
                filtro_empresa = st.selectbox("Filtrar por Empresa", ["TODOS"] + empresas_oficiales)
            with f_col3:
                filtro_tipo = st.selectbox("Filtrar por Tipo", ["TODOS"] + tipos_oficiales)

        # ORDENAMIENTO ALFANUMÉRICO Y APLICACIÓN DE FILTROS
        df_limpio = df_limpio.sort_values(by=["Subsistema", "Tipo", "Tomo"], ascending=[True, True, True]).reset_index(drop=True)
        df_vis = df_limpio.copy()
        
        if buscador_txt:
            df_vis = df_vis[df_vis["Subsistema"].str.contains(buscador_txt.upper(), na=False)]
        if filtro_estado != "TODOS":
            df_vis = df_vis[df_vis["Estado"] == filtro_estado]
        if filtro_empresa != "TODOS":
            df_vis = df_vis[df_vis["Subcontrato"] == filtro_empresa]
        if filtro_tipo != "TODOS":
            df_vis = df_vis[df_vis["Tipo"] == filtro_tipo]

        # --- INTERFAZ DE EDICIÓN SEGURA ---
        st.write("### Matriz de Auditoría de Datos")
        st.info("Doble clic en la celda para editar. Las columnas de identificación (Subsistema, Tipo, Tomo) están bloqueadas para prevenir arrastres accidentales.")
        
        if not df_vis.empty:
            df_editado = st.data_editor(
                df_vis,
                use_container_width=True,
                num_rows="fixed",
                hide_index=False, # Mantiene el índice nativo para resaltar fila
                column_config={
                    "Subsistema": st.column_config.TextColumn("Subsistema", disabled=True), # BLOQUEO ANTI-ARRASTRE
                    "Tipo": st.column_config.TextColumn("Tipo", disabled=True),             # BLOQUEO ANTI-ARRASTRE
                    "Tomo": st.column_config.TextColumn("Tomo", disabled=True),             # BLOQUEO ANTI-ARRASTRE
                    "Subcontrato": st.column_config.SelectboxColumn("Subcontrato", options=empresas_oficiales, required=True),
                    "Responsable": st.column_config.TextColumn("Responsable", required=True),
                    "Estado": st.column_config.SelectboxColumn("Estado", options=estados_oficiales, required=True),
                    "Fecha_Registro": st.column_config.TextColumn("Fecha (DD/MM/YYYY)", disabled=False),
                    "Comentarios": st.column_config.TextColumn("Comentarios")
                }
            )

            st.write("")
            col_save, col_empty, col_export = st.columns([2, 2, 1])
            
            with col_save:
                if st.button("Sincronizar Cambios Editados", type="primary", use_container_width=True):
                    df_editado_str = df_editado.fillna("").astype(str).replace(["nan", "None"], "")
                    hubo_cambios = False
                    
                    for idx in df_editado_str.index:
                        if idx in df_limpio.index:
                            fila_editada = df_editado_str.loc[idx]
                            fila_original = df_limpio.loc[idx]
                            
                            if not fila_original.equals(fila_editada):
                                df_limpio.loc[idx] = fila_editada
                                df_limpio.loc[idx, "Fecha_Registro"] = fila_editada["Fecha_Registro"] + " (Editado)"
                                hubo_cambios = True

                    if hubo_cambios:
                        conn.update(data=df_limpio)
                        st.success("Cambios sincronizados en la base de datos.")
                        st.rerun()
                    else:
                        st.info("No se detectaron modificaciones para guardar.")
                        
            with col_export:
                csv_data = df_vis.to_csv(index=False, sep=";", encoding="utf-8-sig")
                st.download_button("Exportar Vista (CSV)", csv_data, f"Reporte_TOP_{datetime.now().strftime('%d%m%Y')}.csv", "text/csv", use_container_width=True)

            st.divider()

            # --- ZONA DE PURGA (HARD DELETE) ---
            st.write("### Zona de Eliminación de Registros")
            st.warning("Seleccione el registro exacto a eliminar. Esta acción borrará la línea seleccionada de la base de datos maestra.")
            
            opciones_purga = df_vis.index.tolist()
            formato_purga = lambda x: f"{df_vis.loc[x, 'Subsistema']} | Tipo: {df_vis.loc[x, 'Tipo']} | Tomo: {df_vis.loc[x, 'Tomo']} | Estado: {df_vis.loc[x, 'Estado']}"
            
            registro_a_borrar = st.selectbox("Registro a purgar:", opciones_purga, format_func=formato_purga)
            
            if st.button("ELIMINAR REGISTRO SELECCIONADO", type="primary"):
                df_limpio = df_limpio.drop(index=registro_a_borrar)
                conn.update(data=df_limpio)
                st.success("Registro purgado exitosamente del sistema.")
                st.rerun()
                
        else:
            st.warning("No existen coincidencias de datos bajo los parámetros actuales.")
