import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock, ANY # Pastikan MagicMock diimport
import pandas as pd
from datetime import datetime # Diperlukan untuk type hinting atau membuat objek datetime jika perlu
import requests # Pastikan diimport
from pandas.testing import assert_frame_equal

# Impor fungsi yang akan diuji
from utils.extract import scrape_data

# Fixture mock_response_page1 (seperti yang sudah Anda miliki)
@pytest.fixture
def mock_response_page1():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = """
    <html><body>
    <div class="collection-card">
        <div class="product-details">
            <h3 class="product-title">Cool T-Shirt</h3>
            <div class="price-container"><span class="price">$25.50</span></div>
            <p style="font-size: 14px; color: #777;">Rating: ⭐ 4.5 / 5</p>
            <p style="font-size: 14px; color: #777;">3 Colors</p>
            <p style="font-size: 14px; color: #777;">Size: L</p>
            <p style="font-size: 14px; color: #777;">Gender: Male</p>
        </div>
    </div>
    <div class="collection-card">
        <div class="product-details">
            <h3 class="product-title">Awesome Jacket</h3>
            <div class="price-container"><span class="price">Price Unavailable</span></div>
            <p style="font-size: 14px; color: #777;">Rating: ⭐ Invalid Rating</p>
            <p style="font-size: 14px; color: #777;">2 Colors</p>
            <p style="font-size: 14px; color: #777;">Size: M</p>
            <p style="font-size: 14px; color: #777;">Gender: Female</p>
        </div>
    </div>
    </body></html>
    """
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


@patch('utils.extract.requests.get') # Mock requests.get di dalam extract.py
@patch('utils.extract.datetime')    # Mock datetime di dalam extract.py
def test_scrape_data_success(mock_dt_in_extract, mock_get, mock_response_page1, capsys):
    # 1. Konfigurasi mock untuk requests.get
    mock_get.side_effect = [
        mock_response_page1,
        mock_response_page1
    ] + [requests.exceptions.RequestException("Mock network error")] * 48

    # 2. Siapkan mock instance yang akan dikembalikan oleh datetime.now()
    #    dan konfigurasikan metode strftime-nya
    mock_now_instance = MagicMock()
    mock_now_instance.strftime.return_value = "2023-01-01 12:00:00"

    # 3. Atur agar mock datetime.now() mengembalikan instance mock di atas
    mock_dt_in_extract.now.return_value = mock_now_instance

    # 4. Panggil fungsi yang diuji
    df = scrape_data()
    captured = capsys.readouterr() # Tangkap output print (opsional)
    # print(captured.out) # Uncomment untuk debug jika perlu

    # 5. Assertions (sebagian besar sama seperti sebelumnya)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 4 # 2 produk x 2 halaman sukses
    assert list(df.columns) == ["title", "price", "rating", "colors", "size", "gender", "timestamp"]

    # Periksa data produk pertama (dari halaman 1)
    assert df.iloc[0]["title"] == "Cool T-Shirt"
    assert df.iloc[0]["price"] == "$25.50"
    assert df.iloc[0]["rating"] == "4.5 / 5"
    assert df.iloc[0]["colors"] == "3 Colors"
    assert df.iloc[0]["size"] == "Size: L"
    assert df.iloc[0]["gender"] == "Gender: Male"
    # Pastikan timestamp sesuai dengan return_value dari mock strftime
    assert df.iloc[0]["timestamp"] == "2023-01-01 12:00:00"

    # Periksa data produk kedua (dari halaman 1)
    assert df.iloc[1]["title"] == "Awesome Jacket"
    assert df.iloc[1]["price"] == "Price Unavailable"
    assert df.iloc[1]["rating"] == "Invalid Rating"
    assert df.iloc[1]["timestamp"] == "2023-01-01 12:00:00" # Timestamp harus sama

    # Periksa data produk ketiga (dari halaman 2)
    assert df.iloc[2]["title"] == "Cool T-Shirt"
    assert df.iloc[2]["price"] == "$25.50"
    assert df.iloc[2]["timestamp"] == "2023-01-01 12:00:00" # Timestamp harus sama

    # Periksa data produk keempat (dari halaman 2)
    assert df.iloc[3]["title"] == "Awesome Jacket"
    assert df.iloc[3]["price"] == "Price Unavailable"
    assert df.iloc[3]["timestamp"] == "2023-01-01 12:00:00" # Timestamp harus sama

    # Periksa jumlah pemanggilan mock
    assert mock_get.call_count == 50

    # Periksa pemanggilan mock datetime dan strftime
    # Pastikan now() dipanggil (setidaknya 4 kali, sekali per produk)
    assert mock_dt_in_extract.now.call_count >= 4
    # Pastikan strftime dipanggil dengan format yang benar pada instance mock
    # Cek panggilan terakhir atau semua panggilan jika perlu
    mock_now_instance.strftime.assert_called_with("%Y-%m-%d %H:%M:%S")
    # Karena strftime dipanggil untuk setiap produk, call_count harusnya 4
    assert mock_now_instance.strftime.call_count == 4

    # Periksa pemanggilan spesifik mock_get (opsional, tapi baik untuk dimiliki)
    mock_get.assert_any_call("https://fashion-studio.dicoding.dev/", headers=ANY, timeout=15)
    mock_get.assert_any_call("https://fashion-studio.dicoding.dev/page2", headers=ANY, timeout=15)