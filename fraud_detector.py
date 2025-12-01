import pandas as pd
from datetime import timedelta

TIME_LIMIT_GEO_HOURS = 6
AMOUNT_LIMIT_LARGE = 1000
FAILED_COUNT_THRESHOLD = 5
FAILED_TIME_WINDOW_MINUTES = 30
AMOUNT_DEVIATION_PERCENT = 3.0

def apply_fraud_rules(df):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Is_Suspicious'] = 0 
    df['Susp_Geo'] = 0
    df['Susp_FailCount'] = 0
    df['Susp_Amount'] = 0

    df = df.sort_values(by=['Client_ID', 'Timestamp']).reset_index(drop=True)

    print("--- Implementation of Analytical Rules ---")
    
    def check_geo_fraud(client_transactions):
  
        susp_geo_series = pd.Series(0, index=client_transactions.index)
        
        pl_transactions = client_transactions[client_transactions['Location'].str.contains('PL', na=False)] 
        
        if pl_transactions.empty:
            return susp_geo_series

        for index in client_transactions.index:
            current_tx = client_transactions.loc[index]
            
            if ('PL' not in current_tx['Location']) and current_tx['Amount'] >= AMOUNT_LIMIT_LARGE:
                
                time_window = current_tx['Timestamp'] - timedelta(hours=TIME_LIMIT_GEO_HOURS)
                
                recent_pl_txs = pl_transactions[
                    (pl_transactions['Timestamp'] >= time_window) &
                    (pl_transactions['Timestamp'] < current_tx['Timestamp'])
                ]

                if not recent_pl_txs.empty:
                    susp_geo_series.loc[index] = 1
        
        return susp_geo_series

    geo_results = df.groupby('Client_ID').apply(check_geo_fraud)
    df['Susp_Geo'] = geo_results.reset_index(level=0, drop=True)
    df['Is_Suspicious'] = df['Is_Suspicious'].mask(df['Susp_Geo'] == 1, 1)
    
    window_size_str = f'{FAILED_TIME_WINDOW_MINUTES}min'
    
    df['Failed_Count_Past'] = (
        df.groupby('Client_ID', group_keys=False)
        .apply(lambda x: x.set_index('Timestamp')['Is_Failed']
               .rolling(window=window_size_str, closed='left') 
               .sum()
               .fillna(0)
        )
        .reset_index(level=0, drop=True)
    )
    
    is_susp_fail = (df['Failed_Count_Past'] >= FAILED_COUNT_THRESHOLD).astype(int)
    df['Susp_FailCount'] = is_susp_fail
    df['Is_Suspicious'] = df['Is_Suspicious'].mask(is_susp_fail == 1, 1)

    def check_amount_deviation(client_transactions):
        susp_amount_series = pd.Series(0, index=client_transactions.index)
        
        successful_txs = client_transactions[client_transactions['Is_Failed'] == 0]
        historical_mean = successful_txs['Amount'].mean()
        
        if pd.isna(historical_mean) or historical_mean == 0:
            return susp_amount_series

        is_susp = (client_transactions['Amount'] > (historical_mean * AMOUNT_DEVIATION_PERCENT)).astype(int)
        
        susp_amount_series.loc[is_susp == 1] = 1
        
        return susp_amount_series

    amount_results = df.groupby('Client_ID').apply(check_amount_deviation)
    df['Susp_Amount'] = amount_results.reset_index(level=0, drop=True)
    df['Is_Suspicious'] = df['Is_Suspicious'].mask(df['Susp_Amount'] == 1, 1)
    
    return df

try:
    transactions_df = pd.read_csv('simulated_transactions.csv')
    
    if 'Is_Fraud_Manual' not in transactions_df.columns:
         raise KeyError("Kolumna 'Is_Fraud_Manual' jest wymagana do raportowania.")
    if 'Is_Failed' not in transactions_df.columns:
         raise KeyError("Kolumna 'Is_Failed' jest wymagana do reguł analitycznych.")

    print(f"Wczytano {len(transactions_df)} rekordów transakcji.")
    

    result_df = apply_fraud_rules(transactions_df.copy())
    
    total_suspicious = result_df['Is_Suspicious'].sum()
    total_fraud_manual = result_df['Is_Fraud_Manual'].sum()
    
    print(f"\n--- Detection Summary ---")
    print(f"Number of transactions flagged as suspicious by the Rules: {total_suspicious}")
    print(f"Number of actually fraudulent transactions (according to manual flag): {total_fraud_manual}")
    
    
    result_df['Active_Rules'] = result_df.apply(lambda row: ', '.join([
        'GEO' if row['Susp_Geo'] == 1 else '',
        'FAILED_ATTEMPTS' if row['Susp_FailCount'] == 1 else '',
        'HIGH_AMOUNT' if row['Susp_Amount'] == 1 else ''
    ]).strip(' ,'), axis=1)

    report_df = result_df[result_df['Is_Suspicious'] == 1]
    report_df.to_csv('Fraud_Monitoring_Report.csv', index=False)
    report_df.to_excel('Fraud_Monitoring_Report.xlsx', index=False, sheet_name='Suspicious Transactions')
    
    print(f"The suspicious transactions report has been exported to ‘Fraud_Monitoring_Report.xlsx.' ({len(report_df)} records).")

except FileNotFoundError:
    print("ERROR: The file ‘simulated_transactions.csv’ was not found.")
except KeyError as e:
    print(f"DATA ERROR: {e}. Make sure that the CSV file contains the required column with the correct name.")