# Laporan Bug

Salin blok di bawah untuk setiap bug. Bagian **Akar masalah** wajib ditulis dengan kata-kata
sendiri dan memakai konsep dari *Crafting Interpreters* (sebutkan bab). Bagian ini diuji lisan.

---

## Bug 1: Huruf kecil pada keyword SQL tidak dikenali oleh Lexer

**Ditemukan oleh:** falisha · **Diperbaiki oleh:** falisha

**Gejala.** Pada awalnya, input yang diberikan adalah select (dengan huruf kecil) dan output actualnya dikenali dengan IDENT sedangkan output yang diharapkan berdasarkan SPESIFIKASI.md bagian 2.2 dikenali sebagai KEYWORD karena keyword tidak peka dengan huruf besar & kecil sehingga perlu dilakukan normalisasi menjadi huruf besar.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```select id from t;
```

**Akar masalah.** Karena di dalam lexer.py belum menerapkan case-insensitive dalam mengenali keyword SQL sehingga dalam pencocokan keyword/reserved word antara huruf besar dan kecil masih salah. Akibatnya, keyword seperti select dikenali sebagai IDENT bukan sebagai KEYWORD. Hal ini melanggar konsep scanning pada buku crafting interpreters bab 4 yaitu proses membedakan identifier dengan reserved word berdasarkan lexeme yang dikenali. 

**Perbaikan.** File dan fungsi yang diubah adalah crud/lexer.py. Dilakukan normalisasi bentuk kata saat menentukan KEYWORD, tanpa mengubah bentuk nama yang ditangani parser. Alternatif yang ditolak adalah dengan mengubah seluruh variasi kata dengan kapitalisasi di KEYWORDS, karena cara tersebut tidak efisien, memperbanyak kode, dan menyulitkan pemeliharaan.

**Test regresi.** Pengujian dilakukan melalui fungsi test_keyword_lowercase_tetap_dikenali pada file tests/test_tambahan.py. Test tersebut terbukti gagal sebelum perbaikan dan berhasil setelah Lexer diperbaiki.

**Peran AI.** AI membantu dalam mencari alternatif perbaikan selain mencantumkan seluruh variasi kapitalisasi keyword SQL, yaitu dengan melakukan normalisasi huruf menjadi uppercase sebelum proses pencocokan dengan daftar KEYWORDS. Solusi tersebut kemudian diverifikasi melalui test regresi sebelum dan sesudah perbaikan.
---

## Bug 2: Komentar blok multiline tidak dilewati oleh Lexer

**Ditemukan oleh:** falisha · **Diperbaiki oleh:** falisha

**Gejala.** Pada awalnya, input SQL yang mengandung komentar blok /* ... */ tidak diproses dengan benar oleh Lexer. Isi komentar masih dapat terbaca sebagai bagian dari token SQL, padahal berdasarkan SPESIFIKASI.md Bagian 2.2, komentar blok seharusnya dilewati dan tidak menghasilkan token.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```
/* mengambil kolom id
   dari tabel pelanggan */
SELECT id FROM pelanggan;

```

**Akar masalah.** Karena lexer.py belum menangani komentar blok yang diawali /* dan diakhiri */, Lexer belum dapat membedakan isi komentar dengan bagian SQL yang harus ditokenisasi. Akibatnya, proses scanning tidak melewati seluruh isi komentar dengan benar. Hal ini berkaitan dengan konsep Scanning dalam buku Crafting Interpreters Bab 4, yaitu scanner harus mengenali karakter yang perlu diproses menjadi token dan karakter yang harus diabaikan.

**Perbaikan.** Perbaikan dilakukan pada crud/lexer.py dengan menambahkan penanganan komentar blok agar Lexer melewati seluruh karakter sampai menemukan penutup */, termasuk ketika komentar berada pada beberapa baris. Alternatif yang tidak dipilih adalah menghapus komentar menggunakan regex sebelum proses scanning karena dapat mengganggu posisi baris dan kolom yang diperlukan untuk pelaporan kesalahan.

