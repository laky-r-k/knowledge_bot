# 🤖 AI-Based Help Bot for MOSDAC Knowledge Retrieval

An intelligent virtual assistant designed for the **MOSDAC (Meteorological and Oceanographic Satellite Data Archival Centre)** portal, which provides satellite data and services to the public. This AI system helps users retrieve information effortlessly from FAQs, documentation, and data product pages using a combination of **knowledge graphs and large language models (LLMs)**.

---

## 🎯 Project Objective

> The MOSDAC portal hosts rich scientific content including:
> - Satellite mission details
> - Product specifications
> - User manuals
> - Technical documentation

However, users often face difficulty navigating this layered, multi-format content.  
Our solution is an **AI-powered help bot** that can:
- Understand natural language queries
- Search extracted knowledge from the MOSDAC portal
- Respond intelligently using structured data and LLMs

---

## 🧠 What We’re Building

✅ A complete pipeline that includes:

| Component | Description |
|----------|-------------|
| 🔎 Web Scraper | Extract static and dynamic web content from MOSDAC |
| 🧠 NLP Pipeline | Identify entities and relationships using spaCy |
| 🌐 Knowledge Graph | Build a dynamic graph using triples (subject–predicate–object) |
| 💬 LLM Chatbot | Answer user queries using Gemini, OpenAI, or free local LLMs |
| 🔁 Hybrid Prompting | Combine KG search + chat history for intelligent responses |
| 🧩 Modular Design | Plug-and-play architecture, reusable across multiple portals |

---

## 🧩 Why This is Modular

The system is built with **clear interfaces** between modules (scraper, KG builder, LLM bot), making it:

- ✅ **Easily adaptable to other ISRO portals** like:
  - [Bhuvan](https://bhuvan.nrsc.gov.in/)
  - [VEDAS](https://vedas.sac.gov.in/)
  - [ISRO’s outreach sites or research portals](https://www.isro.gov.in/)
- ✅ **Language-agnostic (via NLP + LLM)**
- ✅ **Knowledge-source agnostic (PDFs, tables, FAQs, articles)**

By simply swapping the scraper input and re-running the KG builder, the **same bot can serve multiple departments or domains**.

---

## 📦 Requirements

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
