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

## Bug 6 : Subquery pada UPDATE ditandai sebagai U

**Ditemukan oleh:** Salsabila · **Diperbaiki oleh:** Salsabila

**Gejala.** Pada statement UPDATE yang memiliki subquery di bagian SET atau WHERE, tabel yang hanya dibaca lewat subquery ikut tercatat sebagai U. Padahal berdasarkan SPESIFIKASI.md bagian 5, tabel di dalam subquery selalu R, dan hanya tabel target UPDATE yang boleh bernilai U. Pada test, tabel crm.cabang dan crm.vip bernilai 'U', seharusnya 'R'.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```
UPDATE crm.pelanggan SET kota = (SELECT MAX(kota) FROM crm.cabang)
WHERE id IN (SELECT id FROM crm.vip);
```

**Akar masalah.** Pada cabang Update di fungsi analyze_statement (crud/analyzer.py), fungsi _collect dipanggil dengan nilai "U" untuk assignment.value dan stmt.where. Fungsi _collect meneruskan nilai op tersebut ke semua subquery di dalam ekspresi, sehingga tabel di dalam subquery ikut mendapat operasi milik tabel target. Padahal subquery hanya membaca data. Masalah ini mirip dengan konsep yg ada pada pengelolaan scope Resolving and Binding (Crafting Interpreters Bab 11), dimana informasi yang dibawa saat menelusuri pohon harus berubah ketika masuk ke bagian yang cakupannya berbeda.

**Perbaikan.** Perbaikan dilakukan pada cabang Update di fungsi analyze_statement dalam crud/analyzer.py, dengan mengubah dua pemanggilan _collect dari "U" menjadi "R". Alternatif yang tidak dipilih adalah menghapus parameter op dan menulis "R" langsung di dalam _collect, karena perubahannya mengenai banyak fungsi dan berisiko mengganggu cabang lain yang sudah benar.

**Test regresi.** Pengujian dilakukan melalui fungsi test_update_subquery_di_set_dan_where_adalah_read pada file tests/test_tambahan.py. Test ini gagal pada analyzer.py versi awal karena crm.cabang dan crm.vip bernilai 'U', dan berhasil setelah perbaikan.

**Peran AI.** AI dimanfaatkan untuk membantu membaca analyzer.py terhadap SPESIFIKASI.md Bagian 5 dan menunjuk cabang Update sebagai bagian yang dicurigai. Untuk membuktikannya, test ditulis lebih dulu, dijalankan pada kode awal (dengan git stash pada analyzer.py) sampai gagal, lalu dijalankan lagi setelah perbaikan sampai lulus.
---

## Bug 7 : Operator <> terpecah menjadi dua token

**Ditemukan oleh:** Salsabila · **Diperbaiki oleh:** Salsabila

**Gejala.** Operator <> terbaca sebagai token < diikuti token >. Akibatnya parser gagal pada laporan_penjualan.sql dengan pesan "Baris 6, kolom 41: diharapkan ekspresi, ditemukan '>'", sehingga daftar statement kosong dan CRUD matrix tidak terbentuk. Gejalanya muncul di test analyzer, padahal sumbernya ada di lexer. Operator <=, >=, dan != sudah benar.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```
SELECT a FROM t WHERE x <> 1;
```

**Akar masalah.** Pada fungsi _scan_token (crud/lexer.py), cabang untuk karakter < hanya memeriksa karakter = dengan self._match("="), dan tidak memeriksa karakter >. Karena itu <> diproses sebagai < lalu > sebagai token terpisah. Hal ini tidak sesuai dengan konsep maximal munch pada Scanning (Crafting Interpreters Bab 4), yaitu lexer harus mengambil lexeme terpanjang yang cocok, hal ini terbukti di SPESIFIKASI.md bagian 2.5.

