from pathlib import Path
import yaml
from ingestion.contracts import PackManifest


def load_manifest(path: Path) -> PackManifest:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return PackManifest.model_validate(data)
