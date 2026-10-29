# 📊 Knowledge Graph Help Bot - Evaluation Report

## 1. Executive Summary
- **Retrieval Hit Rate**: 100.0%
- **Factual Accuracy Uplift**: 1.00/5.0 → **5.00/5.0** (+400.0%)
- **Faithfulness (Anti-Hallucination)**: 4.33/5.0 → **5.00/5.0**
- **Average Latency**: 36.68s

## 2. Head-to-Head Comparison Table

| ID | Test Query | Baseline (No KG) | With KG (Graph-RAG) | KG Grounded? |
|---|---|:---:|:---:|:---:|
| 1 | Who is the Head of Department of Information Science and Engineering at BMSCE? | 1/5 | **5/5** | ✔ Yes |
| 2 | What is Dr. Gowrishankar's email address and current designation? | 1/5 | **5/5** | ✔ Yes |
| 3 | Who is the HOD of the Machine Learning department at BMSCE? | 1/5 | **5/5** | ✔ Yes |
| 4 | What is Dr. Monika Puttaramaiah's designation and department? | 1/5 | **5/5** | ✔ Yes |
| 5 | Where did Dr. Gowrishankar receive his PhD from and in which year? | 1/5 | **5/5** | ✔ Yes |
| 6 | What are Dr. M Dakshayini's primary research interests? | 1/5 | **5/5** | ✔ Yes |

## 3. Metric Definitions
1. **Factual Accuracy**: Degree to which response matches institutional ground truth facts.
2. **Faithfulness**: Absence of fabricated information / hallucinations.
3. **KG Retrieval Hit Rate**: Percentage of queries where graph successfully retrieved required entity triples.
