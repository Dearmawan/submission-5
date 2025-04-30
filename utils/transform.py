import pandas as pd
import re

def transform_data(df):
    """
    Membersihkan dan mentransformasi data:
    - Konversi harga ke Rupiah (1 USD = 16,000 IDR)
    - Hapus duplikat, null, dan data invalid
    - Sesuaikan tipe data
    """
    try:
        # Pemeriksaan awal untuk DataFrame kosong bisa dihapus jika except utama sudah menangani
        # if df.empty:
        #     raise ValueError("DataFrame kosong, tidak bisa ditransformasi.")

        # Salin DataFrame untuk menghindari modifikasi asli
        df_clean = df.copy()

        # Hapus data invalid (Pastikan kolom ada sebelum diakses)
        if "title" in df_clean.columns:
            df_clean = df_clean[~df_clean["title"].str.contains("Unknown Product", na=False)]
        if "price" in df_clean.columns:
            df_clean = df_clean[~df_clean["price"].str.contains("Price Unavailable", na=False)]
        if "rating" in df_clean.columns:
            df_clean = df_clean[~df_clean["rating"].str.contains("Invalid Rating", na=False)]

        # Konversi harga ke Rupiah
        def convert_price(price):
            try:
                # Tambahkan pengecekan jika price bukan string
                if not isinstance(price, str):
                    return None
                price_num = float(re.sub(r"[^\d.]", "", price))  # Ambil angka
                return int(price_num * 16000)  # Konversi ke IDR
            except (ValueError, TypeError):
                return None

        if "price" in df_clean.columns:
            df_clean["price"] = df_clean["price"].apply(convert_price)

        # Konversi rating ke float
        def convert_rating(rating):
            try:
                # Jika rating bukan string, re.search akan error
                # Tambahkan TypeError ke except clause
                if not isinstance(rating, str): # Cek tipe dulu lebih aman
                     return None
                match = re.search(r"[\d.]+", rating)
                if match:
                    return float(match.group())
                else:
                    return None
            # Menangkap AttributeError (jika match=None), ValueError (jika float gagal),
            # dan TypeError (jika input bukan string)
            except (AttributeError, ValueError, TypeError):
                return None

        if "rating" in df_clean.columns:
            df_clean["rating"] = df_clean["rating"].apply(convert_rating)

        # Bersihkan kolom colors
        if "colors" in df_clean.columns:
            df_clean["colors"] = df_clean["colors"].str.extract(r"(\d+)", expand=False) # expand=False agar jadi Series
            # Konversi ke float dulu untuk tangani NaN, baru nanti ke Int (setelah dropna)
            df_clean["colors"] = pd.to_numeric(df_clean["colors"], errors='coerce')


        # Bersihkan kolom size dan gender
        if "size" in df_clean.columns:
            # Handle None sebelum str.replace
            df_clean["size"] = df_clean["size"].apply(lambda x: x.replace("Size: ", "").strip() if isinstance(x, str) else x)
        if "gender" in df_clean.columns:
             # Handle None sebelum str.replace
            df_clean["gender"] = df_clean["gender"].apply(lambda x: x.replace("Gender: ", "").strip() if isinstance(x, str) else x)

        # Hapus null dan duplikat
        df_clean = df_clean.dropna().drop_duplicates()

        # Jika DataFrame kosong setelah dropna, kembalikan DataFrame kosong dengan kolom yg benar
        if df_clean.empty:
             # Kembalikan df kosong dengan kolom yg diharapkan agar shape tidak (0,0)
             return pd.DataFrame(columns=["title", "price", "rating", "colors", "size", "gender", "timestamp"])


        # Pastikan tipe data (hanya jika df tidak kosong)
        # Perhatikan: astype(int) akan error jika masih ada NaN (seharusnya sudah hilang krn dropna)
        try:
             df_clean = df_clean.astype({
                 "title": str,
                 "price": int,
                 "rating": float,
                 "colors": int, # Pastikan tidak ada NaN di sini
                 "size": str,
                 "gender": str,
                 "timestamp": str
             })
        except ValueError as e:
             print(f"Error saat casting tipe data setelah dropna: {e}")
             print("DataFrame sebelum error casting:")
             print(df_clean)
             print(df_clean.dtypes)
             # Kembalikan df kosong dg kolom jika error
             return pd.DataFrame(columns=["title", "price", "rating", "colors", "size", "gender", "timestamp"])


        # Tidak perlu raise ValueError di akhir jika sudah return df kosong di atas
        # if df_clean.empty:
        #     raise ValueError("DataFrame kosong setelah transformasi.")

        return df_clean

    except Exception as e:
        # Print error yang lebih spesifik
        import traceback
        print(f"Error tidak terduga saat transformasi data: {str(e)}")
        traceback.print_exc() # Cetak traceback lengkap
        # Kembalikan df kosong dengan kolom yg diharapkan
        return pd.DataFrame(columns=["title", "price", "rating", "colors", "size", "gender", "timestamp"])