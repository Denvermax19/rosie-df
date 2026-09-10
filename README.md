# 🌹 rosie-df

> The interactive DataFrame Rosetta Stone for **Pandas**, **Polars**, and **PySpark**.

Most data teams overspend on cloud compute and run into Out-Of-Memory (OOM) errors not because of bad business logic, but because of **muscle memory**. Engineers stick with Pandas because syntax like `.apply()`, `.reset_index()`, and `pd.concat()` is wired into their fingers—even when a Polars or PySpark implementation would run 10x faster at a fraction of the cost.

Learning a new DataFrame engine usually means constantly pausing your flow, scouring documentation, and hunting for syntax equivalents. 

**`rosie-df` eliminates that friction.** 

It gives you and your team a real-time syntax translator and performance guide right inside your Jupyter Notebook or Terminal. Type what you need, see the exact syntax for each library side-by-side, and catch costly performance gotchas before hitting production.

---

## ⚡ Quick Start

### Installation

Install directly from your repository:

```bash
pip install git+https://github.com/your-org/rosie-df.git
```

Or clone and install in editable mode:

```bash
git clone https://github.com/your-org/rosie-df.git
cd rosie-df
pip install -e .
```

---

## 🚀 Usage

### 1. In Jupyter Notebook

```python
from rosie_df import helper

# Compare Pandas and Polars for your initial morning sanity check
helper.show("pandas", "polars", category="inspect")

# Compare Polars and PySpark with performance gotchas
helper.show("polars", "pyspark", category="eda", gotchas=True)

# Search across all operations by keyword
helper.search("skew", "pandas", "polars")
```

Inside Jupyter, `rosie-df` automatically renders a styled, wrap-enabled table with syntax badges and highlight boxes for gotchas (compatible with both Dark and Light themes).

---

### 2. In Terminal (CLI)

No need to open a notebook for a quick lookup. Run `rosie` directly in your shell:

```bash
# Compare Pandas vs Polars
rosie pandas polars -c inspect

# Polars vs PySpark with performance gotchas
rosie polars pyspark -c eda -g

# Search for any operation
rosie pandas polars -s "filter"

# List all categories
rosie --categories
```

---

## 📚 Supported Categories

Operations are organized around the actual daily workflow of a data engineer:

| Category | Typical Operations Included |
| :--- | :--- |
| **`inspect`** | `read_data`, `view_rows` (head), `schema_info` (info/glimpse), `count_nulls`, `drop_duplicates`, `describe_stats` |
| **`clean`** | `filter_rows`, `handle_nulls` (drop/fill), `cast_types`, `rename_columns`, `string_cleaning` |
| **`transform`** | `add_column`, `groupby_agg`, `join_tables`, `reshape` (pivot/melt), `window_functions` |
| **`eda`** | `univariate_counts`, `univariate_quantiles`, `skew_and_kurtosis`, `bivariate_corr`, `crosstab`, `covariance` |
| **`export`** | `save_parquet`, `save_csv` |

---

## 💡 Why Performance Gotchas Matter

Writing code that runs is easy; writing code that scales is hard. `rosie-df` includes critical guardrails when using `gotchas=True` or `-g`:

* **Pandas:** Warns about `SettingWithCopyWarning`, silent copy operations, and unindexed groupby outputs.
* **Polars:** Prevents Python `and`/`or` mistakes, steers away from slow `.apply()` antipatterns, and emphasizes expression parallelism.
* **PySpark:** Flags expensive network shuffles, catastrophic `.withColumn()` chains, and unpartitioned window functions that cause driver OOMs.

---

## 🛠️ Contributing

Adding new recipes or engines (e.g., DuckDB, SQL) is as simple as editing `rosie_df/data/cheatsheet.yaml`. No Python code changes needed.

1. Fork or branch the repo.
2. Add your recipe and gotcha to `cheatsheet.yaml`.
3. Open a Pull Request.

---

## 📄 License

MIT License. Free to use, adapt, and share across your data teams.
```
