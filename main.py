import pandas as pd
from utils.extract import scrape_data
from utils.transform import transform_data
from utils.load import load_to_csv, load_to_gsheets, load_to_postgres

def main():
    try:
        # Tahap Ekstraksi
        print("Memulai ekstraksi data...")
        raw_data = scrape_data()
        if raw_data.empty:
            raise ValueError("Tidak ada data yang berhasil diekstrak dari website.")

        # Tahap Transformasi
        print("Memulai transformasi data...")
        transformed_data = transform_data(raw_data)
        if transformed_data.empty:
            raise ValueError("Tidak ada data setelah transformasi.")

        # Tahap Pemuatan
        print("Memulai pemuatan data...")

        # SAVE TO CSV
        csv_path = "products.csv"
        load_to_csv(transformed_data, csv_path)

        # SAVE TO GOOGLE SHEETS
        sheet_id = "1jkMPD5_kJjivm7tmyXglsP8RbU7nya0dX_ZJ7ES4Lxc"  
        worksheet_name = "Sheet1" 
        creds_path = "google-sheets-api.json"  
        load_to_gsheets(transformed_data, spreadsheet_id=sheet_id, creds_path=creds_path, worksheet_name=worksheet_name)

        # SAVE TO POSTGRESQL
        db_conn_str = "postgresql://postgres:dear123@localhost:5432/companydb" 
        table_name = "products"
        load_to_postgres(transformed_data, db_conn_str=db_conn_str, table_name=table_name)

        print("Pipeline ETL selesai dengan sukses.")

    except Exception as e:
        print(f"Pipeline ETL gagal: {str(e)}")
        raise

if __name__ == "__main__":
    main()
