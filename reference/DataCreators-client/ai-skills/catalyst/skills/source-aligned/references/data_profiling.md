# Data Profiling Prompt

Profile a source file to extract schema, datatypes, null analysis, and primary key candidates.

## Task

Analyze the provided file and produce a comprehensive profiling table.

## File Analysis Requirements

Before profiling:
1. Use the exact file path provided (no alterations)
2. Identify file type (CSV, DAT, Excel, etc.)
3. Detect delimiter: comma for `.csv`, pipe `|` for `.dat`
4. Try encodings in order: utf-8, latin1, cp1252, iso-8859-1
5. Handle file reading errors gracefully
6. **Header/Trailer detection (required for delimited files):**
    - Scan the file content (for example, by focusing on the first and last ~200 lines, or the entire file for smaller inputs) and compute the **dominant delimiter count** (mode) using Python's `csv.reader` to correctly handle quoted fields (do NOT count raw delimiter characters — quoted commas/pipes must be ignored).
    - Blank lines between preamble and the header row count as preamble rows (include them in `skip_header_rows`, do NOT skip them with `continue`).
    - Treat any leading/trailing lines with a different delimiter count as preamble/trailer.
    - Exclude preamble/trailer lines from profiling and record `skip_header_rows`/`skip_footer_rows` for ingestion.
    - **Note:** This detection runs for ALL flat files. For simple CSVs with no preamble it returns (0, 0) and is a no-op. This is intentional — it catches hidden preamble the user may not know about. If the extra generated code becomes a concern, consider making detection conditional (e.g., skip when the user confirms no preamble).
## Profiling Table Columns

Generate a table with ALL columns from the source file:

| Column | Description |
|--------|-------------|
| Column Name | Exact name as it appears in file |
| Data Type | Inferred type with overrides applied |
| Null Count | Count of null/NaN/empty values |
| Null % | Percentage of nulls |
| Unique Count | Number of distinct values |
| Uniqueness % | unique_count / total_rows × 100 |
| Primary Key Candidate | Yes/No based on rules below |
| Sample Values | Up to 5 distinct sample values |

## Datatype Overrides

Apply these mappings to inferred types:

| Original | Target |
|----------|--------|
| datetime64, datetime, datetime64[ns] | timestamp |
| int64 | int |
| bigint64 | bigint |
| varchar, varchar2, object | string |
| date64 | date |
| float64 | decimal(38,10) |

**Special rule:** If column name contains "date" (case-insensitive), use `date` datatype.

## Primary Key Guidelines

A column is a PK candidate if:
- All values are unique AND no nulls
- Column name contains "uid" or "unique_identifier"
- NOT an amount column (float/decimal like market_value, price, rate)

**Minimality:** The PK should be the minimum columns needed for uniqueness.

**Default behavior:** Use the minimal unique candidate (single column if possible; otherwise the smallest unique combination) as the recommended PK unless the user overrides.

## Python Profiling Code

Run this via terminal:

