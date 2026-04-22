import os
import pandas as pd

REQUIRED_COLUMNS = ["patient_name", "dos", "collector"]
OPTIONAL_COLUMNS = ["claim_number", "insurance_name", "provider_name", "npi", "address"]
ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS

SCHEMA_DOCS = (
    "Expected spreadsheet columns:\n"
    "  Required:\n"
    "    patient_name  – Full name of the patient\n"
    "    dos           – Date of Service (e.g. 01/15/2024 or 2024-01-15)\n"
    "    collector     – Name of the collector assigned to this letter\n"
    "  Optional:\n"
    "    claim_number  – Insurance claim / reference number\n"
    "    insurance_name – Insurance company name\n"
    "    provider_name – Healthcare provider / facility name\n"
    "    npi           – National Provider Identifier\n"
    "    address       – Patient mailing address\n"
)


def load_assignments(file_path):
    """Load and validate assignment rows from a CSV or XLSX file.

    Returns a list of dicts, one per valid row.
    Raises ValueError with a descriptive message when the schema is invalid.
    Raises FileNotFoundError when the file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        try:
            df = pd.read_csv(file_path)
        except Exception as exc:
            raise ValueError(f"Failed to read CSV file: {exc}") from exc
    elif ext in (".xlsx", ".xls"):
        try:
            df = pd.read_excel(file_path)
        except Exception as exc:
            raise ValueError(f"Failed to read Excel file: {exc}") from exc
    else:
        raise ValueError(
            f"Unsupported file format '{ext}'. Please use .csv, .xlsx or .xls.\n"
            + SCHEMA_DOCS
        )

    # Normalise column names: strip whitespace, lowercase, replace spaces with _
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    # Check required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required column(s): {', '.join(missing)}\n\n" + SCHEMA_DOCS
        )

    # Drop rows where any required field is blank
    before = len(df)
    df = df.dropna(subset=REQUIRED_COLUMNS)
    skipped = before - len(df)

    if df.empty:
        raise ValueError(
            "No valid rows found in the input file "
            "(all rows are missing one or more required fields).\n\n" + SCHEMA_DOCS
        )

    # Normalise DOS to a consistent string representation
    if "dos" in df.columns:
        df["dos"] = df["dos"].apply(_normalise_date)

    records = df.to_dict(orient="records")

    # Convert NaN optional fields to empty strings
    for record in records:
        for col in OPTIONAL_COLUMNS:
            val = record.get(col)
            if val is None or (isinstance(val, float) and str(val) == "nan"):
                record[col] = ""
            else:
                record[col] = str(val).strip()

    return records, skipped


def _normalise_date(value):
    """Return a sanitised date string, keeping the original if parsing fails."""
    if pd.isna(value):
        return "00-00-0000"
    # If pandas already parsed it as a Timestamp, format it
    if hasattr(value, "strftime"):
        return value.strftime("%m-%d-%Y")
    text = str(value).strip()
    # Replace slashes with dashes for filename safety
    text = text.replace("/", "-")
    return text
