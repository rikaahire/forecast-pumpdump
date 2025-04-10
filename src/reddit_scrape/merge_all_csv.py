import pandas as pd

def merge_multiple_csvs_with_subreddits(file_subreddit_pairs, output_file):
    all_dfs = []

    for file_path, subreddit_name in file_subreddit_pairs:
        df = pd.read_csv(file_path)
        # df['subreddit'] = subreddit_name  # Add subreddit column
        all_dfs.append(df)

    merged_df = pd.concat(all_dfs, ignore_index=True)
    merged_df.to_csv(output_file, index=False)
    print(f"Merged CSV saved to {output_file} with {len(merged_df)} rows from {len(file_subreddit_pairs)} subreddits.")

# Example usage
file_subreddit_pairs = [
    ("pepe_CryptoCurrency.csv", "CryptoCurrency"),
    ("pepe_dogecoin.csv", "dogecoin"),
    ("pepe_SatoshiStreetBets.csv", "SatoshiStreetBets")
]

merge_multiple_csvs_with_subreddits(file_subreddit_pairs, "pepe_final.csv")
