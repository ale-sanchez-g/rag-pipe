from pathlib import Path
import typer
from ingestion.manifest import load_manifest
from ingestion.pipeline import discover_documents, ingest_documents
from evaluation.gates import schema_gate

app = typer.Typer(help="Knowledge pack ingestion CLI")


@app.command("ingest")
def ingest(path: Path, pack: str, contributor_id: str = "unknown") -> None:
    manifest_path = path / "manifest.yaml"
    manifest = load_manifest(manifest_path)
    if manifest.pack_id != pack:
        raise typer.BadParameter("--pack must match manifest pack_id")

    docs = discover_documents(path)
    chunks = ingest_documents(manifest=manifest, docs=docs, contributor_id=contributor_id)
    if not schema_gate(manifest=manifest, chunks=chunks):
        raise typer.Exit(code=1)

    typer.echo(f"Ingestion draft complete for {manifest.pack_id}@{manifest.pack_version}: {len(chunks)} chunks")
