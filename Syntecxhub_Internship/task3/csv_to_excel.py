
import argparse
import logging
import sys
from pathlib import Path

import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


def convert_csv_to_excel(input_file, output_file):
    """Read, clean, and convert a CSV file into an Excel workbook."""

    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix.lower() != ".csv":
        raise ValueError("The input file must be a CSV file.")

    if output_path.suffix.lower() != ".xlsx":
        raise ValueError("The output file must have an .xlsx extension.")

    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output files must be different.")

    logging.info("Reading CSV file: %s", input_path)

    df = pd.read_csv(input_path)

    if df.empty or len(df.columns) == 0:
        raise ValueError("The CSV file contains no data.")

    # Normalize column names.
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )

    # Remove duplicate rows.
    df = df.drop_duplicates()

    # Handle missing values.
    for column in df.columns:
        if df[column].isna().all():
            df[column] = df[column].fillna("")
        elif pd.api.types.is_numeric_dtype(df[column]):
            df[column] = df[column].fillna(0)
        else:
            df[column] = df[column].fillna("Unknown")

    # Parse columns whose names suggest they contain dates.
    for column in df.columns:
        if "date" in column or column.endswith("_at"):
            parsed_dates = pd.to_datetime(
                df[column], errors="coerce"
            )
            valid_dates = parsed_dates.notna()

            if valid_dates.any():
                df[column] = parsed_dates

    # Example of a simple column rename.
    df = df.rename(columns={
        "student_name": "name",
        "student_id": "id"
    })

    # Create the output directory if needed.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logging.info("Exporting %d rows to Excel.", len(df))

    df.to_excel(output_path, index=False, engine="openpyxl")

    logging.info("Conversion successful: %s", output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Clean a CSV file and convert it to Excel."
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the input CSV file"
    )

    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Path for the output .xlsx file"
    )

    args = parser.parse_args()

    try:
        convert_csv_to_excel(args.input, args.output)
    except (
        FileNotFoundError,
        ValueError,
        pd.errors.ParserError,
        UnicodeDecodeError,
        PermissionError,
        OSError,
        ImportError
    ) as error:
        logging.error("%s", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