```python
import csv
import io
import pandas as pd
import os
from collections import Counter

def detect_header_trailer(file_path, delimiter, encoding='utf-8'):
    """Detect preamble/trailer lines by comparing per-line field counts.
    
    Uses csv.reader so quoted fields (e.g. commas inside quotes) are handled
    correctly instead of naive delimiter counting.
    Returns (skip_header_rows, skip_footer_rows).
    """
    with open(file_path, 'r', encoding=encoding) as f:
        raw_lines = f.readlines()

    if not raw_lines:
        return 0, 0

    # Count fields per line using csv.reader (handles quoting)
    field_counts = []
    for line in raw_lines:
        reader = csv.reader(io.StringIO(line), delimiter=delimiter)
        row = next(reader, [])
        field_counts.append(len(row))

    # Dominant field count = mode of non-trivial lines (field_count > 1)
    non_trivial = [c for c in field_counts if c > 1]
    if not non_trivial:
        return 0, 0
    dominant = Counter(non_trivial).most_common(1)[0][0]

    # Leading preamble: lines before the first line matching dominant count
    # Blank lines count as preamble (do NOT skip them)
    skip_header = 0
    for count in field_counts:
        if count == dominant:
            break
        skip_header += 1

    # Trailing footer: lines after the last line matching dominant count
    skip_footer = 0
    for count in reversed(field_counts):
        if count == dominant:
            break
        skip_footer += 1

    return skip_header, skip_footer

def profile_file(file_path, output_dir):
    # Detect delimiter and encoding
    ext = os.path.splitext(file_path)[1].lower()
    delimiter = '|' if ext == '.dat' else ','
    
    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    chosen_enc = 'utf-8'
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                f.read(4096)
            chosen_enc = enc
            break
        except Exception:
            continue

    # Detect header/trailer rows
    skip_header, skip_footer = detect_header_trailer(file_path, delimiter, chosen_enc)
    print(f"Detected: skip_header_rows={skip_header}, skip_footer_rows={skip_footer}")

    df = pd.read_csv(
        file_path, delimiter=delimiter, encoding=chosen_enc,
        skiprows=skip_header,
        skipfooter=skip_footer,
        engine='python' if skip_footer > 0 else 'c',
    )
    
    # Datatype overrides
    dtype_map = {
        "datetime64": "timestamp", "datetime": "timestamp", "datetime64[ns]": "timestamp",
        "int64": "int", "bigint64": "bigint",
        "varchar": "string", "varchar2": "string", "object": "string",
        "date64": "date", "float64": "decimal(38,10)"
    }
    
    def resolve_dtype(col):
        base = str(df[col].dtype).lower()
        if "date" in col.lower() and "time" not in col.lower():
            return "date"
        if "date" in col.lower() and "time" in col.lower():
            return "timestamp"
        return dtype_map.get(base, df[col].dtype.name)
    
    # Null detection (includes empty strings)
    def null_count(col):
        return df[col].isna().sum() + (df[col].astype(str).str.strip() == '').sum()
    
    # PK candidates
    def is_pk_candidate(col):
        nc = null_count(col)
        uc = df[col].nunique()
        dtype = resolve_dtype(col)
        if dtype in ['decimal(38,10)', 'float']:
            return False
        if 'uid' in col.lower() or 'unique_identifier' in col.lower():
            return nc == 0 and uc == len(df)
        return nc == 0 and uc == len(df)
    
    # Build profile
    profile = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": [resolve_dtype(c) for c in df.columns],
        "Null Count": [null_count(c) for c in df.columns],
        "Null %": [round(null_count(c) / len(df) * 100, 2) for c in df.columns],
        "Unique Count": [df[c].nunique() for c in df.columns],
        "Uniqueness %": [round(df[c].nunique() / len(df) * 100, 2) for c in df.columns],
        "Primary Key Candidate": ["Yes" if is_pk_candidate(c) else "No" for c in df.columns],
        "Sample Values": [df[c].dropna().unique()[:5].tolist() for c in df.columns]
    })
    
    # Save to markdown
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'profiling_output.md')
    
    with open(output_path, 'w') as f:
        f.write(f"# Data Profiling Results

")
        f.write(f"**File:** {file_path}
")
        f.write(f"**Rows:** {len(df)}
")
        f.write(f"**Columns:** {len(df.columns)}

")
        f.write("## Profiling Table

")
        f.write(profile.to_markdown(index=False))
        f.write("

## Primary Key Candidates

")
        pks = profile[profile["Primary Key Candidate"] == "Yes"]["Column Name"].tolist()
        f.write(f"Identified PKs: {pks}

")
        f.write("## Columns with 100% Nulls

")
        nulls = profile[profile["Null %"] == 100.0]["Column Name"].tolist()
        f.write(f"Fully null columns: {nulls}
")
    
    print(profile.to_markdown(index=False))
    print(f"
Primary Key Candidates: {pks}")
    print(f"Saved to: {output_path}")
    
    return profile, pks

# Usage
profile_file("PATH_TO_FILE", "OUTPUT_DIR")
```

## Post-Profiling Questions

After displaying the profiling table, ask:

1. **Primary Keys (defaulted):** "I identified these columns as primary key candidates: [list]. I will proceed with the minimal unique PK recommendation unless you want to override."

2. **100% Null Columns (always kept):** "These columns are 100% null: [list]. I will keep them in the model."

3. **Proceed:** "If the profile looks good, do you want me to generate artifacts for a source-aligned data product?"
