import pandas as pd
from tabulate import tabulate
import argparse

def generate_markdown(csv_path):
    df = pd.read_csv(csv_path)    
    filtered_df = df[df['period'] == 'Annually'].sort_values(by='price')
    print(filtered_df.columns)
    cols = ['p_name', 'cpu', 'disk', 'ram', 'bandwidth', 'bps', 'price', 'period', 'aff']
    df_md = filtered_df[cols]
    df_md.fillna('', inplace=True)
    df_md['p_name'] = df_md['p_name'].apply(lambda x: x.replace("\n", ' '))
    df_md['p_name'] = df_md['p_name'].str.replace('\n', ' ', regex=True)
    df_md['aff'] = df_md['aff'].apply(lambda x: f"[link]({x})")
    df_md['price'] = df_md['price'].apply(lambda x: f"${x}")
    df_md.rename(columns={'aff': 'url', 'p_name': 'product'}, inplace=True)
    df_md.reset_index(drop=True, inplace=True)
    df_md = df_md.loc[~df_md['product'].str.contains(r'RESELLER|SHARED')]

    df_md['cpu'] = df_md['cpu'].str.extract(r'(\d+)').fillna(0).astype(int)
    df_md['cpu'] = df_md['cpu'].replace(0, '')
    df_md['disk'] = df_md['disk'].str.replace(' ', '')
    df_md['ram'] = df_md['ram'].str.replace(' ', '')
    df_md['bandwidth'] = df_md['bandwidth'].str.replace(' ', '')

    df_md.index = df_md.index + 1
    df_md.index.name = 'rank'
    print(df_md.head())
    df_md.to_markdown('data/annually-products.md')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate product report markdown and update README.")
    parser.add_argument("--csv_path", type=str, help="Path to the CSV file", required=True)
    args = parser.parse_args()
    
    generate_markdown(args.csv_path)
