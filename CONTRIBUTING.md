# Contributing Knowledge Pack Content

## Purpose

This repository hosts versioned knowledge packs for retrieval systems. Content quality and traceability are mandatory.

## Document Structure

- Place pack content under `packs/<pack_id>/docs/`.
- Include a pack `manifest.yaml` at `packs/<pack_id>/manifest.yaml`.
- Supported source formats: PDF, Markdown, HTML, DOCX.

## Required Metadata and Manifest Fields

Every pack manifest must include:
- `pack_id`, `pack_version`, `domain_description`, `licence`, `owner`
- `embedding.model`, `embedding.version`
- `chunking.strategy`, `chunking.size`, `chunking.overlap`
- `quality_thresholds` (faithfulness, context precision, regression budget)

Each generated chunk must carry:
- `pack_id`, `pack_version`, `source_uri`, `section_path`, `ingested_at`, `contributor_id`

## Quality Gates

Each ingestion must pass all gates before publication:
1. **Schema gate**: valid manifest and complete chunk metadata.
2. **Duplication gate**: near-duplicate detection (cosine > 0.97 policy).
3. **Grounding gate**: RAGAS thresholds against golden set.
4. **Regression gate**: no more than 2% degradation from previous version.

State transitions are `draft -> evaluated -> published`.

## Golden Set Requirements

- Add `golden/<pack_id>.jsonl`.
- Include at least 25 question/answer pairs.
- Keep questions specific to pack scope and answerable from included content.

## Local Workflow

1. Install dependencies.
2. Run ingest CLI:
   - `pack ingest packs/<pack_id> --pack <pack_id> --contributor-id <your_id>`
3. Run tests:
   - `pytest`
   - `pytest -m unit`
   - `pytest -m e2e`
   - `pytest -m security`
   - `pytest -m performance`

## CI/CD and SonarQube Expectations

- Pull requests run the CI test stages for unit, end-to-end, security, and performance suites.
- Pushes to `main` run tests plus package build.
- Version tags matching `v*` trigger release publication (for example `v1.0.0`).
- SonarQube analysis runs when `SONAR_PROJECT_KEY` (variable) and `SONAR_HOST_URL` and `SONAR_TOKEN` (secrets) are configured in the repository settings.
- When adding or renaming source modules, update `sonar.sources` in `.github/workflows/ci.yml`.

Use Australian English for all documentation updates.
