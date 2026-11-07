# Laporan Akhir

## 1. Hasil evaluasi
Dievaluasi: audit.sql, campuran_error.sql, laporan_penjualan.sql, pemeliharaan.sql (27 triple)

Metode   Precision  Recall     F1
parser        1.00    1.00   1.00
regex         0.65    0.81   0.72

[regex]
  salah ditemukan (FP): ('audit.sql', 16, 'sesi', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 4, 'pesanan', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 8, 'keranjang', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'D')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pesanan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'rahasia', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 15, 'pesanan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.alamat', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.pelanggan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'pelanggan_lama', 'U')
  salah ditemukan (FP): ('pemeliharaan.sql', 15, 'crm.alamat', 'R')
  terlewat (FN):       ('audit.sql', 2, 'pesanan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pesanan', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.alamat', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.pelanggan', 'R')

## 2. Tiga kasus di mana regex salah

Untuk tiap kasus: SQL-nya, kesalahan regex, dan mengapa parser benar (kaitkan dengan konsep
lexing, parsing, atau resolusi).

1. Keyword SQL di dalam komentar
SQL:

-- DELETE FROM pelanggan
SELECT p.nama, SUM(o.total) AS omzet
FROM pelanggan p
JOIN pesanan o ON o.pelanggan_id = p.id;

Kesalahan regex. Regex mengenali DELETE FROM pelanggan sebagai operasi Delete meskipun perintah tersebut berada di dalam komentar. Akibatnya, tabel pelanggan tercatat memiliki operasi D yang sebenarnya tidak dijalankan. Selain itu, kesalahan dalam menentukan awal statement menyebabkan nomor baris hasil ekstraksi tidak sesuai dengan posisi statement sebenarnya.

Mengapa parser benar. Lexer mengenali komentar yang diawali -- dan mengabaikan seluruh isinya sampai akhir baris. Dengan demikian, keyword DELETE dalam komentar tidak dihasilkan sebagai token dan tidak diproses oleh Parser. Hal ini sesuai dengan konsep Scanning dalam Crafting Interpreters Bab 4, yaitu membedakan bagian teks yang harus diubah menjadi token dan bagian yang perlu diabaikan.

2. Keyword SQL di dalam st
SQL:

SELECT o.id
FROM pesanan o
WHERE o.catatan <> 'FROM rahasia';

Kesalahan regex. Regex menganggap pola FROM rahasia di dalam string sebagai referensi tabel, sehingga menghasilkan operasi Read (R) terhadap tabel rahasia yang sebenarnya tidak digunakan dalam query.

Mengapa parser benar. Lexer mengenali 'FROM rahasia' sebagai satu token STRING, bukan sebagai keyword FROM dan identifier rahasia. Oleh karena itu, Parser memahami bahwa teks tersebut merupakan nilai string dalam kondisi WHERE, bukan sumber tabel. Proses ini berkaitan dengan konsep Scanning dan tokenisasi pada Crafting Interpreters Bab 4.

3. Target DELETE dianggap sebagSQL:

DELETE FROM pesanan WHERE tanggal < :batas;

Kesalahan regex. Regex mengenali tabel pesanan sebagai target operasi Delete (D), tetapi juga menganggapnya sebagai tabel yang dibaca (R) karena terdapat keyword FROM. Akibatnya, CRUD matrix menghasilkan operasi tambahan yang tidak sesuai dengan peran tabel.

Mengapa parser benar. Parser mengenali struktur DELETE FROM sebagai statement penghapusan dan membentuk node AST bertipe Delete. Analyzer kemudian mengidentifikasi pesanan sebagai target operasi D, bukan sumber operasi R. Hal ini sesuai dengan konsep Parsing Expressions dan representasi struktur sintaks dalam Crafting Interpreters Bab 5–6, yaitu pemrosesan berdasarkan struktur grammar, bukan sekadar pencocokan kata.

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1. Kolom tanpa qualifier ketika terdapat lebih dari satu tabel
SQL:

SELECT nama
FROM pelanggan p
JOIN pesanan o ON o.pelanggan_id = p.id;

Akibat pada CRUD matrix. Resolver tidak dapat memastikan apakah kolom nama berasal dari tabel pelanggan atau pesanan karena tidak tersedia informasi skema database. Resolver hanya dapat memberikan peringatan bahwa kolom tersebut ambigu. Meskipun demikian, operasi Read (R) terhadap kedua tabel tetap dapat dicatat dengan benar dalam CRUD matrix. Keterbatasan ini terutama memengaruhi hasil resolusi kolom, bukan identifikasi operasi CRUD tingkat tabel.