**Test regresi.** Pengujian dilakukan melalui fungsi test_komentar_blok_multiline_dilewati pada file tests/test_tambahan.py. Test tersebut telah dibuktikan gagal sebelum perbaikan dan berhasil setelah Lexer diperbaiki.

**Peran AI.** AI digunakan sebagai alat bantu diskusi untuk memahami proses scanning pada komentar blok multiline dan mengeksplorasi kemungkinan penyebab kesalahan. Berdasarkan hasil diskusi tersebut, dilakukan pemeriksaan pada kode Lexer, kemudian perbaikan diuji menggunakan test regresi untuk memastikan komentar blok dapat dilewati dengan benar.

---

## Bug 3: Kolom tanpa qualifier tidak berhasil di resolve ke satu tabel 

**Ditemukan oleh:** falisha · **Diperbaiki oleh:** falisha

**Gejala.** Pada awalnya, kolom yang ditulis tanpa qualifier atau nama tabel, seperti id, tidak berhasil di-resolve oleh Resolver meskipun hanya terdapat satu tabel pada statement SQL. Berdasarkan SPESIFIKASI.md Bagian 4.5, kolom tanpa qualifier seharusnya dapat dihubungkan secara otomatis ke tabel tersebut apabila hanya ada satu sumber tabel dalam scope saat ini.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```
SELECT id FROM pelanggan;

```

**Akar masalah.** Karena resolver.py belum menangani proses resolusi kolom tanpa qualifier ketika hanya terdapat satu sumber tabel, Resolver tidak dapat menentukan tabel asal kolom meskipun sumbernya sudah jelas. Hal ini berkaitan dengan konsep Resolving and Binding dalam buku Crafting Interpreters Bab 11, yaitu proses menghubungkan penggunaan suatu nama dengan deklarasi yang sesuai berdasarkan scope.

**Perbaikan.** Perbaikan dilakukan pada crud/resolver.py dengan menambahkan mekanisme pencarian sumber tabel dalam scope saat ini ketika kolom tidak memiliki qualifier. Jika hanya terdapat satu sumber tabel, kolom dihubungkan ke sumber tersebut. Alternatif yang tidak dipilih adalah mengharuskan seluruh kolom menggunakan qualifier karena cara tersebut tidak sesuai dengan spesifikasi dan membatasi penulisan SQL yang valid.

**Test regresi.** Pengujian dilakukan melalui fungsi test_kolom_tanpa_qualifier_diresolve_ke_satu_tabel pada file tests/test_tambahan.py. Test tersebut telah dibuktikan gagal sebelum perbaikan dan berhasil setelah Resolver diperbaiki.

**Peran AI.** AI membantu memperjelas aturan resolusi kolom ketika hanya terdapat satu sumber tabel dalam suatu scope. Pemahaman tersebut digunakan untuk meninjau kondisi yang belum ditangani oleh Resolver, kemudian dibuat test regresi untuk memeriksa apakah kolom tanpa qualifier dapat dihubungkan dengan tabel yang sesuai.

---

---

## Bug 4: ALias shadowing tidak memprioritaskan scope terdalam

**Ditemukan oleh:** falisha · **Diperbaiki oleh:** falisha

**Gejala.** Pada awalnya, Resolver tidak memprioritaskan alias tabel yang dideklarasikan pada scope terdalam ketika terdapat alias dengan nama yang sama pada query luar dan subquery. Akibatnya, referensi kolom berpotensi dihubungkan ke tabel yang salah. Berdasarkan SPESIFIKASI.md Bagian 4.5, pencarian alias seharusnya dilakukan mulai dari scope terdalam menuju scope terluar agar alias lokal memiliki prioritas.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```
SELECT p.id
FROM pelanggan p
WHERE p.id IN (
    SELECT p.id
    FROM pesanan p
);

```

**Akar masalah.** Karena mekanisme pencarian alias pada resolver.py belum memprioritaskan scope terdalam, alias yang dideklarasikan pada query luar dapat ditemukan lebih dahulu dibandingkan alias lokal dalam subquery. Hal ini tidak sesuai dengan konsep Resolving and Binding pada buku Crafting Interpreters Bab 11, yaitu pencarian nama harus mengikuti aturan lexical scope sehingga deklarasi terdekat memiliki prioritas.