**Perbaikan.** Perbaikan dilakukan pada cabang karakter < di fungsi _scan_token dalam crud/lexer.py, dengan menambahkan pemeriksaan elif self._match(">") yang menghasilkan token <>. Alternatif yang tidak dipilih adalah menggabungkan token < dan > di parser, karena parser tidak bisa membedakan <> dari < > yang dipisah spasi, dan penentuan token seharusnya dilakukan oleh lexer.

**Test regresi.** Pengujian dilakukan melalui fungsi test_operator_tidak_sama_adalah_satu_token pada file tests/test_tambahan.py. Test ini gagal pada lexer sebelum perbaikan karena hasilnya ['<', '>'], dan berhasil setelah perbaikan.

**Peran AI.** AI dimanfaatkan untuk membantu menafsirkan pesan error dari parser dan menduga bahwa penyebabnya ada di lexer. Dugaan itu diuji sendiri dengan menjalankan tokenize pada <>, <=, >=, dan !=, lalu dibuktikan dengan test yang dijalankan memakai lexer sebelum perbaikan (git checkout commit 4de4ef7 pada lexer.py) dan sesudah perbaikan.

---

## Bug 8 : Escape '' di dalam string memutus string

**Ditemukan oleh:** Salsabila · **Diperbaiki oleh:** Salsabila

