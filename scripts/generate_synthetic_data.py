"""Generate the reviewed synthetic visa demo dataset."""

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from visa_assist.config import Settings  # noqa: E402
from visa_assist.database.session import (  # noqa: E402
    create_database_engine,
    create_session_factory,
)
from visa_assist.synthetic import (  # noqa: E402
    SyntheticDataExistsError,
    generate_synthetic_data,
)


def parse_args() -> argparse.Namespace:
    """Parse synthetic data generation options."""
    parser = argparse.ArgumentParser(
        description="Generate coherent synthetic visa application journeys."
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Deterministic seed; defaults to SYNTHETIC_DATA_SEED.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing synthetic users in one transaction.",
    )
    return parser.parse_args()


def main() -> int:
    """Generate and report the configured synthetic dataset."""
    args = parse_args()
    settings = Settings()
    seed = settings.synthetic_data_seed if args.seed is None else args.seed
    engine = create_database_engine(settings.database_url)
    factory = create_session_factory(engine)

    try:
        summary = generate_synthetic_data(factory, seed=seed, replace=args.replace)
    except SyntheticDataExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    finally:
        engine.dispose()

    print("Synthetic dataset generated:")
    for name, value in asdict(summary).items():
        print(f"  {name}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
