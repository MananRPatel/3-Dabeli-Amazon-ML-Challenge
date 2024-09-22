import pandas as pd
import argparse
import re
import os
import constants
from utils import parse_string

def check_file(filename):
    if not filename.lower().endswith('.csv'):
        raise ValueError("Only CSV files are allowed.")
    if not os.path.exists(filename):
        raise FileNotFoundError("Filepath: {} invalid or not found.".format(filename))

def parse_prediction(row):
    try:
        # Attempt to parse the 'prediction' column
        print(f"Parsing index {row['index']}")
        number, unit = parse_string(row['prediction'])
        return row['prediction']  # Return the original prediction if valid
    except ValueError as e:
        # If an invalid format is found, return an empty string instead of raising an error
        print(f"Invalid format for index {row['index']}: {e}")
        return ""  # Only modify the prediction if an error is encountered

def sanity_check(test_filename, output_filename, new_filename="bapu.csv"):
    check_file(test_filename)
    check_file(output_filename)

    try:
        test_df = pd.read_csv(test_filename)
        output_df = pd.read_csv(output_filename)
    except Exception as e:
        raise ValueError(f"Error reading the CSV files: {e}")

    if 'index' not in test_df.columns:
        raise ValueError("Test CSV file must contain the 'index' column.")

    if 'index' not in output_df.columns or 'prediction' not in output_df.columns:
        raise ValueError("Output CSV file must contain 'index' and 'prediction' columns.")

    missing_index = set(test_df['index']).difference(set(output_df['index']))
    if len(missing_index) != 0:
        print("Missing index in test file: {}".format(missing_index))

    extra_index = set(output_df['index']).difference(set(test_df['index']))
    if len(extra_index) != 0:
        print("Extra index in test file: {}".format(extra_index))

    # Apply the parse_prediction function to each row
    output_df['new_prediction'] = output_df.apply(parse_prediction, axis=1)

    # Only update 'prediction' where parsing failed and returned an empty string
    output_df['prediction'] = output_df.apply(
        lambda row: row['new_prediction'] if row['new_prediction'] == "" else row['prediction'], axis=1
    )

    # Drop the helper column 'new_prediction'
    output_df.drop(columns=['new_prediction'], inplace=True)

    print(f"Parsing successful for file: {output_filename}")

    # Save the updated DataFrame with empty strings in place of invalid predictions to bapu.csv
    output_df.to_csv(new_filename, index=False)
    print(f"Successfully saved updated output to {new_filename}")

if __name__ == "__main__":
    # Usage example: python sanity.py --test_filename sample_test.csv --output_filename sample_test_out.csv

    parser = argparse.ArgumentParser(description="Run sanity check on a CSV file.")
    parser.add_argument("--test_filename", type=str, required=True, help="The test CSV file name.")
    parser.add_argument("--output_filename", type=str, required=True, help="The output CSV file name to check.")
    args = parser.parse_args()
    
    try:
        sanity_check(args.test_filename, args.output_filename)
    except Exception as e:
        print('Error:', e)
