""" Main script that should be run to ingest documents and chunk JSON files into PostgreSQL. """
import argparse
import sys
from pathlib import Path

from stores.database_postgres import (
    create_tables,
    find_stale_source_keys,
    persist_document,
)
from stores.ingestion import (
    FolderScanError,
    derive_source_identity,
    discover_chunk_files,
    prepare_document,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest chunk JSON files into PostgreSQL."
    )

    parser.add_argument(
        "--chunks-dir",
        type=Path,
        default=Path("data/pdf_parsed_output"),
        help="Directory containing *_chunks.json files.",
    )

    parser.add_argument(
        "--pdf-dir",
        type=Path,
        default=Path("data/pdf_docs"),
        help="Directory containing matching PDF files.",
    )

    return parser.parse_args()

def run_ingestion(
    chunks_root: Path,
    pdf_root: Path,
) -> int:
    try:
        json_files = discover_chunk_files(chunks_root)
    except FolderScanError as exc:
        print(f"[fatal] {exc}", file=sys.stderr)
        return 1

    try:
        create_tables()
    except Exception as exc:
        print(
            f"[fatal] could not initialize PostgreSQL schema: {exc}",
            file=sys.stderr,
        )
        return 1

    counts = {
        "inserted": 0,
        "skipped": 0,
        "failed": 0,
    }

    discovered_source_keys: set[str] = set()

    for json_path in json_files:
        display_path = json_path.relative_to(
            chunks_root.resolve()
        )

        try:
            source_key, _, _ = derive_source_identity(
                json_path,
                chunks_root,
            )
            discovered_source_keys.add(source_key)

            document = prepare_document(
                json_path=json_path,
                chunks_root=chunks_root,
                pdf_root=pdf_root,
            )

            for warning in document.warnings:
                print(
                    f"[warning] {document.source_key}: {warning}"
                )

            result = persist_document(document)
            counts[result.action] += 1

            print(
                f"[{result.action}] "
                f"{result.source_key} "
                f"version={result.version} "
                f"chunks={result.chunk_count}"
            )

        except Exception as exc:
            counts["failed"] += 1
            print(
                f"[failed] {display_path}: {exc}",
                file=sys.stderr,
            )

    #detects database documents whose source JSON file is no longer present.
    try:
        stale_source_keys = find_stale_source_keys(
            discovered_source_keys
        )
    except Exception as exc:
        print(
            f"[fatal] could not check stale documents: {exc}",
            file=sys.stderr,
        )
        return 1

    for source_key in stale_source_keys:
        print(
            f"[stale] {source_key}: "
            "source JSON was not found; database rows were preserved"
        )

    print()
    print("Ingestion summary")
    print(f"  discovered: {len(json_files)}")
    print(f"  inserted:   {counts['inserted']}")
    print(f"  skipped:    {counts['skipped']}")
    print(f"  failed:     {counts['failed']}")
    print(f"  stale:      {len(stale_source_keys)}")

    if counts["failed"] > 0:
        return 1

    return 0


def main() -> int:
    args = parse_args()

    return run_ingestion(
        chunks_root=args.chunks_dir,
        pdf_root=args.pdf_dir,
    )


if __name__ == "__main__":
    raise SystemExit(main())