import pandas as pd

def merge_csvs_remove_duplicates(file1, file2, output_file):
    # Load both CSV files into DataFrames
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Concatenate the two DataFrames
    combined_df = pd.concat([df1, df2], ignore_index=True)

    # Drop exact duplicate rows
    deduplicated_df = combined_df.drop_duplicates()

    # Save the result to a new CSV file
    deduplicated_df.to_csv(output_file, index=False)
    print(f"Merged file saved to {output_file} with {len(deduplicated_df)} unique rows.")

# Example usage
merge_csvs_remove_duplicates("doge_SatoshiStreetBets.csv", "dogecoin_SatoshiStreetBets.csv", "merged_dogecoin_SatoshiStreetBets.csv")
