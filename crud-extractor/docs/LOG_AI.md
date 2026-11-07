# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |
| 1 | Falisha | Diskusi penyebab keyword SQL huruf kecil tidak dikenali Lexer. | Diterima dengan penyesuaian | Normalisasi keyword diperlukan agar pengenalan token tidak bergantung pada huruf besar atau kecil. | Memeriksa lexer.py dan menjalankan test_keyword_lowercase_tetap_dikenali. |
| 2 | Falisha | Meminta penjelasan penanganan komentar blok /* ... */ yang mencakup beberapa baris (TODO T3). | Diterima dengan penyesuaian | Lexer harus melewati seluruh isi komentar tanpa menghasilkan token dan tetap memperbarui posisi baris. | Memeriksa hasil tokenisasi dan menjalankan test_komentar_blok_multiline_dilewati. |
| 3 | Falisha | Diskusi resolusi kolom tanpa qualifier ketika hanya terdapat satu sumber tabel (TODO T2). | Diterima dengan penyesuaian | Kolom dapat dihubungkan ke satu sumber tabel pada scope saat ini sesuai spesifikasi. | Memeriksa resolver.py dan menjalankan test_kolom_tanpa_qualifier_diresolve_ke_satu_tabel. |
| 4 | Falisha | Meminta analisis masalah alias shadowing pada query bersarang. | Diterima dengan penyesuaian | Alias pada scope terdalam harus diprioritaskan agar referensi tidak terhubung ke tabel pada scope luar secara keliru. | Memeriksa urutan pencarian scope dan menjalankan test_alias_shadowing_scope_terdalam. |
| 5 | Falisha | Diskusi penyebab kebocoran scope setelah statement DELETE. | Diterima dengan penyesuaian | Scope yang dibuka pada proses resolusi DELETE harus ditutup agar alias tidak terbawa ke statement berikutnya. | Memeriksa keseimbangan _push() dan _pop(), serta menjalankan test_scope_delete_tidak_bocor_ke_statement_berikutnya. |
| 6 | Falisha | Meminta bantuan meninjau kesesuaian test regresi dengan bug yang diperbaiki. | Diterima dengan penyesuaian | Setiap test harus menguji perilaku spesifik yang sebelumnya bermasalah, bukan sekadar memastikan program berjalan. | Membandingkan hasil test sebelum dan sesudah perbaikan serta menjalankan python -m pytest -q. |
| 7 | Falisha | Diskusi pelabelan ground truth untuk audit.sql dan pemeliharaan.sql. | Diterima dengan penyesuaian | Label CRUD harus ditentukan berdasarkan peran tabel dalam statement SQL, bukan menyalin keluaran parser atau regex. | Memeriksa kembali statement SQL dan membandingkan label dengan ketentuan SPESIFIKASI.md Bagian 5. |
| 8 | Falisha | Meminta bantuan memahami hasil evaluasi parser dan regex serta penyebab perbedaan precision, recall, dan F1-score. | Diterima dengan penyesuaian | Analisis diperlukan untuk menjelaskan mengapa pendekatan parser lebih akurat pada dataset pengujian. | Menjalankan python evaluate.py dan mencocokkan hasilnya dengan ground truth. |


**Refleksi (3-5 kalimat).** Di bagian mana AI paling membantu? Di mana AI keliru atau
menyesatkan, dan bagaimana kalian mengetahuinya?

AI paling membantu dalam memahami penyebab bug pada Lexer dan Resolver, terutama terkait pengenalan token, pencarian alias berdasarkan scope, dan kebocoran scope pada statement DELETE. Selain itu, AI membantu memberikan alternatif penyelesaian, menyusun pengujian regresi, serta meninjau kesesuaian dokumentasi dengan spesifikasi tugas. Namun, saran AI tidak selalu langsung sesuai kebutuhan, seperti ketika mengusulkan tujuh keputusan desain padahal dokumen hanya membutuhkan lima keputusan. Ketidaksesuaian tersebut diketahui dengan memeriksa kembali instruksi tugas, sehingga hasil dari AI tetap perlu ditinjau, disesuaikan, dan diverifikasi melalui kode serta pengujian.