<div align="center">

# 🎧 Vireo Support Signals

**Local, Explainable Customer Support Signal Analysis & Workload Explorer**

![Python Version](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Standard%20Library)-success?style=for-the-badge)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

<p align="center">
  A zero-dependency, local-first analytics engine designed to extract weekly customer complaint themes, rank recurring signal phrases, and evaluate agent workload contexts from raw support tickets—without sending data to third-party models or cloud APIs.
</p>

[Key Features](#-key-features) • [Architecture](#-system-architecture) • [Quick Start](#-quick-start) • [Schema Mapping](#-column-detection--schema-mapping) • [Mathematical & Algorithmic Foundations](#-mathematical--algorithmic-foundations) • [Executive & CX Strategy](#-executive--cx-strategy)

</div>

---

## 📌 Executive Summary

**Vireo Support Signals** is built to give Customer Experience (CX) leaders, support managers, and operations analysts immediate, data-backed insights into incoming support tickets[cite: 4, 5]. 

By relying on deterministic, rule-based classification rather than opaque generative AI models, the application delivers audit-ready complaint categorization while ensuring **100% data privacy**. All customer interactions, timestamps, and agent metadata remain entirely local to your environment[cite: 5, 6].

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| 🛡️ **100% Local Processing** | Operates strictly in-memory using Python's standard library (`http.server`, `csv`, `re`, `json`). Zero network calls, zero telemetry[cite: 5, 6]. |
| 🔍 **Deterministic Heuristic Classification** | Categorizes ticket opening messages into distinct complaint themes using explicit keyword matching[cite: 5, 6]. |
| 📈 **Weekly Trend Digest** | Groups ticket volumes by calendar week, calculating relative percentage splits per complaint theme[cite: 5, 6]. |
| 🔤 **Document Frequency-Weighted Phrase Scoring** | Identifies top recurring terms across ticket messages while automatically stripping common stop words[cite: 5, 6]. |
| 👥 **Contextual Workload View** | Tracks closed and assigned tickets per agent alongside channel distribution without generating biased performance rankings[cite: 5, 6]. |
| ⚙️ **Fuzzy Schema Matching** | Automatically normalizes and detects varying CSV header naming conventions across different support platforms[cite: 5, 6]. |
| 💻 **Dual Output Modes** | Launches a lightweight HTTP dashboard (`http://127.0.0.1:8765`) or exports standalone static HTML reports[cite: 5, 6]. |

---

## 🏗️ System Architecture

┌───────────────────────────┐
                                  │   Raw Support Datasets    │
                                  │  (tickets.csv / agents)   │
                                  └─────────────┬─────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │   Schema Normalization    │
                                  │   & Date Parsing Engine   │
                                  └─────────────┬─────────────┘
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       ▼                                                 ▼
        ┌─────────────────────────────┐                   ┌─────────────────────────────┐
        │  Weekly Categorization      │                   │   Agent Workload Analysis   │
        │  & Term Ranking             │                   │   & Channel Distribution    │
        └──────────────┬──────────────┘                   └──────────────┬──────────────┘
                       │                                                 │
                       └────────────────────────┬────────────────────────┘
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │    HTML Render Engine     │
                                  │   (BaseHTTPRequestHandler)│
                                  └─────────────┬─────────────┘
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       ▼                                                 ▼
        ┌─────────────────────────────┐                   ┌─────────────────────────────┐
        │    Local Web Interface      │                   │     Static Report File      │
        │   http://127.0.0.1:8765     │                   │       (report.html)         │
        └─────────────────────────────┘                   └─────────────────────────────┘
