# Yapping-Bot: Twitter Auto Reply Bot

Bot otomatis untuk membalas tweet di X (Twitter) berdasarkan filter project tertentu menggunakan AI dari ai.relayer.host

## 🚀 Fitur

- **Auto Reply Tweet**: Membalas tweet secara otomatis berdasarkan filter project
- **Melon Full Auto Raid**: Membalas tweet dari daftar target secara otomatis
- **Auto Raid**: Membalas tweet dari URL yang diberikan
- **Cek Update**: Mengecek apakah ada update terbaru dari repository
- **Duplicate Prevention**: Mencegah reply duplikat
- **Interactive Mode**: Opsi untuk mengedit reply sebelum dikirim
- **Project Filter**: Filter tweet berdasarkan kata kunci project tertentu

## 📋 Prerequisites

- Python 3.7+
- Twitter Developer Account
- AI Key dari [ai.relayer.host](https://ai.relayer.host)

## 🛠️ Instalasi

1. **Clone repository**
```bash
git clone https://github.com/JustPandaEver/Yapping-Bot.git
cd Yapping-Bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**
Buat file `.env` di root directory dengan konfigurasi berikut:
```env
AI_KEY=your_ai_relayer_api_key
CLIENT_ID=your_client_id
REFRESH_TOKEN=your_refresh_token # (akan diisi otomatis setelah login pertama)
```

4. **Setup target users**
Buat file `target.txt` dan masukkan username Twitter target (satu username per baris, tanpa @):
```txt
username1
username2
username3
```

## 🎯 Cara Penggunaan

### Menjalankan Bot
```bash
python main.py
```

### Menu Utama
Saat dijalankan, bot akan menampilkan menu:

1. **Reply tweet** - Membalas tweet user di `target.txt` berdasarkan filter project
2. **Melon Full Auto Raid** - Membalas tweet dari daftar target otomatis (khusus fitur melon)
3. **Auto Raid** - Membalas tweet dari daftar URL yang diberikan
4. **Cek Update** - Mengecek update script dari repository
5. **Keluar** - Keluar dari program

### Penjelasan Menu
- **Reply tweet**: Masukkan kata kunci project (misal: caldera, memex). Bot akan mencari tweet yang mengandung kata kunci tersebut dan membalasnya.
- **Melon Full Auto Raid**: Membalas semua tweet dari daftar target yang diambil otomatis dari server.
- **Auto Raid**: Masukkan daftar URL tweet (format: https://x.com/username/status/1234567890) untuk dibalas secara otomatis.
- **Cek Update**: Mengecek apakah script sudah versi terbaru.

## ⚙️ Konfigurasi & Catatan
- File `.env` hanya membutuhkan `AI_KEY`, `CLIENT_ID`, dan `REFRESH_TOKEN`.
- `REFRESH_TOKEN` akan diminta saat pertama kali login dan diperbarui otomatis.
- File `target.txt` wajib ada untuk menu Reply tweet.
- Tidak ada fitur auto-follow atau penyimpanan ke `done.txt`/`followed.txt`.
- Semua tracking status dilakukan via API ai.relayer.host.

## 🧩 Dependencies

- `requests` - HTTP requests
- `python-dotenv` - Environment variable management

## 🤝 Kontribusi

Bot ini dikembangkan oleh [PandaEver](https://github.com/JustPandaEver)

- **Github**: [JustPandaEver](https://github.com/JustPandaEver)
- **X (Twitter)**: [@PandaEverX](https://twitter.com/PandaEverX)

## ⚠️ Disclaimer

- Gunakan bot ini dengan bijak dan sesuai dengan Terms of Service X (Twitter)
- Bot ini untuk tujuan edukasi dan penggunaan pribadi
- Penulis tidak bertanggung jawab atas penyalahgunaan bot

---

**Note**: Pastikan untuk mematuhi [Twitter Developer Policy](https://developer.twitter.com/en/developer-terms/agreement-and-policy) saat menggunakan bot ini.
