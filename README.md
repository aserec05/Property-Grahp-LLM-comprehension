# LLMs' Understanding of Queries on Property Graphs

**Authors:** Thomas CERESA, Lucca HOOGENBOSCH
**Date:** February 2025
**Supervisors:** Angela Bonifati (HDR), Andrea Mauri (PhD)
**Laboratory:** LIRIS, Claude Bernard University Lyon 1

---

## Abstract

This project explores how Large Language Models (LLMs) understand and process queries on property graphs, focusing on Cypher (Neo4j) and natural language. The goal is to evaluate LLMs' ability to interpret graph queries, generate Cypher code, and return accurate results. The work was conducted as part of the "Ouverture à la Recherche" course and involved both literature review and experimental implementation.

**Keywords:** LLM, Property Graph, Reasoning, Cypher, Neo4j

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Pipelines](#pipelines)
- [Graph Schema](#graph-schema)
- [Installation](#installation)
- [Usage](#usage)
- [Results](#results)
- [Limitations](#limitations)
- [Future Work](#future-work)
- [References](#references)
- [Contacts](#contacts)

---

## Introduction

### Context

This project was developed during a research internship (April–July 2024) at LIRIS Laboratory, Claude Bernard University Lyon 1. The focus was on studying how LLMs interpret and generate queries for property graphs, especially in the context of Cypher and natural language.

### Objectives

- Evaluate LLMs' ability to reason about property graphs.
- Compare different pipelines for query interpretation and execution.
- Assess the accuracy, performance, and linguistic understanding of LLMs in generating Cypher queries.

---

## Features

- **Five Pipelines:** Different approaches to process graph queries using LLMs and Neo4j.
- **Graph Encoding:** Hybrid encoding of property graphs for LLM interpretation.
- **Query Evaluation:** Support for schema discovery, analytical, and aggregate queries.
- **Automatic Testing:** Framework to evaluate LLMs' responses against Neo4j results.

---

## Pipelines

| Pipeline | Description |
|----------|-------------|
| **Pipeline 1** | Plain text graph + Cypher query → LLM → JSON result. |
| **Pipeline 2** | Graph schema + natural language query → LLM → Cypher query → Neo4j → JSON result. |
| **Pipeline 3** | Plain text graph + natural language query → LLM → JSON result. |
| **Pipeline Neo4j** | Direct execution of Cypher queries in Neo4j (baseline). |

---

## Graph Schema

The project uses a schema based on the **World Cup 2019 graph** (Neo4j example). The schema includes nodes like `Match`, `Person`, `Team`, and `Tournament`, with relationships such as `SCORED_GOAL`, `PARTICIPATED_IN`, and `REPRESENTS`.

Example:
```json
[
    {"StartLabels": ["Match"], "RelationshipType": "IN_TOURNAMENT", "EndLabels": ["Tournament"]},
    {"StartLabels": ["Person"], "RelationshipType": "SCORED_GOAL", "EndLabels": ["Match"]}
]
```

---

## Installation

### Prerequisites

- Python 3.8+
- Neo4j (for Pipeline Neo4j)
- Ollama (for local LLM)
- Required libraries: `networkx`, `langchain`, `chatollama`

### Setup

1. Clone the repository:
   ```bash
   git clone https://forge.univ-lyon1.fr/p2105653/ouverture-recherche.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Neo4j and Ollama according to the [documentation](Doc/).

---

## Usage

1. **Run the framework:**
   ```bash
   python main.py
   ```

2. **Test pipelines:**
   - Results are saved in the `results/` directory.
   - Queries and natural language questions are located in `requests/`.

3. **Evaluate results:**
   - Compare LLM-generated results with Neo4j outputs.
   - Use the predefined JSON format for consistency.

---

## Results

### Pipeline 1 (LLM-only)
- **Average Score:** 2.54/5
- **Strengths:** Good for simple queries.
- **Weaknesses:** Struggles with aggregates, paths, and complex properties.

### Pipeline 2 (LLM + Neo4j)
- **Observation:** Ollama struggles to generate correct Cypher queries, unlike ChatGPT-3.5.
- **Conclusion:** Natural language ambiguity affects query accuracy.

---

## Limitations

- **Token Limit:** Ollama's 2048-token limit restricts graph size.
- **Naive Encoding:** Hybrid encoding is not optimized for properties and labels.
- **LLM Variability:** Performance varies significantly between LLMs (e.g., Ollama vs. ChatGPT-3.5).

---

## Future Work

- Improve graph encoding for better LLM comprehension.
- Test larger graphs and more LLMs.
- Integrate schema encoding to enhance query accuracy.
- Explore PGDF (Property Graph Data Format) for interoperability.

---

## References

1. R. Angles, *The Property Graph Database Model*, 2018.
2. ISO/IEC 39075:2024, *GQL Standard*, 2024.
3. Halcrow & Perozzi, *Talk Like a Graph: Encoding Graphs for LLMs*, 2023.
4. Neo4j, *World Cup 2019 Graph*, 2019.

Full references are available in the [report](Report.pdf).

---

## Contacts

For questions or feedback, contact:
- **Thomas Ceresa:** [thomas.ceresa@univ-lyon1.fr](mailto:thomas.ceresa@univ-lyon1.fr)
- **Lucca Hoogenbosch:** [lucca.hoogenbosch@univ-lyon1.fr](mailto:lucca.hoogenbosch@univ-lyon1.fr)
- **Andrea Mauri:** [andrea.mauri@univ-lyon1.fr](mailto:andrea.mauri@univ-lyon1.fr)
