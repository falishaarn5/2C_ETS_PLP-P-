# Kartu Desain

Tuliskan lima keputusan desain penting dalam pekerjaan kalian. Untuk tiap keputusan, sebutkan
alternatif yang ditolak dan alasannya. Contoh topik (boleh memilih yang lain):

- bagaimana parser membedakan `*` sebagai "semua kolom" dan sebagai perkalian;
- di mana dan bagaimana presedensi `AND`/`OR` dinyatakan;
- mengapa error recovery berhenti di `;`, bukan di keyword `SELECT` berikutnya;
- urutan pencarian scope dan akibatnya pada shadowing serta correlated subquery;
- mengapa kolom tanpa qualifier hanya dilihat di scope terdalam, dan apa kelemahannya;
- bagaimana implementasi `INSERT ... SELECT` atau komentar blok kalian.

| No | Keputusan | Alternatif yang ditolak | Alasan |
| --- | --- | --- | --- |
| 1 |Pemrosesan INSERT ... SELECT dilakukan dengan memanggil fungsi _select() dari _insert(), kemudian hasilnya disimpan pada atribut query dalam node Insert.|Membuat parser SELECT khusus untuk INSERT atau memproses bagian SELECT menggunakan regex.|Fungsi _select() sudah menangani struktur SELECT sehingga dapat digunakan kembali tanpa menduplikasi logika parsing. Pendekatan ini juga memungkinkan Analyzer mengenali tabel tujuan sebagai operasi Create (C) dan tabel sumber sebagai Read (R). Membuat parser terpisah akan memperbanyak kode, sedangkan regex tidak sesuai dengan arsitektur parser berbasis AST.|
| 2 |Pemrosesan ekspresi logika dilakukan melalui fungsi _or() dan _and() secara terpisah, dengan _or() memanggil _and() agar operator AND memiliki prioritas lebih tinggi daripada OR.|Memproses AND dan OR dalam satu fungsi dengan tingkat prioritas yang sama atau menyusun ulang AST setelah parsing.|Berdasarkan SPESIFIKASI.md Bagian 3.1, AND memiliki prioritas lebih tinggi daripada OR. Pemisahan fungsi membuat struktur parser lebih mudah dipahami dan sesuai dengan grammar. Selain itu, pendekatan ini menghindari proses tambahan untuk memperbaiki struktur AST setelah parsing.|
| 3 |Ketika terjadi kesalahan sintaks, Parser menggunakan mekanisme _synchronize() untuk melewati token hingga menemukan tanda ;, kemudian melanjutkan pemrosesan statement berikutnya.|Menghentikan seluruh parsing ketika menemukan error atau menggunakan pergantian baris sebagai batas pemulihan.|Berdasarkan SPESIFIKASI.md Bagian 6, kesalahan pada satu statement tidak boleh menghentikan pemrosesan statement valid berikutnya. Tanda ; digunakan karena merupakan pemisah statement SQL, sedangkan pergantian baris tidak dapat dijadikan acuan karena satu statement SQL dapat ditulis dalam beberapa baris.|
| 4 |Resolver melakukan pencarian alias mulai dari scope terdalam menuju scope terluar. Ketika query luar dan subquery menggunakan nama alias yang sama, alias pada scope terdalam akan diprioritaskan.|Melakukan pencarian dari scope terluar atau melarang penggunaan alias yang sama pada query dan subquery.|Berdasarkan SPESIFIKASI.md Bagian 4.5, pencarian alias harus memprioritaskan scope terdekat. Pendekatan ini sesuai dengan konsep Resolving and Binding pada Crafting Interpreters Bab 11. Pencarian dari scope terluar dapat menyebabkan referensi kolom dihubungkan ke tabel yang salah, sedangkan melarang penggunaan alias yang sama akan membatasi SQL yang sebenarnya valid.|
| 5 |Resolver menentukan sumber kolom tanpa qualifier berdasarkan jumlah tabel yang tersedia pada scope saat ini. Jika hanya terdapat satu sumber tabel, kolom dihubungkan ke tabel tersebut. Jika terdapat lebih dari satu sumber, Resolver memberikan peringatan ambigu.|Mewajibkan setiap kolom menggunakan qualifier atau mencari sumber kolom tanpa qualifier pada scope luar.|Berdasarkan SPESIFIKASI.md Bagian 4.5, kolom tanpa qualifier hanya dapat di-resolve secara otomatis ketika terdapat satu sumber tabel dalam scope saat ini. Pendekatan ini memungkinkan SQL yang valid tetap diproses tanpa harus menuliskan qualifier. Sebaliknya, pencarian ke scope luar berpotensi menghasilkan resolusi yang tidak sesuai dengan aturan, sedangkan mewajibkan qualifier akan membatasi penggunaan SQL.|

