# Proyek ETL Pipeline yang Keren Abis! 🚀

Selamat datang di proyek ETL (Extract, Transform, Load) super kece yang dibuat dengan Python! Proyek ini bakal nyanyi sambil ngambil data dari website, ngedit data biar ciamik, lalu nyanyi lagi sambil menyimpan ke CSV, Google Sheets, dan PostgreSQL. Siap-siap terpukau! 😺🎉

## Apa Sih Ini?

Proyek ini adalah pipeline ETL yang:
- **Ekstrak**: Ngambil data kece dari website pake fungsi `scrape_data` dari `utils.extract`.
- **Transformasi**: Bikin data jadi lebih glowing pake `transform_data` dari `utils.transform`.
- **Muat**: Simpen data ke tiga tempat keren:
  - File CSV (`products.csv`)
  - Google Sheets (di worksheet yang kamu tentuin)
  - Database PostgreSQL (tabel `products` di `companydb`)

Semua dikomando oleh `main.py` dengan penanganan error yang super tangguh! 🦄💪

## Apa yang Kamu Butuhin?

- Python 3.8+ (yang terbaru biar ga ketinggalan zaman)
- Paket Python (pasang pake pip):
  ```bash
  pip install pandas psycopg2-binary gspread oauth2client
  ```
- Database PostgreSQL (`companydb`) dengan detail login:
  - Username: `postgres`
  - Password: ******** (rahasia dong! 😜)
  - Host: `localhost`
  - Port: `5432`
- File kredensial Google Sheets API (`google-sheets-api.json`) biar bisa nyanyi bareng Google Sheets.

## Struktur Proyek

```
proyek/
├── main.py                  # Komandan utama pipeline ETL
├── utils/
│   ├── extract.py           # Jagoan ekstraksi data
│   ├── transform.py         # Penata data biar kece
│   └── load.py              # Penyanyi yang nyanyi ke CSV, Sheets, & Postgres
├── google-sheets-api.json   # Kunci ajaib buat Google Sheets
└── products.csv             # Hasil karya CSV yang ciamik
```

## Cara Nyalain Pipeline Ini

1. Clone repo ini biar masuk ke markasmu:
   ```bash
   git clone <url-repo-kamu>
   cd <folder-proyek>
   ```

2. Pasang semua kebutuhan:
   ```bash
   pip install -r requirements.txt
   ```

3. Pastiin database PostgreSQL udah nyanyi di `companydb`.

4. Taruh file `google-sheets-api.json` di folder proyek.

5. Jalanin pipeline dengan penuh gaya:
   ```bash
   python main.py
   ```

Boom! Pipeline bakal:
- Nyanyi sambil ngambil data dari sumber.
- Berdandan biar data glowing.
- Nyanyi lagi sambil nyimpan ke `products.csv`, Google Sheets, dan tabel `products` di PostgreSQL. 🎤✨

## Tangkap Error dengan Keren

Pipeline ini punya tameng super:
- Cek kalau data ekstraksi kosong.
- Cek kalau data transformasi ga muncul.
- Tangkap error koneksi atau izin pas nyanyi ​​pake `main.py` bilang:
> Pipeline ETL gagal: Tidak ada data yang berhasil diekstrak dari website.

Kalau ada error, pipeline bakal teriak errornya dan berhenti dengan elegan. 🦁🚨

## Atur Sesuka Hati

Ubah pengaturan di `main.py` sesuai selera:
- **CSV**: `csv_path = "products.csv"`
- **Google Sheets**:
  - `sheet_id`: ID spreadsheet Google Sheets
  - `worksheet_name`: Nama worksheet
  - `creds_path`: Lokasi file `google-sheets-api.json`
- **PostgreSQL**:
  - `db_conn_str`: String koneksi database
  - `table_name`: Nama tabel

## Hasil Keren

- **CSV**: File `products.csv` muncul di folder proyek.
- **Google Sheets**: Data masuk ke worksheet yang kamu pilih.
- **PostgreSQL**: Data nyanyi di tabel `products` di `companydb`.

## Catatan Penting

- Pastiin Google Sheets API aktif dan akun servis punya akses ke spreadsheet.
- Database `companydb` harus udah dibuat sebelum nyanyi.
- Modul `utils` diasumsikan punya fungsi kece (`scrape_data`, `transform_data`, `load_to_csv`, dll).

## Rencana Masa Depan

- Tambah log biar debug makin asyik.
- Kasih fitur nyanyi ulang kalau API/database gagal.
- Dukung lebih banyak sumber dan tujuan data.
- Bikin tes biar `utils` makin mantap.

Ayo nyanyi bareng pipeline ETL ini! 🦒🎊