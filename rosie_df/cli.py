import argparse
import polars as pl
from rosie_df.core import helper

def main():
    parser = argparse.ArgumentParser(
        prog="rosie",
        description="Rosie-DF: Fast DataFrame Cheatsheet for Pandas, Polars & PySpark"
    )
    parser.add_argument("engines", nargs="*", default=[], help="Engines: pandas, polars, pyspark")
    parser.add_argument("--category", "-c", type=str, default=None, help="Filter category: inspect, clean, transform, eda, export")
    parser.add_argument("--search", "-s", type=str, default=None, help="Search query")
    parser.add_argument("--ops", "-o", nargs="+", default=None, help="Filter specific operations")
    parser.add_argument("--gotchas", "-g", action="store_true", help="Show performance gotchas")
    parser.add_argument("--transpose", "-t", action="store_true", help="Transpose rows and columns")
    parser.add_argument("--categories", action="store_true", help="List available categories")

    args = parser.parse_args()

    if args.categories:
        print("\nAvailable Categories:", ", ".join(helper.categories()), "\n")
        return

    if args.search:
        result = helper.search(args.search, *args.engines, gotchas=args.gotchas)
    else:
        result = helper.show(
            *args.engines,
            category=args.category,
            ops=args.ops,
            gotchas=args.gotchas,
            transpose=True if args.transpose else None
        )

    with pl.Config(tbl_rows=-1, tbl_cols=-1, fmt_str_lengths=120, tbl_width_chars=180):
        print("\n", result.df, "\n")

if __name__ == "__main__":
    main()