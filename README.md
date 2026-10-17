# Tamal Portfolio — Proyek Lokal

## Menjalankan

1. Ekstrak ZIP ini.
2. Buka folder `tamal-portfolio-project` di VS Code atau editor pilihanmu.
3. Pastikan Python 3 tersedia, lalu jalankan:

   python start-local.py

   Di Windows, jika perintah python tidak tersedia, gunakan:

   py start-local.py

4. Buka http://localhost:8080 di browser.
5. Edit file, simpan, lalu refresh browser.

Dashboard lokal tersedia di http://localhost:8080/dashboard/. Pada layar mobile, navigasi berada di bagian bawah seperti aplikasi native. Dashboard dapat membaca dan menyimpan `data/portfolio.json` serta mengunggah gambar ke `dist/wp-content/uploads/portfolio/`.

Setiap kali data disimpan, konfigurasi langsung diterapkan ke halaman utama di `dist/index.html` melalui script sinkronisasi. Buka http://localhost:8080/ untuk melihat perubahan. Struktur HTML, CSS, layout, dan animasi portfolio asli tetap dipertahankan; yang diperbarui hanya konten teks dan gambar.

Alternatif dari terminal di folder proyek:

   python -m http.server 8080 --directory dist

Gunakan server lokal karena URL aset dimulai dari root `/`. Membuka index.html dengan klik ganda tidak akan memuat semua aset dengan benar.

## Struktur

- dist/index.html — halaman utama.
- dist/project/<nama-proyek>/index.html — 10 halaman detail proyek.
- dist/portfolio-category/ — 2 halaman kategori.
- dist/wp-content/uploads/ — gambar, video, dan berkas animasi.
- dist/wp-content/cache/autoptimize/css/ — stylesheet asli.
- dist/wp-content/cache/autoptimize/js/ — skrip asli.
- dist/wp-content/plugins/, dist/wp-content/themes/, dist/wp-includes/ — dependensi frontend asli.
- dist/external/ — salinan font dan dependensi eksternal.
- dashboard/index.html — dashboard editor lokal.
- data/portfolio.json — file data portfolio yang diedit dashboard.
- scripts/portfolio-sync.js — sinkronisasi konten dashboard ke frontend utama.

Tidak memerlukan npm install atau build. HTML, CSS, dan JavaScript dapat diedit langsung. Beberapa berkas asli sudah diminifikasi; gunakan fitur Format Document pada editor agar lebih mudah dibaca. Untuk mengganti gambar, pertahankan nama dan jalurnya atau ubah referensinya di HTML/CSS.

## Cakupan

Paket ini adalah seluruh proyek replika statis yang dibuat dari tampilan publik https://tamalsen.dev/ pada 17 Oktober 2026. Ini bukan source code backend WordPress, database, atau dashboard Elementor. Tautan sosial dan situs proyek eksternal tetap menuju tujuan aslinya. Konten, branding, dan atribusi pemilik asli tetap disertakan. Analytics pihak ketiga telah dihapus.

Pemeriksaan tautan internal, aset langsung, dan sintaks JavaScript telah lolos. Perbandingan visual 1:1 lewat browser belum dilakukan.
# yopiwebportofolio
