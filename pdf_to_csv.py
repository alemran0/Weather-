"""
pdf_to_csv.py
Reads 'Cyclone - Met BAF.pdf' (Climate of Jessore, Bangladesh) and writes
all structured data tables to CSV files.

Output files
------------
extreme_weather.csv       – 12 extreme weather records (PDF page 10)
monthly_wind.csv          – Monthly max wind direction & speed, 1984-2013 (PDF page 46)
monthly_rainfall.csv      – Monthly total rainfall (mm), 1984-2013 (PDF page 47)
monthly_rainy_days.csv    – Monthly total rainy days, 1984-2013 (PDF page 48)
"""

import csv
import re
import pdfplumber

PDF_FILE = "Cyclone - Met BAF.pdf"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean(value):
    """Strip whitespace and normalise newlines inside a cell."""
    if value is None:
        return ""
    return " ".join(str(value).split())


def write_csv(filename, rows, fieldnames=None):
    """Write *rows* (list of lists or list of dicts) to *filename*."""
    if not rows:
        return
    with open(filename, "w", newline="", encoding="utf-8") as fh:
        if fieldnames:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        else:
            writer = csv.writer(fh)
            writer.writerows(rows)
    print(f"  Written: {filename}  ({len(rows)} data rows)")


# ---------------------------------------------------------------------------
# Extract tables
# ---------------------------------------------------------------------------

def extract_tables_from_pages(pdf, page_numbers):
    """Return all pdfplumber tables found on the given 1-based page numbers."""
    tables = []
    for pnum in page_numbers:
        page = pdf.pages[pnum - 1]
        for tbl in page.extract_tables():
            tables.append(tbl)
    return tables


# ---------------------------------------------------------------------------
# Table 1 – Extreme weather records  (page 10)
# ---------------------------------------------------------------------------

def build_extreme_weather(pdf):
    tables = extract_tables_from_pages(pdf, [10])
    if not tables:
        print("  WARNING: extreme weather table not found on page 10")
        return

    raw = tables[0]
    fieldnames = ["Ser_No", "Met_Element", "Value", "Date_Time_of_Occurrence"]
    rows = []
    for row in raw[1:]:           # skip header row
        if len(row) < 4:
            continue
        rows.append({
            "Ser_No":                  clean(row[0]),
            "Met_Element":             clean(row[1]),
            "Value":                   clean(row[2]),
            "Date_Time_of_Occurrence": clean(row[3]),
        })

    write_csv("extreme_weather.csv", rows, fieldnames)


# ---------------------------------------------------------------------------
# Table 2 – Monthly max wind direction & speed  (page 46)
# ---------------------------------------------------------------------------

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def build_monthly_wind(pdf):
    tables = extract_tables_from_pages(pdf, [46])
    if not tables:
        print("  WARNING: monthly wind table not found on page 46")
        return

    raw = tables[0]
    fieldnames = ["Year"] + MONTHS
    rows = []
    for row in raw[1:]:           # skip header row
        if not row or not clean(row[0]):
            continue
        year = clean(row[0])
        if not re.match(r"^\d{4}$", year):
            continue
        entry = {"Year": year}
        for i, month in enumerate(MONTHS):
            val = clean(row[i + 1]) if i + 1 < len(row) else ""
            entry[month] = val if val not in ("", "-") else ""
        rows.append(entry)

    write_csv("monthly_wind.csv", rows, fieldnames)


# ---------------------------------------------------------------------------
# Table 3 – Monthly total rainfall (mm)  (page 47)
# ---------------------------------------------------------------------------

def build_monthly_rainfall(pdf):
    tables = extract_tables_from_pages(pdf, [47])
    if not tables:
        print("  WARNING: monthly rainfall table not found on page 47")
        return

    raw = tables[0]
    fieldnames = ["Year"] + MONTHS
    rows = []
    for row in raw[1:]:
        if not row or not clean(row[0]):
            continue
        year = clean(row[0])
        if not re.match(r"^\d{4}$", year):
            continue
        entry = {"Year": year}
        for i, month in enumerate(MONTHS):
            val = clean(row[i + 1]) if i + 1 < len(row) else ""
            # Normalise "Nil" to 0
            entry[month] = "0" if val.lower() == "nil" else val
        rows.append(entry)

    write_csv("monthly_rainfall.csv", rows, fieldnames)


# ---------------------------------------------------------------------------
# Table 4 – Monthly total rainy days  (page 48)
# ---------------------------------------------------------------------------

def build_monthly_rainy_days(pdf):
    tables = extract_tables_from_pages(pdf, [48])
    if not tables:
        print("  WARNING: monthly rainy days table not found on page 48")
        return

    raw = tables[0]
    fieldnames = ["Year"] + MONTHS
    rows = []
    for row in raw[1:]:
        if not row or not clean(row[0]):
            continue
        year = clean(row[0])
        if not re.match(r"^\d{4}$", year):
            continue
        entry = {"Year": year}
        for i, month in enumerate(MONTHS):
            val = clean(row[i + 1]) if i + 1 < len(row) else ""
            entry[month] = "0" if val.lower() == "nil" else val
        rows.append(entry)

    write_csv("monthly_rainy_days.csv", rows, fieldnames)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Opening: {PDF_FILE}")
    with pdfplumber.open(PDF_FILE) as pdf:
        print(f"Pages: {len(pdf.pages)}\n")

        print("Extracting extreme weather records…")
        build_extreme_weather(pdf)

        print("Extracting monthly max wind direction & speed…")
        build_monthly_wind(pdf)

        print("Extracting monthly total rainfall…")
        build_monthly_rainfall(pdf)

        print("Extracting monthly total rainy days…")
        build_monthly_rainy_days(pdf)

    print("\nDone.")


if __name__ == "__main__":
    main()
