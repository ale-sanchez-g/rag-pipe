# Productised RAG Pipeline Specification

## 1. Scope and Principles

This platform is a multi-tenant, pack-versioned RAG system where each knowledge pack is a first-class, sellable artefact.

Principles:
- Retrieval-first architecture with a fully model-free retrieval API.
- LLM-agnostic design with optional generation and swappable model providers.
- Strict pack and version isolation to prevent cross-pack leakage.
- Versioned content lifecycle with staged publish and rollback.

## 2. Architecture

### Components
- `packs/`: pack manifests, sample content, and local pack metadata.
- `ingestion/`: loader orchestration, chunking, embedding, and publish staging.
- `retrieval/`: hybrid retrieval orchestration (dense + BM25 + RRF + optional rerank).
- `evaluation/`: schema, duplication, grounding, and regression gates.
- `api/`: FastAPI retrieval API and customer key entitlement checks.
- `mcp/`: MCP wrapper exposing pack query as tool-compatible primitives.
- `golden/`: golden question sets per pack in JSONL.

### Data plane
- One Qdrant collection per `pack_id`.
- Payload metadata includes `pack_id`, `pack_version`, `source_uri`, `section_path`, `ingested_at`, `contributor_id`.
- Mandatory metadata filters on every query (`pack_id` + `pack_version`).

### Control plane
- Ingestion states: `draft -> evaluated -> published`.
- Publish operation only allowed when all gates pass.
- Rollback selects any prior published version.

## 3. Data Contracts

### `manifest.yaml`
Required fields:
- `pack_id`, `pack_version`, `domain_description`, `licence`, `owner`
- `embedding.model`, `embedding.version`
- `chunking.strategy`, `chunking.size`, `chunking.overlap`
- `quality_thresholds.faithfulness_min`, `quality_thresholds.context_precision_min`

### Chunk metadata
Each chunk must include:
- `pack_id`
- `pack_version`
- `source_uri`
- `section_path`
- `ingested_at`
- `contributor_id`

### Golden set
- File path: `golden/{pack_id}.jsonl`
- Minimum 25 Q/A pairs.
- JSONL record: `question`, `answer`, optional `context_hints`.

## 4. Retrieval and API Contracts

### Endpoint
`POST /v1/packs/{pack_id}/query`

Request:
- `query` (string)
- `pack_version` (string, optional; defaults to latest published)
- `top_k` (int)
- `rerank` (bool)

Response:
- `query_id`
- `pack_id`
- `pack_version`
- `results[]` with `text`, `score`, `source_uri`, `section_path`, `chunk_id`

### Auth and tenancy
- API key required on every request.
- Keys map to customer identity and an allow-list of purchased packs.
- Requests for non-entitled packs return 403.

### MCP wrapper
- Exposes retrieval as a tool endpoint that proxies to API contracts.
- Maintains the same entitlement and pack/version constraints.

## 5. Quality Gates

Per ingestion run:
1. Schema gate: all manifest fields valid and metadata coverage = 100%.
2. Duplication gate: near-duplicate detection against existing pack content with cosine > 0.97 flagged or rejected by policy.
3. Grounding gate: RAGAS metrics against golden set with defaults:
   - faithfulness >= 0.85
   - context precision >= 0.75
4. Regression gate: no >2% degradation from previous published version on golden metrics.

Only passing runs transition from `draft` to `evaluated`, then to `published`.

## 6. NFRs and Operations

- Retrieval SLO: p95 latency < 500 ms at 10k chunks per pack.
- Availability SLO: 98%.
- Metrics: retrieval latency, hybrid hit rate, rerank latency, eval scores by pack/version.
- Observability: OpenTelemetry traces across ingest, retrieve, and generate.
- Logging: structured JSON with `pack_id`, `query_id`, `customer_id`; no raw query text at INFO level.
- Static code analysis: SonarQube analysis in CI when repository SonarQube settings are configured.

## 7. Delivery Plan

Phase 1: scaffold and contracts.
Phase 2: ingestion and gates.
Phase 3: hybrid retrieval API and MCP wrapper.
Phase 4: example pack, contributor docs, README runbook and SLO/SLI content.
