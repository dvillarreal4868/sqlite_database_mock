"""
ehr_parser.py
-------------
Functions to extract structured data from Electronic Health Record (EHR) text files.
Each function accepts the raw EHR text string and returns the extracted value(s).
Use `parse_ehr()` to extract all fields at once into a dict, ready for a DataFrame row.
"""

# Imports
from pathlib import Path
import pandas as pd


# ── Low-level helpers ──────────────────────────────────────────────────────────

# def _get_section(text: str, section_name: str) -> str:
#     """Return the raw text block under a given section header."""
#     pattern = rf"{re.escape(section_name)}\s*\n(.*?)(?=\n[A-Z ]+\n|\Z)"
#     match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
#     return match.group(1).strip() if match else ""
#
#
# def _extract_bullets(section_text: str) -> list[str]:
#     """Return a list of bullet-point items from a section block."""
#     return [
#         re.sub(r"^[-•*]\s*", "", line).strip()
#         for line in section_text.splitlines()
#         if re.match(r"\s*[-•*]\s+\S", line)
#     ]
#
#
# def _extract_field(text: str, label: str) -> str:
#     """Extract a single inline field value by label (e.g. 'Age: 49' → '49')."""
#     match = re.search(rf"{re.escape(label)}\s*[:\-]\s*(.+)", text, re.IGNORECASE)
#     return match.group(1).strip() if match else None


# ── Header / metadata ──────────────────────────────────────────────────────────

# Function: Extract Patient IDs
def extract_patient_id(text: str) -> str | None:
    for line in text.splitlines():
        if line.strip().lower().startswith("patient id"):
            return line.split(":")[-1].strip()
    return None


# Function: Extract IRB Protocol
def extract_irb_protocol(text: str) -> str | None:
    for line in text.splitlines():
        if line.strip().lower().startswith("irb protocol"):
            return line.split(":")[-1].strip()
    return None


# Function: Extract Record Date
def extract_record_date(text: str) -> str | None:
    for line in text.splitlines():
        if line.strip().lower().startswith("record date"):
            return line.split(":")[-1].strip()
    return None


# ── Demographics ───────────────────────────────────────────────────────────────

# def extract_age(text: str) -> int | None:
#     """Extract patient age as an integer."""
#     value = _extract_field(_get_section(text, "DEMOGRAPHICS"), "Age")
#     return int(value) if value and value.isdigit() else None
#
#
# def extract_sex(text: str) -> str | None:
#     """Extract patient sex (e.g. 'Male', 'Female')."""
#     return _extract_field(_get_section(text, "DEMOGRAPHICS"), "Sex")


# ── Active Conditions ──────────────────────────────────────────────────────────

# def extract_conditions(text: str) -> list[str]:
#     """Extract list of active conditions."""
#     return _extract_bullets(_get_section(text, "ACTIVE CONDITIONS"))


# ── Medications ───────────────────────────────────────────────────────────────

# def extract_medications(text: str) -> list[str]:
#     """Extract list of current medications (name + dose)."""
#     return _extract_bullets(_get_section(text, "CURRENT MEDICATIONS"))


# ── Vitals ─────────────────────────────────────────────────────────────────────

# def extract_blood_pressure(text: str) -> str | None:
#     """Extract blood pressure string (e.g. '165/67 mmHg')."""
#     return _extract_field(_get_section(text, "VITALS"), "Blood Pressure")
#
#
# def extract_heart_rate(text: str) -> str | None:
#     """Extract heart rate string (e.g. '75 bpm')."""
#     return _extract_field(_get_section(text, "VITALS"), "Heart Rate")
#
#
# def extract_weight(text: str) -> str | None:
#     """Extract weight string (e.g. '77.8 kg')."""
#     return _extract_field(_get_section(text, "VITALS"), "Weight")


# ── Notes ──────────────────────────────────────────────────────────────────────

# def extract_notes(text: str) -> str | None:
#     """Extract free-text clinical notes as a single string."""
#     section = _get_section(text, "NOTES")
#     return " ".join(section.split()) if section else None


# ── Master parser ──────────────────────────────────────────────────────────────

def parse_ehr(texts: list[str]) -> dict:

    """
    Try each extractor against a list of EHR text strings.
    Once a field gets a non-None value, it is considered complete
    and skipped for all remaining texts.
    """

    # Initialize
    extractors = {
        "patient_id":   extract_patient_id,
        "irb_protocol": extract_irb_protocol,
        "record_date":  extract_record_date,
    }

    results = {field: None for field in extractors}

    # Iterate through lines within the txt
    for text in texts:

        # Only run extractors for fields still missing
        pending = {
            field: fn for field, fn in extractors.items() if fn is not None
        }

        # When empty
        if not pending:
            break  # everything is filled, no need to keep going

        # Otherwise attempt to extract
        for field, fn in pending.items():
            value = fn(text)
            if value is not None:
                results[field] = value

    return results

# ── DataFrame builder ──────────────────────────────────────────────────────────

def build_dataframe(file_paths: list[str | Path]) -> pd.DataFrame:
    """
    Given a list of EHR file paths, read each file and return a
    DataFrame with one row per patient.

    Example
    -------
    >>> from pathlib import Path
    >>> files = Path("records/").glob("*.txt")
    >>> df = build_dataframe(files)
    """
    # Initialize
    rows = []
    # Iterate through files
    for path in file_paths:

        # Open
        with open(path, 'r') as f:

            # Read
            text = f.readlines()

        # Parse
        row = parse_ehr(text)

        # Define path
        row["path_ehr"] = str(path)   # keep provenance

        # Append
        rows.append(row)

    return pd.DataFrame(rows)
