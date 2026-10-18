############################################
# AI Code Review # PROJECT.3, 2026 (C)     #
# -------------10/18/2026----------------- #
# Thi Thuy Tien Ho # thithuytienho@usf.edu #
#------------------------------------------#
# For research and educational use         #
# only, not for clinical decisions.        #
############################################


#!/usr/bin/env python3
"""
Clean healthcare_dataset.csv, compute summary statistics with NumPy, pseudonymize
patient names, and encrypt the complete cleaned dataset with Fernet.

Install:
    pip install pandas numpy cryptography

Run:
    python clean_encrypt_healthcare.py --input healthcare_dataset.csv --outdir secure_output

Security notes:
- The encrypted CSV is the deliverable containing all cleaned patient records.
- The key file is highly sensitive. Store it separately from the encrypted data,
  restrict access, and back it up securely. Anyone with the key can decrypt the data.
- Replacing names with IDs is pseudonymization, not guaranteed anonymization:
  other fields may still permit re-identification.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import stat
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from cryptography.fernet import Fernet


DATE_COLUMNS = ["Date of Admission", "Discharge Date"]
REQUIRED_COLUMNS = [
    "Name", "Age", "Gender", "Blood Type", "Medical Condition",
    "Date of Admission", "Doctor", "Hospital", "Insurance Provider",
    "Billing Amount", "Room Number", "Admission Type", "Discharge Date",
    "Medication", "Test Results",
]

CATEGORY_COLUMNS = [
    "Gender",
    "Blood Type",
    "Medical Condition",
    "Insurance Provider",
    "Admission Type",
    "Medication",
    "Test Results",
]


def load_or_create_key(key_path: Path) -> bytes:
    """Load an existing Fernet key or create one without overwriting an existing key."""
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        key = key_path.read_bytes().strip()
        # Validate key early; Fernet raises ValueError for malformed keys.
        try:
            Fernet(key)
        except(ValueError, TypeError) as exc:
            raise ValueError(f"Invalid Fernet key file:{key_path}") from exc
        return key

    key = Fernet.generate_key()
    # O_EXCL prevents accidentally overwriting a key created by another process.
    fd = os.open(str(key_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(key + b"\n")
    try:
        os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        # Some platforms do not support POSIX permissions; continue with a warning
        print(f"n/Warning: could not restrict permissions on key file {key_path}.", file=sys.stderr)
    return key


def clean_data(input_path: Path) -> tuple[pd.DataFrame, dict]:
    try:
        df = pd.read_csv(input_path, low_memory=False)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError (f"could not read CSV file '{input_path}':{exc}") from exc


    original_rows = len(df)
    original_columns = list(df.columns)

    # Standardize header whitespace and check schema.
    df.columns = [str(c).strip() for c in df.columns]
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValueError(
            "Input file is missing expected columns: " + ", ".join(missing_columns)
        )

    # Preserve every source column; trim whitespace from text fields.
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace("", pd.NA)

    # Convert numeric fields safely.
    age_raw= df["Age"].copy()
    age_numeric = pd.to_numeric(df["Age"], errors="coerce")
    invalid_age_range = age_numeric.notna() & ~age_numeric.between(0, 120)
    invalid_age_text = age_raw.notna() & age_numeric.isna()
    df["Age"] = age_numeric.mask(invalid_age_range).round().astype("Int64")

    billing_raw = df["Billing Amount"].copy()
    billing_numeric = pd.to_numeric(billing_raw, errors="coerce")
    invalid_billing_text = billing_raw.notna() & billing_numeric.isna()
    invalid_billing_value = billing_numeric.notna() & (~np.isfinite(billing_numeric) | (billing_numeric < 0))
    df["Billing Amount"]= billing_numeric.mask(invalid_billing_value)

    room_raw= df["Room Number"].copy()
    room_numeric = pd.to_numeric(room_raw, errors="coerce")
    invalid_room_text = room_raw.notna() & room_numeric.isna()
    invalid_room_value= room_numeric.notna() & ((room_numeric < 0) | (room_numeric % 1 != 0))
    df["Room Number"] = room_numeric.mask(invalid_room_value).astype("Int64")

    # Parse dates; unparseable values become missing.
    for col in DATE_COLUMNS:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Flag contradictory date ranges by nulling the discharge date, rather than
    # silently changing either date.
    invalid_date_order = (
        df["Date of Admission"].notna()
        & df["Discharge Date"].notna()
        & (df["Discharge Date"] < df["Date of Admission"])
    )
    invalid_date_order_count = int(invalid_date_order.sum())
    df.loc[invalid_date_order, "Discharge Date"] = pd.NaT

    # Remove exact duplicate records after basic normalization.
    rows_before_dedup = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    duplicates_removed = rows_before_dedup - len(df)

    # Normalize category-like strings without altering free-text proper names.
    for col in CATEGORY_COLUMNS:
        df[col] = df[col].astype("string").str.strip().str.title()

    report = {
        "input_file": input_path.name,
        "original_rows": int(original_rows),
        "rows_after_cleaning": int(len(df)),
        "duplicates_removed": int(duplicates_removed),
        "unparseable_age_values_set_missing": int(invalid_age_text.sum()),
        "out_of_range_age_values_set_missing": int(invalid_age_range.sum()),
        "unparseable_billing_values_set_missing": int(invalid_billing_text.sum()),
        "invalid_billing_values_set_missing": int(invalid_billing_value.sum()),
        "unparseable_room_values_set_missing": int(invalid_room_text.sum()),
        "invalid_room_numbers_set_missing": int(invalid_room_value.sum()),
        "invalid_date_order_discharge_dates_set_missing": invalid_date_order_count,
        "columns_in_input": original_columns,
        "missing_values_by_column": {
            str(column): int(count) for column, count in df.isna().sum().items()
        },
    }
    return df, report


def add_patient_ids(df: pd.DataFrame, key: bytes) -> pd.DataFrame:
    """Replace names with keyed, stable pseudonymous IDs."""
    from cryptography.fernet import Fernet  # validates key format
    Fernet(key)

    # Derive an HMAC key from the Fernet key material. IDs are deterministic for
    # a given key; never publish the key or the ID mapping.
    import hashlib
    import hmac

    Fernet(key) # Validatw the key before deriving IDs
    hmac_key = __import__("base64").urlsafe_b64decode(key)
    result = df.copy()

    names = result["Name"].fillna("UNKNOWN").astype(str)
    # Include the row position so different records for people with the same
    # name do not automatically receive the same pseudonymous ID. IDs are
    # stable only while the cleaned row order and key remain unchanged.
    result["Patient_ID"] = [
        hmac.new(
            hmac_key, f"{row_number}|{name.casefold()}".encode("utf-8"), hashlib.sha256
        ).hexdigest()[:20]
        for row_number, name in enumerate(names.tolist())
    ]

    result = result.drop(columns=["Name"])
    # Put the pseudonymous identifier first.
    cols = ["Patient_ID"] + [c for c in result.columns if c != "Patient_ID"]
    return result[cols]


def make_statistics(df: pd.DataFrame, cleaning_report: dict) -> dict:
    """Return aggregate statistics; do not include row-level patient data."""
    stats = dict(cleaning_report)

    def numeric_summary(series: pd.Series) -> dict:
        values = (
            pd.to_numeric(series, errors="coerce")
            .dropna()
            .to_numpy(dtype=float)
        )

        if values.size == 0:
            return {
                "n": 0,
                "mean": None,
                "median": None,
                "std_population": None,
                "min": None,
                "max": None,
                "q1": None,
                "q3": None,
            }

        return {
            "n": int(values.size),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std_population": float(np.std(values, ddof=0)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "q1": float(np.percentile(values, 25)),
            "q3": float(np.percentile(values, 75)),
        }

    stats["age"] = numeric_summary(df["Age"])
    stats["billing_amount"] = numeric_summary(df["Billing Amount"])

    stats["category_counts"] = {}
    for col in CATEGORY_COLUMNS:
        stats["category_counts"][col] = {
            str(category): int(count)
            for category, count in df[col].value_counts(
                dropna=False
            ).items()
        }

    valid_dates = (
            df["Date of Admission"].notna()
            & df["Discharge Date"].notna()
    )

    if valid_dates.any():
        stay_days = (
                            df.loc[valid_dates, "Discharge Date"]
                            - df.loc[valid_dates, "Date of Admission"]
                    ).dt.total_seconds() / 86400.0

        stats["length_of_stay_days"] = numeric_summary(stay_days)
    else:
        stats["length_of_stay_days"] = numeric_summary(
            pd.Series(dtype=float)
        )

    return stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean, summarize, pseudonymize, and encrypt healthcare CSV data.")
    parser.add_argument("--input", type=Path, default=Path("healthcare_dataset.csv"))
    parser.add_argument("--outdir", type=Path, default=Path("secure_output"))

    parser.add_argument(
        "--check-only", action="store_true",
        help="Clean and validate the CSV, print a report, and write no output files."
    )
    parser.add_argument(
        "--strict-validation", action="store_true",
        help="Stop if invalid numeric values or contradictory date ranges are found."
    )
    parser.add_argument(
        "--key-file",
        type=Path,
        default=None,
        help="Path to the Fernet key file."
    )
    return parser

def main() -> int:
    args = build_parser().parse_args()
    if not args.input.is_file():
        print(f"Error: input CSV does not exist or is not a file: {args.input}",
              file=sys.stderr)
        return 2

    cleaned, cleaning_report = clean_data(args.input)
    invalid_count_keys = [
        "unparseable_age_values_set_missing",
        "out_of_range_age_values_set_missing",
        "unparseable_billing_values_set_missing",
        "invalid_billing_values_set_missing",
        "unparseable_room_values_set_missing",
        "invalid_room_numbers_set_missing",
        "invalid_date_order_discharge_dates_set_missing",
    ]
    invalid_total = sum(int(cleaning_report[key]) for key in invalid_count_keys)

    print(f"Rows read: {cleaning_report['original_rows']:,}")
    print(f"Rows retained after cleaning: {len(cleaned):,}")
    print(f"Exact duplicates removed: {cleaning_report['duplicates_removed']:,}")
    print(f"Invalid values flagged: {invalid_total:,}")

    if args.strict_validation and invalid_total:
        print(
            "Strict validation failed: invalid values were found. "
            "Review the report by running without --strict-validation or correct the source.",
            file=sys.stderr,
        )
        return 3

    stats = make_statistics(cleaned, cleaning_report)
    if args.check_only:
        print("Check-only mode: no key, encrypted data, or statistics file was written.")
        print(json.dumps(stats, indent=2, allow_nan=False))
        return 0

    args.outdir.mkdir(parents=True, exist_ok=True)
    key_path = args.key_file or (args.outdir / "fernet.key")
    key = load_or_create_key(key_path)
    pseudonymized = add_patient_ids(cleaned, key)

    # Keep patient-level plaintext in memory only; encrypt before writing to disk.
    plaintext_csv = pseudonymized.to_csv(
        index=False, date_format="%Y-%m-%d"
    ).encode("utf-8")
    encrypted_bytes = Fernet(key).encrypt(plaintext_csv)
    encrypted_path = args.outdir / "patient_data.csv.fernet"
    encrypted_path.write_bytes(encrypted_bytes)
    try:
        os.chmod(encrypted_path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        print(f"Warning: could not restrict permissions on {encrypted_path}.",
              file=sys.stderr)

    stats_path = args.outdir / "summary_statistics.json"
    stats_path.write_text(
        json.dumps(stats, indent=2, allow_nan=False), encoding="utf-8"
    )

    print(f"Encrypted patient data: {encrypted_path}")
    print(f"Aggregate statistics: {stats_path}")
    print(f"Fernet key: {key_path}")
    print("\nIMPORTANT: move the key to a separate, access-controlled location and back it up.")
    print("Do not email, commit, or upload the key alongside the encrypted data.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, pd.errors.ParserError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)