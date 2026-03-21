import streamlit as st
import time
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

run = st.button("Run")

with st.sidebar:
    st.info("""
        ### About AquaMind
                
        This app lets you search taxa in WoRMS and OBIS, process biological records, assign ecoregions, and generate automatic reports.  
        It uses AI agents to reason about species information, and relies on the [OBIS Parquet data release](https://obis.org/2025/10/16/parquet-release/) for efficient access to occurrence records. 
        If you want to help us improve AquaMind, please fill in [this form](https://docs.google.com/forms/d/e/1FAIpQLScdGsUVgdHdfW24tvFsZSc2B8LqLQ0NtjlUYcP1YdGjSkhS-w/viewform?usp=publish-editor). It is anonymous and takes less than 3 minutes to complete. Thank you very much!
    """)

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

    log_box = st.empty()

    def progress_cb(msg: str):
        log_box.info(msg)

    with st.spinner("Running analysis (may take a few minutes)..."):
        result = run_pipeline(
            scientific_name=scientific_name.strip(),
            limit_per_dataset=int(limit_per_dataset),
            sample_size=int(sample_size),
            progress_cb=progress_cb,
        )

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

    # Crear contexto estructurado
    context_text = ContextBuilder.build(
        df=df_map,            # <-- df sin filtro
        summary_text=result["global_summary"],
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