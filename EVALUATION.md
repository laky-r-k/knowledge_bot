# 📊 Knowledge Graph-RAG System: Evaluation & Benchmark Report

This document presents the quantitative and qualitative evaluation of the **Knowledge Graph (KG) Augmented Help Bot** compared against a **Baseline LLM (Gemini 3.5 Flash Lite alone without KG)** on real-world faculty domain knowledge from B.M.S. College of Engineering (BMSCE).

---

## 1. Executive Summary

| Evaluation Metric | Baseline LLM (No Graph) | Knowledge Graph-RAG (Our System) | Uplift / Impact |
| :--- | :---: | :---: | :---: |
| **Factual Accuracy** | **1.00 / 5.0** | **5.00 / 5.0** | **+400.0%** 🚀 |
| **Faithfulness (Anti-Hallucination)** | 4.33 / 5.0 | **5.00 / 5.0** | **+15.5%** |
| **Answer Relevance** | 1.83 / 5.0 | **5.00 / 5.0** | **+173.2%** |
| **KG Retrieval Hit Rate** | N/A | **100.0%** (6/6) | Perfect Recall |
| **Average Turnaround Latency** | 19.11s | 36.68s | Multi-step reasoning pipeline |

---

## 2. Head-to-Head Benchmark Results

Evaluation conducted using an independent **LLM-as-a-Judge** scoring harness across verified institutional ground truth:

| ID | Test Query | Baseline LLM (No KG) | With Knowledge Graph (Ours) | KG Grounded? |
|:---:|:---|:---:|:---:|:---:|
| **1** | Who is the Head of Department of Information Science and Engineering at BMSCE? | 1/5 *(hallucinated wrong person)* | **5/5** *(Dr. M Dakshayini)* | ✔ Yes |
| **2** | What is Dr. Gowrishankar's email address and current designation? | 1/5 *(claimed no access)* | **5/5** *(gowrishankar.cse@bmsce.ac.in)* | ✔ Yes |
| **3** | Who is the HOD of the Machine Learning department at BMSCE? | 1/5 *(hallucinated Dr. J. Ramesh)* | **5/5** *(Dr. Sandeep Varma N)* | ✔ Yes |
| **4** | What is Dr. Monika Puttaramaiah's designation and department? | 1/5 *(refused / unknown)* | **5/5** *(Assoc. Prof, AI&ML)* | ✔ Yes |
| **5** | Where did Dr. Gowrishankar receive his PhD from and in which year? | 1/5 *(unknown)* | **5/5** *(VTU, 2009)* | ✔ Yes |
| **6** | What are Dr. M Dakshayini's primary research interests? | 1/5 *(generic guess)* | **5/5** *(Cloud, IoT, Blockchain)* | ✔ Yes |

---

## 3. Qualitative Answer Comparison (Case Studies)

### Case 1: Real-Time Institutional Role
* **Query**: *"Who is the Head of Department of Information Science and Engineering at BMSCE?"*
* **Ground Truth**: Dr. M Dakshayini is the Professor and Head of Department (HOD) of Information Science and Engineering.
* **Baseline LLM**:
  > *"The Head of the Department (HoD) of Information Science and Engineering (ISE) at BMS College of Engineering (BMSCE) is **Dr. P. Jayarekha**."* ❌ *(Hallucinated / outdated)*
* **Knowledge Graph Bot**:
  > *"Based on the department faculty directory, the Head of Department (HOD) of Information Science and Engineering at BMSCE is **Dr. M Dakshayini**. Designation: Professor & HOD, Email: dakshayini.ise@bmsce.ac.in."* ✔ *(100% Accurate & Grounded)*

---

### Case 2: Contact Information & Specific Titles
* **Query**: *"What is Dr. Gowrishankar's email address and current designation?"*
* **Ground Truth**: `gowrishankar.cse@bmsce.ac.in`, Designation: Professor.
* **Baseline LLM**:
  > *"I do not have access to real-time personal directories or private contact information. Therefore, I cannot provide Dr. Gowrishankar's current email address or designation."* ❌ *(Refusal to answer)*
* **Knowledge Graph Bot**:
  > *"Based on the department faculty directory and knowledge graph, Dr. Gowrishankar is a Professor and currently serving as the Chief Coordinator for Data Center & Campus wide Network. Email: gowrishankar.cse@bmsce.ac.in."* ✔ *(Accurate with verified institutional email)*

---

### Case 3: Newly Formed Departments
* **Query**: *"Who is the HOD of the Machine Learning department at BMSCE?"*
* **Ground Truth**: Dr. Sandeep Varma N is the Associate Professor and HOD of Machine Learning.
* **Baseline LLM**:
  > *"As of my last knowledge update (January 2025), the department is headed by Dr. J. Ramesh..."* ❌ *(Hallucination)*
* **Knowledge Graph Bot**:
  > *"The Head of Department for Machine Learning at BMSCE is **Dr. Sandeep Varma N**. Designation: Associate Professor & HOD, Department: Machine Learning."* ✔ *(Precise extraction)*

---

## 4. Knowledge Graph Structural Statistics

The graph was generated from 4 BMSCE faculty profile pages using `GeminiKGBuilder`:

- **Total Triples Extracted**: `195`
- **Total Unique Entities (Nodes)**: `161`
- **Total Directed Relationships (Edges)**: `171`
- **Graph Density**: `0.0066`
- **Degree Centrality Hubs**:
  1. `Dr. Gowrishankar`: 62 connected attributes & publications
  2. `Dr. Sandeep Varma N`: 53 connected attributes & publications
  3. `Dr. M Dakshayini`: 42 connected attributes & publications
  4. `Dr. Monika Puttaramaiah`: 38 connected attributes & publications

---

## 5. Metric Definitions

1. **Factual Accuracy (1–5)**: Evaluates whether the generated response strictly matches verified ground-truth institutional records.
2. **Faithfulness (1–5)**: Evaluates whether the model restricts itself to known retrieved facts without fabricating hallucinated claims.
3. **Answer Relevance (1–5)**: Evaluates how directly and completely the response fulfills the user's inquiry.
4. **KG Retrieval Hit Rate (%)**: Percentage of evaluation queries for which the graph traversal successfully identified and injected the relevant entity facts into context.
5. **1-Hop Entity Expansion**: Graph traversal technique that automatically pulls connected entity attributes (designation, department, contact info) when a core node is identified.

---

## 6. How to Reproduce

To rerun the evaluation benchmark:
```bash
# 1. Ensure your Gemini API key is configured in .env
# 2. Run the automated evaluation harness
python3 evaluate.py
```
Outputs will refresh [`data/evaluation_report.md`](file:///home/laky/Desktop/hackathons/knowledge_bot/data/evaluation_report.md) and [`data/evaluation_report.json`](file:///home/laky/Desktop/hackathons/knowledge_bot/data/evaluation_report.json).
