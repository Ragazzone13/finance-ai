import io
import pandas as pd
from datetime import datetime

def parse_transactions_csv(user_id: int, file_obj: io.BufferedReader):
    df = pd.read_csv(file_obj)
    required = {"date", "amount", "type"}
    if not required.issubset(set(df.columns)):
        missing = required - set(df.columns)
        raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")

    items = []
    for _, row in df.iterrows():
        dt = datetime.strptime(str(row["date"]).strip(), "%Y-%m-%d").date()
        t_type = str(row["type"]).lower().strip()
        amount = float(row["amount"])

        item = {
            "user_id": int(user_id),
            "account_id": int(row["account_id"]) if "account_id" in df.columns and pd.notna(row["account_id"]) else None,
            "date": dt,
            "amount": amount,
            "txn_type": t_type,  # renamed
            "category_id": int(row["category_id"]) if "category_id" in df.columns and pd.notna(row["category_id"]) else None,
            "vendor": str(row["vendor"]) if "vendor" in df.columns and pd.notna(row["vendor"]) else None,
            "note": str(row["note"]) if "note" in df.columns and pd.notna(row["note"]) else None,
            "is_recurring": False,
            "source": "csv",
        }
        items.append(item)
    return items