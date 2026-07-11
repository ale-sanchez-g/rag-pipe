from pathlib import Path

import pytest
from typer.testing import CliRunner

from ingestion.cli import app

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

runner = CliRunner()


def _write_pack(tmp_path: Path) -> Path:
    (tmp_path / "manifest.yaml").write_text(MANIFEST_YAML, encoding="utf-8")
    (tmp_path / "doc.md").write_text("content", encoding="utf-8")
    return tmp_path


def test_ingest_command_succeeds_for_matching_pack(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)

    result = runner.invoke(
        app,
        [str(pack_dir), "threat-modelling-aws-war", "--contributor-id", "alice"],
    )

    assert result.exit_code == 0
    assert "Ingestion draft complete" in result.stdout


def test_ingest_command_rejects_mismatched_pack_id(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)

    result = runner.invoke(app, [str(pack_dir), "wrong-pack-id"])

    assert result.exit_code != 0