**Perbaikan.** Perbaikan dilakukan pada crud/resolver.py, khususnya mekanisme pencarian alias, dengan mengubah urutan pencarian agar dimulai dari scope terdalam menuju scope terluar. Dengan demikian, alias lokal pada subquery akan digunakan terlebih dahulu apabila terdapat nama alias yang sama. Alternatif yang tidak dipilih adalah melarang penggunaan alias yang sama pada query luar dan subquery karena penggunaan tersebut diperbolehkan dan dapat dibedakan berdasarkan scope masing-masing.

**Test regresi.** Pengujian dilakukan melalui fungsi test_alias_shadowing_scope_terdalam pada file tests/test_tambahan.py. Test tersebut telah dibuktikan gagal sebelum perbaikan dan berhasil setelah mekanisme pencarian alias diperbaiki.

**Peran AI.** AI digunakan untuk mendiskusikan konsep alias shadowing melalui contoh query dan subquery yang menggunakan nama alias sama. Dari proses tersebut, dilakukan penelusuran terhadap urutan pencarian scope pada Resolver. Hasilnya diperiksa menggunakan test regresi untuk memastikan deklarasi pada scope terdalam memperoleh prioritas.

---

---

## Bug 5: Scope DELETE tidak ditutup sehingga bocor ke statement berikutnya

**Ditemukan oleh:** falisha · **Diperbaiki oleh:** falisha

**Gejala.** Pada awalnya, Resolver masih dapat mengenali alias tabel yang berasal dari statement DELETE sebelumnya ketika memproses statement SQL berikutnya. Padahal, berdasarkan SPESIFIKASI.md Bagian 4.5, setiap statement harus memiliki scope tersendiri sehingga alias dari statement sebelumnya tidak boleh digunakan kembali tanpa deklarasi.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```
DELETE FROM pelanggan p WHERE p.id = 1;
SELECT p.id FROM pesanan o;

```

**Akar masalah.** Karena fungsi _delete() pada crud/resolver.py hanya memanggil _push() untuk membuat scope baru tanpa diikuti _pop() untuk menutupnya, scope dari statement DELETE tetap tersimpan setelah proses resolusi selesai. Akibatnya, alias p dari statement sebelumnya masih dapat ditemukan ketika Resolver memproses statement berikutnya. Hal ini tidak sesuai dengan konsep Resolving and Binding pada buku Crafting Interpreters Bab 11, yaitu pengelolaan scope harus memastikan deklarasi nama hanya berlaku dalam ruang lingkup yang sesuai.

**Perbaikan.** Perbaikan dilakukan pada fungsi _delete() dalam file crud/resolver.py dengan menambahkan pemanggilan self._pop() setelah proses resolusi kondisi WHERE selesai. Dengan demikian, scope yang dibuat melalui _push() akan ditutup setelah statement DELETE diproses. Alternatif yang tidak dipilih adalah menghapus seluruh scope secara manual setelah setiap statement karena berpotensi mengganggu pengelolaan scope bertingkat pada subquery.

**Test regresi.** Pengujian dilakukan melalui fungsi test_scope_delete_tidak_bocor_ke_statement_berikutnya pada file tests/test_tambahan.py. Test tersebut terbukti gagal sebelum perbaikan karena alias dari statement DELETE sebelumnya masih dikenali. Setelah dilakukan perbaikan dengan menambahkan self._pop(), test berhasil lulus sehingga membuktikan bahwa scope DELETE tidak lagi bocor ke statement berikutnya.

**Peran AI.** AI dimanfaatkan untuk membantu menelusuri hubungan antara pemanggilan _push() dan _pop() dalam pengelolaan scope. Pemeriksaan difokuskan pada fungsi _delete() dan dampaknya terhadap statement berikutnya. Untuk membuktikan masalah tersebut, digunakan test regresi yang dijalankan sebelum perbaikan dan dibandingkan kembali setelah perubahan kode.

---