**Gejala.** String yang berisi dua kutip berturut-turut, misalnya 'O''Brien', terbaca sebagai dua token STRING (O dan Brien). Padahal menurut SPESIFIKASI.md bagian 2.4, dua kutip berturut-turut mewakili satu karakter kutip, sehingga hasilnya harus satu token bernilai O'Brien.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```
SELECT a FROM t WHERE n = 'O''Brien';
```

**Akar masalah.** Fungsi _string pada crud/lexer.py berhenti membaca string begitu bertemu kutip tunggal pertama, tanpa melihat karakter sesudahnya. Padahal keputusan apakah "akhir string atau bukan" memerlukan satu karakter lookahead dengan peek. Hal ini tidak sesuai dengan konsep pemindaian string literal pada Scanning (Crafting Interpreters Bab 4).

**Perbaikan.** Perbaikan dilakukan pada fungsi _string dalam crud/lexer.py. Ketika bertemu kutip, kode memeriksa self._peek(): jika karakter berikutnya juga kutip, satu kutip ditambahkan ke nilai string dan kutip kedua dilewati, lalu pembacaan dilanjutkan. Alternatif yang tidak dipilih adalah menggabungkan dua token STRING setelah pemindaian, karena dua string berurutan bisa saja sah di tempat lain dan posisi baris serta kolom token menjadi tidak akurat.

**Test regresi.** . Pengujian dilakukan melalui fungsi test_string_dengan_kutip_ganda_adalah_satu_token pada file tests/test_tambahan.py. Test ini gagal pada lexer sebelum perbaikan karena hasilnya ['O', 'Brien'], dan berhasil setelah perbaikan.

**Peran AI.** AI dimanfaatkan untuk membantu memeriksa lexer.py terhadap SPESIFIKASI.md Bagian 2 dan menunjuk fungsi _string sebagai bagian yang belum menangani escape. Untuk membuktikannya, test ditulis lebih dulu, dijalankan pada lexer sebelum perbaikan sampai gagal, lalu dijalankan lagi setelah perbaikan sampai berhasil.

---

## Bug 9 : Error recovery membuang semua token sampai akhir file
**Ditemukan oleh:** Salsabila · **Diperbaiki oleh:** Salsabila

**Gejala.** Ketika ada satu statement yang rusak, semua statement yg valid setelahnya akan ikut hilang. Padahal SPESIFIKASI.md bagian 6 menyatakan bahwa setelah error, token dibuang sampai dan termasuk tanda ; berikutnya, lalu statement sesudahnya tetap diproses.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```
SELECT FROM t; DELETE FROM x;
```

**Akar masalah.** Fungsi _synchronize pada crud/parser.py memanggil _advance() berulang kali sampai _at_end(), sehingga titik aman yang dipakai adalah akhir file, bukan akhir statement. Hal ini tidak sesuai dengan konsep panic mode dan synchronization pada Parsing Expressions (Crafting Interpreters Bab 6), yaitu setelah error parser harus berhenti di titik sinkronisasi, yaitu batas statement, agar bisa melanjutkan parsing.

**Perbaikan.** Perbaikan dilakukan pada fungsi _synchronize dalam crud/parser.py, dengan menghentikan loop segera setelah token SEMICOLON dikonsumsi. Alternatif yang tidak dipilih adalah berhenti di keyword awal statement seperti SELECT, karena kata SELECT juga muncul di dalam subquery dan INSERT ... SELECT, sehingga satu statement rusak bisa menghasilkan lebih dari satu error.

**Test regresi.** Pengujian dilakukan melalui fungsi test_recovery_statement_valid_sesudah_error_tetap_diproses pada file tests/test_tambahan.py. Test ini gagal pada parser sebelum perbaikan (assert 0 == 1 pada jumlah statement), dan berhasil setelah perbaikan.

**Peran AI.** AI dimanfaatkan untuk membantu membandingkan parser.py dengan SPESIFIKASI.md bagian 6 dan menunjuk fungsi _synchronize. Untuk membuktikannya, test ditulis lebih dulu, dijalankan pada parser sebelum perbaikan (dengan git stash pada parser.py) sampai gagal, lalu dijalankan lagi setelah perbaikan sampai berhasil.

---

## Bug 10 : Operator <> terpecah menjadi dua token

**Ditemukan oleh:** Salsabila · **Diperbaiki oleh:** Salsabila

**Gejala.** Ekspresi a = 1 OR b = 2 AND c = 3 terbaca sebagai (a = 1 OR b = 2) AND c = 3. Padahal berdasarkan SPESIFIKASI.md Bagian 3.1, OR memiliki presedensi terendah dan AND berada di atasnya, sehingga seharusnya terbaca a = 1 OR (b = 2 AND c = 3). Pada test, akar pohon bernilai AND, seharusnya OR.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```
SELECT x FROM t WHERE a = 1 OR b = 2 AND c = 3;
```

**Akar masalah.** Fungsi _logical pada crud/parser.py menangani AND dan OR dalam satu loop yang sama, sehingga keduanya dianggap setara dan dikelompokkan dari kiri ke kanan. Hal ini tidak sesuai dengan konsep presedensi pada Parsing Expressions (Crafting Interpreters Bab 6), yaitu setiap tingkat presedensi dibentuk oleh satu fungsi tersendiri yang memanggil tingkat di atasnya.

**Perbaikan.** Perbaikan dilakukan pada crud/parser.py dengan memecah _logical menjadi dua fungsi: _or yang memanggil _and, dan _and yang memanggil _not. Fungsi _expr kemudian memanggil _or. Alternatif yang tidak dipilih adalah memakai tabel presedensi dengan satu loop (precedence climbing), karena gayanya berbeda dari fungsi ekspresi lain di file ini dan perubahannya lebih besar.

**Test regresi.** Pengujian dilakukan melalui fungsi test_and_lebih_tinggi_dari_or pada file tests/test_tambahan.py. Test ini gagal pada parser sebelum perbaikan karena akar pohon bernilai AND, dan berhasil setelah perbaikan.

**Peran AI.** AI dimanfaatkan untuk membantu mencocokkan fungsi-fungsi ekspresi di parser.py dengan tabel presedensi pada SPESIFIKASI.md bagian 3.1 dan menunjuk fungsi _logical. Untuk membuktikannya, test ditulis lebih dulu, dijalankan pada parser sebelum perbaikan sampai gagal, lalu dijalankan lagi setelah perbaikan sampai berhasil.
---

## Bug 11 : LEFT OUTER JOIN ditolak oleh parser

**Ditemukan oleh:** Salsabila · **Diperbaiki oleh:** Salsabila

**Gejala.** Statement dengan LEFT OUTER JOIN menghasilkan error "Baris 1, kolom 22: diharapkan JOIN, ditemukan 'OUTER'". Padahal berdasarkan grammar pada SPESIFIKASI.md bagian 3, dimana kata OUTER bersifat opsional. 

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```
SELECT a FROM t LEFT OUTER JOIN u ON t.id = u.id;
```

**Akar masalah.** Fungsi _join pada crud/parser.py hanya mengonsumsi kata LEFT, lalu langsung mengharapkan kata JOIN dengan _expect_kw("JOIN"). Bagian [ "OUTER" ] pada grammar tidak ikut diterjemahkan ke kode. Hal ini tidak sesuai dengan konsep penerjemahan grammar ke recursive descent pada Representing Code dan Parsing Expressions (Crafting Interpreters Bab 5 dan 6), yaitu elemen opsional pada grammar harus diperiksa dengan pemanggilan match yang tidak wajib berhasil.

**Perbaikan.** Perbaikan dilakukan pada fungsi _join dalam crud/parser.py, dengan menambahkan self._match_kw("OUTER") setelah LEFT sehingga kata OUTER dikonsumsi jika ada.

**Test regresi.** Pengujian dilakukan melalui fungsi test_left_outer_join_diterima pada file tests/test_tambahan.py. Test ini gagal pada parser sebelum perbaikan karena error ditemukan 'OUTER', dan berhasil setelah perbaikan.

**Peran AI.** AI dimanfaatkan untuk membantu mencocokkan fungsi _join dengan aturan join pada SPESIFIKASI.md Bagian 3 dan menunjuk kata OUTER yang tidak dikonsumsi. Untuk membuktikannya, test ditulis lebih dulu, dijalankan pada parser sebelum perbaikan sampai gagal, lalu dijalankan lagi setelah perbaikan sampai berhasil.

---

## Bug 12 : Pada TODO T1 INSERT ... SELECT belum didukung parser

**Ditemukan oleh:** Salsabila · **Diperbaiki oleh:** Salsabila

**Gejala.** Statement INSERT ... SELECT menghasilkan error "INSERT ... SELECT belum didukung", sehingga statement tidak masuk ke AST dan tabel target (C) serta tabel sumber (R) tidak muncul di CRUD matrix. Test test_insert_select dan test_matrix_laporan_penjualan gagal karena hal ini.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```
INSERT INTO arsip (id) SELECT id FROM pesanan WHERE total > 10;
```

**Akar masalah.**  Pada fungsi _insert (crud/parser.py), cabang untuk SELECT sengaja dibiarkan melempar ParseError sebagai TODO. Padahal grammar insert_stmt pada SPESIFIKASI.md bagian 3 memiliki dua cabang setelah daftar kolom, yaitu VALUES atau select_stmt. Berdasarkan konsep recursive descent pada Parsing Expressions (Crafting Interpreters Bab 6), satu aturan grammar dipetakan ke satu fungsi, sehingga aturan select_stmt cukup dipanggil kembali lewat _select().

**Perbaikan.** Perbaikan dilakukan pada fungsi _insert dalam crud/parser.py, dengan memanggil self._select() pada cabang SELECT dan menyimpan hasilnya di field query pada node Insert. Cabang Insert di analyzer.py sudah siap membaca query, sehingga tabel sumber otomatis bernilai R dan tabel target bernilai C. Alternatif yang tidak dipilih adalah membuat parser SELECT khusus untuk INSERT, karena akan menduplikasi logika yang sudah ada.

**Test regresi.** Pengujian dilakukan melalui fungsi test_insert_select_menghasilkan_create_dan_read pada file tests/test_tambahan.py. Test ini gagal pada parser sebelum perbaikan karena error "belum didukung", dan berhasil setelah perbaikan.

**Peran AI.** AI dimanfaatkan untuk membantu menemukan bagian TODO(T1) pada fungsi _insert dan mengusulkan pemanggilan _select() kembali. Untuk membuktikannya, test ditulis lebih dulu, dijalankan pada parser sebelum perbaikan sampai gagal, lalu dijalankan lagi setelah perbaikan sampai lulus.

---