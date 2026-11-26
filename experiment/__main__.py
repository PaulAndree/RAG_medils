"""python -m RAG_medils.experiment {ingest,index,evaluate,run,create-user}"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from RAG_medils.experiment import TENANT_ID
from RAG_medils.ingest import RAG_ROOT

DEFAULT_DATA_DIR = RAG_ROOT / "data"
DEFAULT_QUESTIONS = RAG_ROOT / "evaluation" / "questions_easy.json"
DEFAULT_RESULTS = RAG_ROOT / "evaluation" / "results"


def _types(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _add_ingest_args(parser: argparse.ArgumentParser) -> None:
    from RAG_medils.experiment.ingest import DEFAULT_WORK_DIR

    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK_DIR,
                        help="Rendered Markdown, per-document checkpoints and level files")
    parser.add_argument("--types", type=_types, default=None,
                        help="Comma list of chat,document,email,event,note,task (default: all)")
    parser.add_argument("--limit", type=int, default=None, help="Records per type (smoke tests)")
    parser.add_argument("--workers", type=int, default=None, help="Parallel documents (default RAPTOR_MAX_WORKERS)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--resume", dest="clean", action="store_false",
                      help="Reuse per-document checkpoints (default)")
    mode.add_argument("--clean", action="store_true",
                      help="Delete this tenant's rows and generated files first")
    parser.set_defaults(clean=False)


def _add_evaluate_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--out", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--limit-questions", type=int, default=None)
    if not any(action.dest == "data_dir" for action in parser._actions):
        parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m RAG_medils.experiment", description=__doc__)
    parser.add_argument("--tenant", default=TENANT_ID, help=f"Tenant / catalog (default {TENANT_ID})")
    commands = parser.add_subparsers(dest="command", required=True)
    _add_ingest_args(commands.add_parser("ingest", help="Render, register, build RAPTOR nodes, store in PostgreSQL"))
    commands.add_parser("index", help="Rebuild the Qdrant collection from PostgreSQL and swap the live alias")
    _add_evaluate_args(commands.add_parser("evaluate", help="Compute retrieval metrics over the questions"))
    run = commands.add_parser("run", help="ingest + index + evaluate")
    _add_ingest_args(run)
    _add_evaluate_args(run)
    user = commands.add_parser("create-user", help="Create a chat UI user for the tenant")
    user.add_argument("username")
    return parser.parse_args(argv)


def _ingest(args: argparse.Namespace) -> int:
    from RAG_medils.experiment.ingest import run_ingest

    return run_ingest(
        data_dir=args.data_dir,
        tenant_id=args.tenant,
        work_dir=args.work_dir,
        types=args.types,
        limit=args.limit,
        clean_first=args.clean,
        workers=args.workers,
    )


def _index(_: argparse.Namespace) -> int:
    from RAG_medils.ingest.indexing.main import run_pipeline

    run_pipeline()
    return 0


def _evaluate(args: argparse.Namespace) -> int:
    from RAG_medils.experiment.evaluate import run_evaluation

    run_evaluation(
        questions_path=args.questions,
        data_dir=args.data_dir,
        tenant_id=args.tenant,
        out_dir=args.out,
        k=args.k,
        limit=args.limit_questions,
    )
    return 0


def _create_user(args: argparse.Namespace) -> int:
    from getpass import getpass

    from pwdlib import PasswordHash

    from RAG_medils.ingest.stores.database_postgres import get_connection

    password = getpass("Password: ")
    if not password or password != getpass("Confirm password: "):
        print("Passwords must be nonempty and match", file=sys.stderr)
        return 1
    with get_connection() as conn:
        if conn.execute("SELECT to_regclass('users')").fetchone()[0] is None:
            print("users table missing: run retrieval_and_generation/auth.sql first", file=sys.stderr)
            return 1
        conn.execute("INSERT INTO tenants (id) VALUES (%s) ON CONFLICT DO NOTHING", (args.tenant,))
        conn.execute(
            "INSERT INTO users (username, password_hash, tenant_id) VALUES (%s, %s, %s) "
            "ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash, "
            "tenant_id = EXCLUDED.tenant_id, is_active = TRUE",
            (args.username, PasswordHash.recommended().hash(password), args.tenant),
        )
    print(f"user {args.username} can now log in to tenant {args.tenant}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "ingest":
        return _ingest(args)
    if args.command == "index":
        return _index(args)
    if args.command == "evaluate":
        return _evaluate(args)
    if args.command == "create-user":
        return _create_user(args)
    if args.command == "run":
        for step in (_ingest, _index, _evaluate):
            status = step(args)
            if status:
                return status
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
