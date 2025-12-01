import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_data(num_records=10000):
    client_ids = [f'C{i:03}' for i in range(100)]
    start_time = datetime(2025, 10, 1)

    data = {
        'Transaction_ID': np.arange(num_records),
        'Client_ID': [random.choice(client_ids) for _ in range(num_records)],
        'Amount': np.round(np.random.lognormal(mean=6, sigma=1.5, size=num_records), 2),
        'Timestamp': [start_time + timedelta(minutes=random.randint(0, 1440 * 30), seconds=random.randint(0, 60)) for _ in range(num_records)],
        'Location': [random.choice(['Kraków, PL', 'Warszawa, PL', 'New York, US', 'London, UK']) for _ in range(num_records)],
        'Is_Fraud_Manual': np.random.choice([0, 1], size=num_records, p=[0.98, 0.02]) # 2% oznaczamy jako "prawdziwe" oszustwo
    }
    df = pd.DataFrame(data).sort_values(by='Timestamp').reset_index(drop=True)
    return df

transactions_df = generate_data()
transactions_df.to_csv('simulated_transactions.csv', index=False)