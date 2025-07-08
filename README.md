# Twitter Auto Reply Bot

Bot Twitter otomatis untuk melakukan auto reply dan follow user berdasarkan filter project tertentu.

## 🚀 Fitur

- **Auto Reply Tweet**: Membalas tweet secara otomatis berdasarkan filter project
- **Auto Follow User**: Follow user target secara otomatis
- **Rate Limit Handling**: Penanganan rate limit Twitter API yang cerdas
- **Duplicate Prevention**: Mencegah reply duplikat dan follow duplikat
- **Interactive Mode**: Mode interaktif untuk review reply sebelum dikirim
- **Project Filter**: Filter tweet berdasarkan kata kunci project tertentu

## 📋 Prerequisites

- Python 3.7+
- Twitter Developer Account
- API Key dari [ai.relayer.host](https://ai.relayer.host)

## 🛠️ Instalasi

1. **Clone repository**
```bash
git clone https://github.com/JustPandaEver/Yapping-Bot
cd Yapping-Bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**
Buat file `.env` di root directory dengan konfigurasi berikut:
```env
# Twitter API Credentials
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# AI Service API Key
AI_KEY=your_ai_relayer_api_key
```

4. **Setup target users**
Buat file `target.txt` dan masukkan username Twitter target (satu username per baris):
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
Bot akan menampilkan menu dengan 3 opsi:

1. **Follow semua target** - Follow semua user dalam `target.txt`
2. **Reply tweet** - Mode auto reply dengan konfigurasi
3. **Keluar** - Keluar dari program

### Mode Reply Tweet
Ketika memilih opsi 2, bot akan meminta input:

1. **Project Filter**: Masukkan kata kunci project (contoh: `caldera, memex`)
2. **Skip Crosscheck**: Pilih Y/N untuk skip review reply
3. **Auto Follow**: Pilih Y/N untuk auto follow user setelah reply

## 📁 File Output

Bot akan membuat beberapa file untuk tracking:

- `done.txt` - Menyimpan ID tweet yang sudah direply
- `followed.txt` - Menyimpan username yang sudah di-follow

## ⚙️ Konfigurasi

### Rate Limit Handling
Bot secara otomatis menangani rate limit Twitter API dengan:
- Menunggu sesuai header `x-rate-limit-reset`
- Countdown display untuk user
- Retry otomatis setelah rate limit reset

### Delay Settings
- Delay 5 detik setelah get user ID
- Delay 20 detik antara reply tweet
- Delay 12 jam setelah selesai satu cycle

## 🔧 Troubleshooting

### Error Umum

1. **"Forbidden: apikey twitter di .env salah"**
   - Periksa kembali Twitter API credentials di file `.env`
   - Pastikan aplikasi Twitter memiliki permission yang tepat

2. **"User tidak ditemukan"**
   - Periksa username di `target.txt`
   - Pastikan username valid dan tidak di-private

3. **"Tweet tidak ditemukan"**
   - Tweet mungkin sudah dihapus
   - Atau tweet di-private oleh user

### Tips Penggunaan

1. **Gunakan mode interaktif** untuk review reply sebelum dikirim
2. **Monitor rate limit** untuk menghindari suspension
3. **Backup file tracking** secara berkala
4. **Test dengan user dummy** sebelum menggunakan ke target utama

## �� Dependencies

- `tweepy>=4.14.0` - Twitter API wrapper
- `python-dotenv>=0.19.0` - Environment variable management
- `requests` - HTTP requests untuk AI service

## 🤝 Kontribusi

Bot ini dikembangkan oleh [PandaEver](https://github.com/JustPandaEver)

- **Github**: [JustPandaEver](https://github.com/JustPandaEver)
- **Twitter**: [@PandaEverX](https://twitter.com/PandaEverX)

## ⚠️ Disclaimer

- Gunakan bot ini dengan bijak dan sesuai dengan Terms of Service Twitter
- Bot ini untuk tujuan edukasi dan penggunaan pribadi
- Penulis tidak bertanggung jawab atas penyalahgunaan bot

## 📄 License

Project ini open source dan tersedia di bawah lisensi MIT.

---

**Note**: Pastikan untuk mematuhi [Twitter Developer Policy](https://developer.twitter.com/en/developer-terms/agreement-and-policy) saat menggunakan bot ini.
