# Food Data Pipeline

An end-to-end ELT data pipeline that ingests food product data from a public API,
lands it in cloud storage, loads it into a data warehouse, and transforms it into
clean, analytics-ready tables — all orchestrated to run on a schedule.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![dbt](https://img.shields.io/badge/dbt-transform-orange)
![BigQuery](https://img.shields.io/badge/BigQuery-warehouse-blue)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED)
![Status](https://img.shields.io/badge/status-in%20progress-yellow)

---

## Overview

This project builds a realistic, production-style data pipeline around **food and grocery
product data**: nutrition facts, brands, categories, and ingredients pulled from the
[Open Food Facts](https://world.openfoodfacts.org/data) open database.

The goal is to demonstrate the core workflow of modern data engineering — extracting data
from an external source, storing raw and processed copies, modeling it for analytics, and
running the whole thing on a schedule — using the kind of tooling found in real data teams.

It is built in phases. Each phase is a self-contained milestone, so the project is useful
and runnable well before every feature is finished. See the [Roadmap](#roadmap) for current
status.

## Architecture

```
                  ┌─────────────────────────────────────────────────────────────┐
                  │   Orchestrated on a schedule  (Airflow / Cloud Composer)      │
                  └─────────────────────────────────────────────────────────────┘
                            │            │            │            │
  ┌──────────┐     ┌──────────────┐   ┌──────────┐   ┌───────────┐   ┌────────────┐
  │  Source  │ ──▶ │   Extract    │──▶│ Raw zone │──▶│ Warehouse │──▶│ Transform  │
  │ Food API │     │ Python · REST│   │ GCS +    │   │ BigQuery  │   │ dbt models │
  │          │     │              │   │ NoSQL    │   │ (SQL)     │   │ dim / fact │
  └──────────┘     └──────────────┘   └──────────┘   └───────────┘   └────────────┘

  Stretch goal — streaming layer (Kubernetes / GKE):
      ┌──────────────┐     ┌──────────────────┐
      │ Kafka topic  │ ──▶ │ Stream consumer  │ ──▶ raw zone
      └──────────────┘     └──────────────────┘
```

The **batch pipeline** (the main flow) is built first. The **streaming layer** is an optional
extension that adds real-time event processing on top of the same warehouse.

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| Language | Python | Extraction logic, glue code |
| Source | Open Food Facts REST API | Free, large, food-domain dataset |
| Raw storage | Google Cloud Storage + a document/NoSQL store | Keep an immutable copy of raw responses |
| Warehouse | BigQuery | Cloud SQL warehouse for analytics |
| Transformation | dbt | Modeling, testing, documentation, lineage |
| Orchestration | Airflow (locally) / Cloud Composer (on GCP) | Scheduling and reliable re-runs |
| Packaging | Docker + Docker Compose | One-command local setup |
| Streaming (stretch) | Kafka + Kubernetes (GKE) | Real-time event processing |

## Data source

Data comes from [Open Food Facts](https://world.openfoodfacts.org/data), a free and open
database of food products from around the world. It exposes a REST API returning product
records with fields like product name, brand, categories, nutrition facts (energy, sugar,
fat, salt), and ingredient lists.

No API key is required. The pipeline respects the API's rate limits and paginates through
results during extraction.

## Data model

Raw API responses are loaded as-is, then progressively cleaned and reshaped into a small
analytics model:

- **Staging** — lightly cleaned, one row per source record, consistent column names and types.
- **Dimensions** — `dim_product`, `dim_brand`, `dim_category`.
- **Facts** — `fct_nutrition`, holding per-product nutrition measures.

Each model includes dbt tests (e.g. uniqueness and not-null on keys) and documentation, so the
warehouse is verifiable rather than just populated.

## Project structure

```
food-data-pipeline/
├── extract/              # Python extraction from the Open Food Facts API
├── load/                 # Loading raw data into storage and the warehouse
├── transform/            # dbt project (staging, dimensions, facts, tests, docs)
├── orchestration/        # Airflow DAGs / pipeline schedules
├── streaming/            # (Stretch) Kafka producer + consumer
├── docker-compose.yml    # Local stack: warehouse, orchestrator, services
├── .env.example          # Template for environment variables
└── README.md
```

## Getting started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- (For the cloud phase) A Google Cloud account with the free tier enabled

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/food-data-pipeline.git
cd food-data-pipeline

# 2. Create your environment file from the template and fill in values
cp ..env .env

# 3. Start the local stack (warehouse, orchestrator, etc.)
docker compose up
```

### Running the pipeline

```bash
# Trigger the full extract -> load -> transform run
# (exact command depends on the orchestrator; see orchestration/)
```

Once running, open the orchestrator UI to watch the pipeline execute and inspect each step.

## Roadmap

The project is built in phases. Completed work is checked off below.

- [x] **Phase 0 — Project setup:** repo, environment, README, base structure
- [x] **Phase 1 — Extract:** pull and paginate food data from the Open Food Facts API in Python
- [x] **Phase 2 — Load:** store raw responses (NoSQL) and a structured copy (SQL)
- [Current ] **Phase 3 — Transform:** build staging, dimension, and fact models in dbt, with tests and docs
- [ ] **Phase 4 — Orchestrate:** schedule the pipeline and make runs idempotent; containerize with Docker Compose
- [ ] **Phase 5 — Cloud:** deploy on GCP (Cloud Storage, BigQuery, Cloud Composer)
- [ ] **Phase 6 — Streaming (stretch):** add a Kafka stream and consumer, deployed on Kubernetes (GKE)


## Engineering practices

This project is intentionally built to reflect how real data teams work:

- **Idempotent loads** — re-running the pipeline does not create duplicate data.
- **Tested transformations** — dbt tests validate keys and critical fields on every run.
- **Documented models** — dbt docs describe each table and its lineage.
- **Reproducible setup** — the full stack runs locally with a single `docker compose up`.
- **Raw data preserved** — an immutable copy of source data is always kept, so the warehouse can be rebuilt from scratch.

## Acknowledgements

Product data provided by [Open Food Facts](https://world.openfoodfacts.org), made available
under the Open Database License (ODbL).

## License

Released under the MIT License. See `LICENSE` for details.
