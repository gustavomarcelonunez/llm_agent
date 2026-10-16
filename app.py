import streamlit as st
import time
import html

from pipeline import run_pipeline, PIPELINE_STAGES
from utils.map_utils import render_occurrence_map

from pipeline import run_pipeline
from utils.map_utils import render_occurrence_map

st.cache_data.clear()
st.cache_resource.clear()

# Evitar caché del navegador
st.markdown(
    """
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    """, 
    unsafe_allow_html=True
)

# Invalidar assets cacheados
cache_buster = int(time.time())
st.markdown(f"""
<script>
fetch("/?cb={cache_buster}");
if ('serviceWorker' in navigator) {{
    navigator.serviceWorker.getRegistrations().then(function(registrations) {{
        for (let reg of registrations) {{
            reg.unregister();
        }}
    }});
}}
</script>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="AquaMind",
    page_icon="🌊",
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<style>
.header-container {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 10px 0px 30px 0px;
}
.header-logo {
    font-size: 60px;
}
.header-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: -5px;
}
.header-subtitle {
    font-size: 20px;
    color: #BBBBBB;
}
</style>

<div class="header-container">
    <div class="header-logo">🌊</div>
    <div>
        <div class="header-title">AquaMind</div>
        <div class="header-subtitle">Intelligent Exploration of Marine Biodiversity</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INPUTS
# ---------------------------------------------------------
scientific_name = st.text_input("Scientific name", placeholder="Ej: Odontesthes smitti")

with st.expander("Settings"):
    limit_per_dataset = st.number_input("Limit per dataset", 1, 5000, 200,
                                        help="Maximum number of occurrences that will be retrieved from each dataset before processing. Range: 1-5000"
                                        )
    sample_size = st.number_input("Sample size", 1, 1000, 15,
                                  help="Number of random OBIS datasets to be used for analysis. Range: 1-1000"
                                  )
# Estado del progreso, persistente entre reruns de Streamlit.
if "analysis_progress" not in st.session_state:
    st.session_state["analysis_progress"] = {
        stage: {
            "status": "pending",
            "duration": None,
        }
        for stage in PIPELINE_STAGES
    }

def render_progress(progress_box, progress_bar_box):
    progress_state = st.session_state["analysis_progress"]

    completed = sum(
        1
        for stage in PIPELINE_STAGES
        if progress_state[stage]["status"] == "complete"
    )
    failed = any(
        progress_state[stage]["status"] == "error"
        for stage in PIPELINE_STAGES
    )

    with progress_bar_box.container():
        st.progress(
            completed / len(PIPELINE_STAGES),
            text=f"{completed} of {len(PIPELINE_STAGES)} stages completed",
        )

    with progress_box.container():
        

        rows = []

        for stage in PIPELINE_STAGES:
            item = progress_state[stage]
            status = item["status"]
            duration = item["duration"]

            safe_stage = html.escape(stage)

            if status == "complete":
                icon = "✓"
                detail = f"{duration:.2f} s" if duration is not None else "Done"
                css_class = "complete"

            elif status == "running":
                icon = '<span class="am-spinner"></span>'
                detail = "In progress"
                css_class = "running"

            elif status == "error":
                icon = "✕"
                detail = f"Failed · {duration:.2f} s" if duration is not None else "Failed"
                css_class = "error"

            else:
                icon = "○"
                detail = "Pending"
                css_class = "pending"

            rows.append(
                f"""
                <div class="am-progress-row {css_class}">
                    <span class="am-progress-icon">{icon}</span>
                    <span class="am-progress-stage">{safe_stage}</span>
                    <span class="am-progress-detail">{detail}</span>
                </div>
                """
            )


        st.markdown(
            """
            <style>
            .am-progress-row {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 9px 2px;
                border-bottom: 1px solid rgba(128, 128, 128, 0.18);
                font-size: 0.92rem;
            }
            .am-progress-icon {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-width: 20px;
                font-weight: 600;
            }
            .am-progress-stage {
                flex: 1;
            }
            .am-progress-detail {
                font-size: 0.8rem;
                opacity: 0.7;
                white-space: nowrap;
            }
            .am-progress-row.complete .am-progress-icon {
                color: #2e9d62;
            }
            .am-progress-row.error .am-progress-icon {
                color: #dc4545;
            }
            .am-spinner {
                display: inline-block;
                width: 13px;
                height: 13px;
                border: 2px solid rgba(128, 128, 128, 0.3);
                border-top-color: #2e9d62;
                border-radius: 50%;
                animation: am-spin 0.8s linear infinite;
            }
            @keyframes am-spin {
                to { transform: rotate(360deg); }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "\n".join(rows),
            unsafe_allow_html=True,
        )


progress_bar_box = st.empty()

with st.expander("Analysis progress", expanded=True):
    progress_box = st.empty()
    
render_progress(progress_box, progress_bar_box)

run = st.button("Run")

with st.sidebar:
    @st.dialog("About AquaMind")
    def show_about():
        st.markdown("""
        This app lets you search taxa in WoRMS and OBIS,
        process biological records, assign ecoregions,
        and generate automatic reports.

        It uses AI agents to reason about species information
        and relies on the [OBIS Parquet data release](
        https://obis.org/2025/10/16/parquet-release/
        ) for efficient access to occurrence records.

        You can also chat with the data using the built-in AI assistant to explore results and ask questions about the retrieved biological records.

        If you want to help us improve AquaMind, please fill in
        [this anonymous feedback form](
        https://docs.google.com/forms/d/e/1FAIpQLScdGsUVgdHdfW24tvFsZSc2B8LqLQ0NtjlUYcP1YdGjSkhS-w/viewform?usp=publish-editor
        ). It takes less than 3 minutes. Thank you!
        """)

    if st.button("ⓘ About AquaMind"):
        show_about()

    # Popup
    @st.dialog("Disclaimer")
    def disclaimer_popup():
        st.markdown("""
            This application uses language models to analyze data from WoRMS and OBIS.
            The generated responses are for guidance only and may contain errors. They should not be considered definitive scientific advice.
            Verify the information with expert sources before making decisions.
        """)

    if st.button("Disclaimer"):
        disclaimer_popup()



# ---------------------------------------------------------
# EJECUCIÓN DEL PIPELINE (solo cuando se presiona Analizar)
# ---------------------------------------------------------
if run:
    if not scientific_name.strip():
        st.error("Please enter a scientific name.")
        st.stop()

    st.session_state.pop("chat_agent", None)
    st.session_state.pop("chat_history", None)

    log_box = st.empty()

    # Reiniciar el progreso para una nueva ejecución.
    st.session_state["analysis_progress"] = {
        stage: {
            "status": "pending",
            "duration": None,
        }
        for stage in PIPELINE_STAGES
    }

    render_progress(progress_box, progress_bar_box)

    def progress_cb(event: dict):
        stage = event["stage"]

        if stage not in st.session_state["analysis_progress"]:
            return

        st.session_state["analysis_progress"][stage].update({
            "status": event["status"],
            "duration": event.get("duration"),
        })

        render_progress(progress_box, progress_bar_box)

    try:
        with st.spinner("Running analysis..."):
            result = run_pipeline(
                scientific_name=scientific_name.strip(),
                limit_per_dataset=int(limit_per_dataset),
                sample_size=int(sample_size),
                progress_cb=progress_cb,
            )

    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        st.stop()

    # Error devuelto por la validación de WoRMS.
    if result.get("status") == "error":
        st.error(f"❌ {result['message']}")
        st.stop()

    st.session_state["analysis_result"] = result


    # Si hubo error al buscar el taxón
    if result.get("status") == "error":
        st.error(f"❌ {result['message']}")
        st.stop()

    # Guardamos resultados
    st.session_state["analysis_result"] = result

# ---------------------------------------------------------
# MOSTRAR RESULTADOS SI EXISTEN EN SESSION_STATE
# ---------------------------------------------------------
if "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]

    st.success("Analysis completed")

    st.subheader("Global summary")
    st.write(result["global_summary"])

    st.subheader("Map of occurrences")

    df_map = result["df"].copy()

    # ================================
    #      FILTROS INTERACTIVOS
    # ================================

    eco_counts = df_map["ecoregion"].value_counts().to_dict()   # {eco: count}

    options = ["All ({})".format(len(df_map))] + [
        f"{eco} ({eco_counts[eco]})" for eco in sorted(eco_counts.keys())
    ]

    selected = st.selectbox("Filter by ecoregion", options)

    # --- Filtro por ecoregión ---
    # Extraer el nombre real de la ecoregión (sin el número)
    if selected.startswith("All"):
        selected_ecoregion = None
    else:
        selected_ecoregion = selected.rsplit(" (", 1)[0]   # "North Patagonian Gulf"

    # Aplicar filtro
    if selected_ecoregion:
        df_map = df_map[df_map["ecoregion"] == selected_ecoregion]

    # ================================
    #      RENDER DEL MAPA
    # ================================

    render_occurrence_map(df_map)



    st.subheader("Download full report (TXT)")
    with open(result["txt_path"], "rb") as f:
        st.download_button(
            label="📥 Download full report",
            data=f,
            file_name=f"{result['scientific_name'].replace(' ', '_')}_report.txt",
            mime="text/plain",
        )

    # ---------------------------------------------------------
    # CHATBOT ABOUT THE REPORT
    # ---------------------------------------------------------

    from agents.chat_agent import ChatAgent, ContextBuilder

    st.subheader("Chat about this species")

    # Inicializamos el agente (solo una vez)
    if "chat_agent" not in st.session_state:
        st.session_state["chat_agent"] = ChatAgent(
            api_key=st.secrets["OPENAI_API_KEY"],  # si usas secrets
            model="gpt-4o-mini"
        )
    agent = st.session_state["chat_agent"]

    # Leer el informe completo como contexto para el chatbot.
    with open(result["txt_path"], "r", encoding="utf-8") as f:
        full_report = f.read()

    # Crear contexto estructurado con estadísticas y el informe completo.
    context_text = ContextBuilder.build(
        df=df_map,
        summary_text=full_report,
        species_name=result["scientific_name"]
    )



    # Historial del chat
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    user_message = st.text_input(
        "Ask something based on the analysis and data:"
    )

    send = st.button("Send message")
    if send and user_message.strip():
        assistant_message = agent.ask(
            context_text=context_text,
            chat_history=st.session_state["chat_history"],
            user_message=user_message
        )

        # Save history
        st.session_state["chat_history"].append({"role": "user", "content": user_message})
        st.session_state["chat_history"].append({"role": "assistant", "content": assistant_message})

    # Display messages
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**AquaMind AI:** {msg['content']}")