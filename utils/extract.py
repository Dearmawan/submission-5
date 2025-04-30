import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_data():
    """
    Mengambil data dari website fashion-studio.dicoding.dev (halaman 1-50).
    Menambahkan kolom timestamp untuk waktu ekstraksi.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        all_data = []

        # Loop melalui halaman 1 sampai 50
        for page in range(1, 51):
            # Halaman 1 tidak memiliki /page, halaman 2-50 menggunakan /page{page}
            if page == 1:
                url = "https://fashion-studio.dicoding.dev/"
            else:
                url = f"https://fashion-studio.dicoding.dev/page{page}"
            print(f"Mengakses halaman {page}: {url}")

            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                print(f"Halaman {page} berhasil diakses, status code: {response.status_code}")
            except requests.RequestException as e:
                print(f"Gagal mengakses halaman {page}: {str(e)}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            products = soup.select("div.collection-card")
            print(f"Ditemukan {len(products)} produk di halaman {page}")

            if not products:
                print(f"Tidak ada produk ditemukan di halaman {page}.")
                continue

            for product in products:
                try:
                    # Ambil title
                    title_elem = product.select_one("h3.product-title")
                    title = title_elem.text.strip() if title_elem else "Unknown Product"
                    print(f"Title: {title}")

                    # Ambil price
                    price_container = product.select_one("div.price-container span.price")
                    price_direct = product.select_one("p.price")
                    price = price_container.text.strip() if price_container else (price_direct.text.strip() if price_direct else "Price Unavailable")
                    print(f"Price: {price}")

                    # Ambil rating, colors, size, gender dari elemen <p>
                    details = product.select("div.product-details p")
                    print(f"Jumlah detail: {len(details)}")
                    rating = "Invalid Rating"
                    colors = "0 Colors"
                    size = "Size: Unknown"
                    gender = "Gender: Unknown"

                    for detail in details:
                        text = detail.text.strip()
                        print(f"Detail: {text}")
                        if "Rating:" in text:
                            rating = text.replace("Rating: ⭐ ", "")
                        elif "Colors" in text:
                            colors = text
                        elif "Size:" in text:
                            size = text
                        elif "Gender:" in text:
                            gender = text

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    all_data.append({
                        "title": title,
                        "price": price,
                        "rating": rating,
                        "colors": colors,
                        "size": size,
                        "gender": gender,
                        "timestamp": timestamp
                    })
                except Exception as e:
                    print(f"Gagal memproses produk di halaman {page}: {str(e)}")
                    continue

        if not all_data:
            print("Tidak ada data yang berhasil di-scrape.")
            
        print(f"Berhasil mengekstrak {len(all_data)} produk.")
        return pd.DataFrame(all_data)

    except Exception as e:
        print(f"Error tak terduga saat ekstraksi: {str(e)}")
        return pd.DataFrame()