Informasi yang dibutuhkan. Diperlukan skema database yang berisi daftar kolom pada setiap tabel agar Resolver dapat menentukan asal kolom secara tepat.

2. View dan trigger tidak dapat ditelusuri hingga tabel aslinya
SQL:

SELECT * FROM v_laporan;

Akibat pada CRUD matrix. Program mencatat v_laporan sebagai objek yang dibaca (R), tetapi tidak dapat mengetahui tabel asli yang digunakan untuk membentuk view tersebut. Begitu juga dengan trigger, program tidak dapat mendeteksi operasi tambahan yang dijalankan secara otomatis oleh database. Akibatnya, CRUD matrix hanya menggambarkan operasi yang terlihat secara langsung pada teks SQL dan dapat melewatkan tabel yang diakses secara tidak langsung.

Informasi yang dibutuhkan. Diperlukan metadata database, terutama definisi view, trigger, dan hubungan antarobjek database, untuk mengetahui seluruh tabel yang terlibat dalam operasi tersebut.

3. Sintaks SQL di luar grammar yang didukung
SQL:

WITH recent AS (
    SELECT id FROM pesanan
    WHERE tanggal > :batas
)
SELECT * FROM recent;

Akibat pada CRUD matrix. Program belum mendukung Common Table Expression (WITH) karena berada di luar cakupan grammar yang diimplementasikan. Akibatnya, Parser menghasilkan kesalahan sintaks dan statement tersebut tidak dimasukkan ke CRUD matrix. Operasi Read (R) terhadap tabel pesanan menjadi tidak tercatat meskipun terdapat dalam query.

Informasi yang dibutuhkan. Diperlukan perluasan grammar, penambahan representasi AST untuk CTE, serta pengembangan Resolver dan Analyzer agar dapat memahami hubungan antara CTE dan tabel sumbernya.

## 4. Pembagian kerja

Pengerjaan SQL CRUD Extractor dilakukan secara berkelompok dengan pembagian tugas pada komponen Lexer, Parser, Resolver, Analyzer, pengujian, dan dokumentasi.

| Bagian Pekerjaan | Anggota |
|---|---|
| Perbaikan keyword SQL lowercase pada Lexer | Falisha |
| Penanganan komentar blok multiline pada Lexer (TODO T3) | Falisha |
| Resolusi kolom tanpa qualifier pada Resolver (TODO T2) | Falisha |
| Perbaikan alias shadowing pada Resolver | Falisha |
| Perbaikan kebocoran scope DELETE pada Resolver | Falisha |
| Perbaikan operator `<>` dan escape string `''` pada Lexer | Salsabila Ramdhani Zahra |
| Implementasi `INSERT ... SELECT` pada Parser (TODO T1) | Salsabila Ramdhani Zahra |
| Perbaikan error recovery pada Parser | Salsabila Ramdhani Zahra |
| Perbaikan presedensi AND/OR pada Parser | Salsabila Ramdhani Zahra |
| Penanganan LEFT OUTER JOIN pada Parser | Salsabila Ramdhani Zahra |
| Perbaikan klasifikasi subquery UPDATE pada Analyzer | Salsabila Ramdhani Zahra |
| Pelabelan ground truth `audit.sql` dan `pemeliharaan.sql` | Falisha |
| Pengujian regresi | Masing-masing anggota sesuai bug yang dikerjakan |
| Pengujian kasus tepi dan dokumentasi | Dikerjakan bersama sesuai pembagian tugas |

Bagaimana kami memastikan keduanya memahami seluruh kode?
Untuk memastikan kedua anggota memahami keseluruhan program, kami mempelajari alur pemrosesan SQL mulai dari Lexer, Parser, Resolver, hingga Analyzer serta mendiskusikan permasalahan dan perbaikan pada masing-masing komponen. Setiap bug diperiksa menggunakan test regresi untuk membandingkan perilaku program sebelum dan sesudah perbaikan. Selain itu, hasil evaluasi parser dan regex dianalisis untuk memahami perbedaan kedua pendekatan serta kesesuaiannya dengan ground truth. Melalui proses tersebut, kedua anggota dapat memahami fungsi setiap komponen, alasan perubahan kode, dan hasil pengujian sebagai persiapan demonstrasi.
