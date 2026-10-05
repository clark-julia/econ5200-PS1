"""Audit and robust-average helpers for the consumer basket-value metric."""

import numpy as np
import pandas as pd


def audit_report(df: pd.DataFrame) -> pd.DataFrame:
  """One row per column: missingness, dtype, skew and outlier count."""

  report_rows = []
  for col_name in df:
    col_values = df[col_name]

    #rows that are missing (NaN) in this column
    share_missing = col_values.isna().mean()

    col_type = col_values.dtype

    if (pd.api.types.is_numeric_dtype(col_values)):

        col_skew = col_values.skew()

    #find spread (IQR)
        first_quartile = col_values.quantile(0.25)
        third_quartile = col_values.quantile(0.75)
        spread = third_quartile - first_quartile

        # Values more than 1.5 IQRs outside the quartiles count as outliers
        floor_cutoff = first_quartile - 1.5 * spread
        ceiling_cutoff = third_quartile + 1.5 * spread

        n_outliers = (
            (col_values < floor_cutoff) |
            (col_values > ceiling_cutoff)
        ).sum()

    else:
        #no outliers or text column
        col_skew = np.nan
        n_outliers = np.nan

    report_rows.append({
        "column": col_name,
        "missing": share_missing,
        "dtype": col_type,
        "skew": col_skew,
        "outlier_count": n_outliers
    })
  return pd.DataFrame(report_rows)


def robust_mean(
    x: pd.Series,
    method: str = "median",
    segment: pd.Series | None = None
    ) -> float:

  match method:
    case "median":
      return x.median()

    case "trimmed":
      # Keep only values between the 10th and 90th percentiles, then average
      low_cut = x.quantile(0.1)
      high_cut = x.quantile(0.9)

      return x.loc[
          (x >= low_cut) & (x <= high_cut)
      ].mean()

    case "rule-based":
      # Needs the order-type label
      if segment is None:
        raise ValueError("order_type must be provided")
      return x.loc[segment == "B2C"].mean()

    case _:
            raise ValueError(
                "The method is not valid. "
                "Use 'median', 'trimmed', or 'rule-based'."
            )

if __name__ == "__main__":
    # A short demonstration that runs when the file is run as a script
    demo_df = pd.DataFrame({
        "basket_value": [10, 12, 15, 20, 25, 30, 1000],
        "order_type": ["B2C", "B2C", "B2C", "B2C", "B2C", "B2C", "B2B"]
    })

    print("Audit Report:")
    print(audit_report(demo_df))

    print("\nMedian:")
    print(robust_mean(demo_df["basket_value"], "median"))

    print("\nTrimmed Mean:")
    print(robust_mean(demo_df["basket_value"], "trimmed"))

    print("\nRule-based Exclusion:")
    print(robust_mean(demo_df["basket_value"], "rule-based", demo_df["order_type"]))
