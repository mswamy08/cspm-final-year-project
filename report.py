import pandas as pd
from tabulate import tabulate
import os

def print_report(data, title="Report"):
    print(f"\n--- {title} ---")
    if not data:
        print("No findings.")
        return
    print(tabulate(data, headers="keys"))

import pandas as pd
import os

def export_csv(data, path):
    # Ensure the folder exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)

    print(f"[INFO] Report exported to {path}")
