import html
from pathlib import Path
from typing import List, Optional
import yaml
import polars as pl

YAML_FILE = Path(__file__).parent / "data" / "cheatsheet.yaml"
VALID_ENGINES = ["pandas", "polars", "pyspark"]


class RosieResult:
    def __init__(self, df: pl.DataFrame, raw_data: list, engines: list, gotchas: bool, transpose: bool):
        self.df = df
        self.raw_data = raw_data
        self.engines = engines
        self.gotchas = gotchas
        self.transpose = transpose

    def _repr_html_(self) -> str:
        css = """
        <style>
            .rosie-table {
                width: 100%;
                border-collapse: collapse;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                margin: 12px 0;
                font-size: 13px;
                line-height: 1.4;
            }
            .rosie-table th {
                background: rgba(125, 125, 125, 0.15);
                color: var(--jp-ui-font-color1, #e0e0e0);
                font-weight: 600;
                padding: 10px 14px;
                border: 1px solid rgba(125, 125, 125, 0.25);
                text-align: left;
            }
            .rosie-table td {
                padding: 10px 14px;
                border: 1px solid rgba(125, 125, 125, 0.25);
                vertical-align: top;
            }
            .rosie-badge {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
                text-transform: uppercase;
            }
            .badge-pandas { background: #306998; color: #ffffff; }
            .badge-polars { background: #00876c; color: #ffffff; }
            .badge-pyspark { background: #e25a1c; color: #ffffff; }
            .rosie-code {
                font-family: "JetBrains Mono", Consolas, Menlo, monospace;
                font-size: 12px;
                background: rgba(125, 125, 125, 0.1);
                border: 1px solid rgba(125, 125, 125, 0.2);
                border-radius: 4px;
                padding: 8px 10px;
                margin: 0;
                white-space: pre-wrap;
                word-break: break-word;
                color: var(--jp-ui-font-color1, #ffffff);
            }
            .rosie-gotcha {
                margin-top: 6px;
                padding: 6px 8px;
                background: rgba(245, 158, 11, 0.12);
                border-left: 3px solid #f59e0b;
                border-radius: 2px;
                font-size: 11px;
                color: var(--jp-ui-font-color2, #f3f4f6);
            }
        </style>
        """

        html_out = [css, '<table class="rosie-table">']

        if not self.transpose:
            html_out.append("<thead><tr><th>Library</th>")
            for item in self.raw_data:
                op_name = item.get("name", item.get("id"))
                html_out.append(f"<th>{html.escape(op_name)}</th>")
            html_out.append("</tr></thead><tbody>")

            for eng in self.engines:
                html_out.append("<tr>")
                html_out.append(f'<td><span class="rosie-badge badge-{eng}">{eng}</span></td>')
                for item in self.raw_data:
                    syntax = item.get(eng, "").strip()
                    code_html = f'<pre class="rosie-code">{html.escape(syntax)}</pre>'
                    gotcha_html = ""
                    if self.gotchas:
                        note = item.get("gotchas", {}).get(eng, "")
                        if note:
                            gotcha_html = f'<div class="rosie-gotcha">💡 <b>Gotcha:</b> {html.escape(note)}</div>'
                    html_out.append(f"<td>{code_html}{gotcha_html}</td>")
                html_out.append("</tr>")
        else:
            html_out.append("<thead><tr><th>Operation</th>")
            for eng in self.engines:
                html_out.append(f'<th><span class="rosie-badge badge-{eng}">{eng}</span></th>')
            html_out.append("</tr></thead><tbody>")

            for item in self.raw_data:
                op_name = item.get("name", item.get("id"))
                html_out.append(f"<tr><td><b>{html.escape(op_name)}</b></td>")
                for eng in self.engines:
                    syntax = item.get(eng, "").strip()
                    code_html = f'<pre class="rosie-code">{html.escape(syntax)}</pre>'
                    gotcha_html = ""
                    if self.gotchas:
                        note = item.get("gotchas", {}).get(eng, "")
                        if note:
                            gotcha_html = f'<div class="rosie-gotcha">💡 <b>Gotcha:</b> {html.escape(note)}</div>'
                    html_out.append(f"<td>{code_html}{gotcha_html}</td>")
                html_out.append("</tr>")

        html_out.append("</tbody></table>")
        return "".join(html_out)

    def to_polars(self) -> pl.DataFrame:
        return self.df

    def __repr__(self) -> str:
        with pl.Config(tbl_rows=-1, tbl_cols=-1, fmt_str_lengths=120, tbl_width_chars=180):
            return str(self.df)


class SyntaxLookup:
    def __init__(self, data_path: Path = YAML_FILE):
        self.data_path = data_path
        self._raw_data = self._load_data()

    def _load_data(self) -> list:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Cheatsheet data not found at: {self.data_path}")
        with open(self.data_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f).get("operations", [])

    def categories(self) -> List[str]:
        return sorted(list(set(item.get("category", "general") for item in self._raw_data)))

    def show(
        self,
        *engines: str,
        category: Optional[str] = None,
        ops: Optional[List[str]] = None,
        gotchas: bool = False,
        transpose: Optional[bool] = None
    ) -> RosieResult:
        """
        Compare DataFrame syntax across engines.

        Categories:
            - 'inspect'   : read_data, view_rows, schema_info, count_nulls, drop_duplicates, describe_stats
            - 'clean'     : filter_rows, handle_nulls, cast_types, rename_columns, string_cleaning
            - 'transform' : add_column, groupby_agg, join_tables, reshape, window_functions
            - 'eda'       : univariate_counts, quantiles, skew_kurt, bivariate_corr, crosstab, covariance
            - 'export'    : save_parquet, save_csv
        """
        selected_engines = [e.lower() for e in engines] if engines else VALID_ENGINES
        for eng in selected_engines:
            if eng not in VALID_ENGINES:
                raise ValueError(f"Unknown engine '{eng}'. Choose from: {VALID_ENGINES}")

        filtered_items = []
        for item in self._raw_data:
            if category and item.get("category", "").lower() != category.lower():
                continue
            op_id = item.get("id", "")
            op_name = item.get("name", op_id)
            if ops and not any(t.lower() in (op_id.lower(), op_name.lower()) for t in ops):
                continue
            filtered_items.append(item)

        # Auto-transpose if table is wide (> 3 columns) unless explicitly overridden
        should_transpose = transpose if transpose is not None else (len(filtered_items) > 3)

        if not should_transpose:
            data_dict = {"Library": selected_engines}
            for item in filtered_items:
                name = item.get("name", item.get("id"))
                data_dict[name] = [item.get(eng, "").strip() for eng in selected_engines]
            df = pl.DataFrame(data_dict)
        else:
            data_dict = {"Operation": [item.get("name", item.get("id")) for item in filtered_items]}
            for eng in selected_engines:
                data_dict[eng] = [item.get(eng, "").strip() for item in filtered_items]
            df = pl.DataFrame(data_dict)

        return RosieResult(df, filtered_items, selected_engines, gotchas, should_transpose)

    def search(self, query: str, *engines: str, gotchas: bool = False) -> RosieResult:
        """Search query matching across name, id, category, and gotchas."""
        q = query.lower()
        matched_ops = []
        for item in self._raw_data:
            fields = [
                item.get("id", ""),
                item.get("name", ""),
                item.get("category", ""),
                str(item.get("gotchas", ""))
            ]
            if any(q in f.lower() for f in fields):
                matched_ops.append(item.get("id"))
        return self.show(*engines, ops=matched_ops, gotchas=gotchas)


helper = SyntaxLookup()
show = helper.show