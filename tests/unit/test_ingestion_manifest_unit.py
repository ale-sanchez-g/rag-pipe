from pathlib import Path

import pytest

from ingestion.manifest import load_manifest

pytestmark = pytest.mark.unit

MANIFEST_YAML = """
pack_id: threat-modelling-aws-war
pack_version: "1.0.0"
domain_description: desc
licence: MIT
owner: owner
embedding:
  model: BAAI/bge-large-en-v1.5
  version: "1.5"
chunking:
  strategy: semantic
  size: 800
  overlap: 120
quality_thresholds:
  faithfulness_min: 0.85
  context_precision_min: 0.75
  max_regression_pct: 2.0
"""


def test_load_manifest_parses_yaml(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text(MANIFEST_YAML, encoding="utf-8")

    manifest = load_manifest(manifest_path)

    assert manifest.pack_id == "threat-modelling-aws-war"
    assert manifest.pack_version == "1.0.0"
    assert manifest.chunking.size == 800
