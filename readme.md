# 🧠 Marine Species Reasoning Agent

**Marine Species Reasoning Agent** is an experimental project that integrates marine biodiversity data from **OBIS** (Ocean Biodiversity Information System) with taxonomic validation from **WoRMS** (World Register of Marine Species).  
It leverages **LLM-based agents** to process, validate, and summarize large occurrence datasets into scientifically meaningful insights.

---

## 🌊 Overview

This tool automates the workflow of exploring marine species data by:
1. Querying **OBIS** for occurrence datasets of a target species.
2. Extracting and filtering relevant records from large public **S3** archives.
3. Enriching data with **MEOW marine ecoregions** (based on geographic coordinates).
4. Using **LLM agents** to generate bioregional summaries and interpret taxonomic and ecological patterns.
5. Combining all results into a single integrated text report.

The goal is to support marine research and environmental monitoring by enabling scalable, AI-driven reasoning over global biodiversity datasets.

---

## ⚙️ Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/gustavomarcelonunez/llm_agent.git
   cd llm_agent
   ```

2. **Create and activate a virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate    # on Linux/Mac
    # .\venv\Scripts\activate   # on Windows
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set your OpenAI API key**
    Create a .env file in the project root and add your key:
    ```bash
    OPENAI_API_KEY=your_api_key_here
    ```
    (Note: .env is ignored by Git for security.)

## 🚀 Usage

Run the main entry point from the terminal:
   ```bash
   python main.py
   ```
When prompted, enter the scientific name of a marine species (e.g., Eubalaena australis).

The script will:
- Fetch and validate taxonomic data from WoRMS.
- Retrieve occurrence data from OBIS’s public S3 repository.
- Assign each record to a MEOW marine ecoregion.
- Summarize each region via parallel LLM agents.
- Generate an integrated reasoning report.

## 📄 Output
Terminal: concise scientific summary.
outputs/ folder: a full integrated text file combining:
- WoRMS taxonomic information
- OBIS regional summaries
- Final reasoning synthesis

## 🧩 Main Components

llm_agent/
├── main.py                         # Entry point for the workflow
├── agents/
|   ├── reasoning_agent.py          # Final reasoning LLM
│   ├── regional_agent_runner.py    # Multithread-agent runner
│   ├── summarizer_agent.py         # Multi-agent summarization
├── api_search/
│   ├── obis_api.py                 # OBIS data retrieval and filtering
│   ├── worms_api.py                # WoRMS API integration
├── aws_search/
│   ├── obis_duckdb.py              # Bucket S3 caller
├── data/                           # MEOW shapefiles
├── utils/
│   ├── meow_ecoregions.py          # MEOW ecoregion spatial join
│   ├── save_regional_summaries.py  # Merge final summarie text output with regional summarie
│   ├── save_regional_summaries.py  # Combined text output
├── requirements.txt
├── .env (not committed)
└── outputs/                        # Generated summaries

## 🧠 Architecture Overview

        ┌───────────────┐
        │ User input    │
        │ (species name)│
        └──────┬────────┘
               ▼
        ┌───────────────┐
        │ OBIS Query    │──► Download datasets data
        └──────┬────────┘
               ▼
        ┌───────────────┐
        │ WoRMS API     │──► Validate taxonomy
        └──────┬────────┘
               ▼
        ┌──────────────────┐
        │ S3 recovery data │──► OBIS bucket occurrences recovery
        └──────┬───────────┘
               ▼
        ┌───────────────┐
        │ MEOW Regions  │──► Spatial classification
        └──────┬────────┘
               ▼
        ┌──────────────────────┐
        │ Regional LLM Agents  │──► Generate summaries
        └──────┬───────────────┘
               ▼
        ┌──────────────────────┐
        │ Reasoning Agent      │──► Integrate & interpret results
        └──────────────────────┘

## 🧪 Development Notes

- Tested on Ubuntu 22.04 with Python 3.10+.
- Uses duckdb for fast local querying of large CSV/Parquet data.
- Designed for modular expansion (e.g., adding visualization or additional datasets).
- Still under active development.

## 🛡️ License
MIT License — Free for research and educational use.

## 📬 Contact
Maintained by Gustavo Marcelo Nuñez
For questions or collaborations: gnunez@cenpat-conicet.gob.ar, guscostaf@gmail.com

---