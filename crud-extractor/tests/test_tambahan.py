"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
import ast

from crud.pipeline import analyze_source
from crud.lexer import tokenize, TokenType
from crud.parser import parse_sql
from crud.resolver import Resolver
from crud import ast_nodes as ast

def test_update_subquery_di_set_dan_where_adalah_read():
    # Regresi: subquery di UPDATE sebelumnya ditandai "U", seharusnya "R" (Spec Bagian 5)
    sql = """UPDATE crm.pelanggan SET kota = (SELECT MAX(kota) FROM crm.cabang)
             WHERE id IN (SELECT id FROM crm.vip);"""
    assert analyze_source(sql).matrix() == {
        "crm.cabang": "R",        # subquery di SET: hanya dibaca
        "crm.pelanggan": "U",     # target UPDATE
        "crm.vip": "R",           # subquery di WHERE: hanya dibaca
    }

def test_operator_tidak_sama_adalah_satu_token():
    # Regresi: "<>" terpecah jadi "<" lalu ">" (maximal munch, Spec 2.5)
    toks = tokenize("a <> b")
    assert [t.value for t in toks if t.type == TokenType.OP] == ["<>"]

def test_string_dengan_kutip_ganda_adalah_satu_token():
    # Regresi: 'O''Brien' sebelumnya terpecah jadi dua STRING (Spec 2.4)
    toks = [t for t in tokenize("'O''Brien'") if t.type == TokenType.STRING]
    assert [t.value for t in toks] == ["O'Brien"]

def test_insert_select_menghasilkan_create_dan_read():
    # TODO T1: sebelumnya ParseError "belum didukung"
    sql = "INSERT INTO arsip (id) SELECT id FROM pesanan WHERE total > 10;"
    assert analyze_source(sql).matrix() == {"arsip": "C", "pesanan": "R"}
    
def test_recovery_statement_valid_sesudah_error_tetap_diproses():
    # Regresi: _synchronize membuang semua token, statement sesudah error hilang (Spec 6)
    script = parse_sql("SELECT FROM t; DELETE FROM x;")
    assert len(script.errors) == 1
    assert len(script.statements) == 1

def test_and_lebih_tinggi_dari_or():
    # Regresi: OR dan AND setara. Harus a=1 OR (b=2 AND c=3) (Spec 3.1)
    where = parse_sql("SELECT x FROM t WHERE a = 1 OR b = 2 AND c = 3").statements[0].where
    assert where.op == "OR" and where.right.op == "AND"

def test_left_outer_join_diterima():
    # Regresi: OUTER tidak dikonsumsi (Spec 3, aturan join)
    assert parse_sql("SELECT a FROM t LEFT OUTER JOIN u ON t.id = u.id").errors == []

def test_keyword_lowercase_tetap_dikenali():
    # Regresi: keyword lowercase sebelumnya tidak dikenali dengan benar.
    toks = tokenize("select nama from pelanggan")
    assert toks[0].type == TokenType.KEYWORD
    assert toks[0].value.upper() == "SELECT"

def test_komentar_blok_multiline_dilewati():
    # Regresi: komentar /* ... */ sebelumnya menghasilkan LexError.
    toks = tokenize("/* komentar\n dua baris */ SELECT")
    assert [t.value.upper() for t in toks
            if t.type == TokenType.KEYWORD] == ["SELECT"]

def test_kolom_tanpa_qualifier_diresolve_ke_satu_tabel():
    # Regresi: kolom tanpa qualifier sebelumnya menghasilkan resolved=None.
    script = parse_sql("SELECT nama FROM pelanggan WHERE aktif = 1;")
    resolver = Resolver()
    resolver.resolve_script(script)
    stmt = script.statements[0]

    # Periksa kolom nama pada SELECT
    assert stmt.columns[0].expr.resolved == "pelanggan"
    # Periksa kolom aktif pada WHERE
    assert stmt.where.left.resolved == "pelanggan"

def test_alias_shadowing_scope_terdalam():
    # Regresi: alias yang sama harus merujuk ke scope terdalam.
    sql = """
    SELECT p.id
    FROM pelanggan p
    WHERE p.id IN (
        SELECT p.pelanggan_id
        FROM pesanan p
    );
    """

    script = parse_sql(sql)
    assert script.errors == [], script.errors

    resolver = Resolver()
    diagnostics = resolver.resolve_script(script)
    # Ambil semua referensi kolom dengan qualifier p.
    kolom_p = [
        node for node in ast.iter_nodes(script)
        if isinstance(node, ast.ColumnRef)
        and node.qualifier == "p"
    ]

    # p.id pada query luar harus merujuk ke pelanggan.
    assert kolom_p[0].resolved == "pelanggan"
    # p.pelanggan_id pada subquery harus merujuk ke pesanan.
    assert kolom_p[2].resolved == "pesanan"
    assert diagnostics == []

def test_scope_delete_tidak_bocor_ke_statement_berikutnya():
    # Regresi: scope DELETE tidak boleh terlihat oleh statement berikutnya.
    from crud.parser import parse_sql
    from crud.resolver import Resolver

    sql = """
    DELETE FROM pelanggan p WHERE p.id = 1;
    SELECT p.id FROM pesanan o;
    """

    script = parse_sql(sql)
    assert script.errors == [], script.errors

    diagnostics = Resolver().resolve_script(script)

    assert any(
        d.level == "error"
        and "alias 'p' tidak terdefinisi" in d.message
        for d in diagnostics
    )

def test_insert_select_dengan_subquery():
    # Edge case: tabel pada subquery berisiko terlewat sehingga tidak ditandai sebagai "R".
    sql = """
    INSERT INTO arsip (id)
    SELECT p.id
    FROM pesanan p
    WHERE p.id IN (
        SELECT v.id FROM vip v
    );
    """
    result = analyze_source(sql)

    assert result.matrix() == {
        "arsip": "C",
        "pesanan": "R",
        "vip": "R"
    }

def test_edge_komentar_dengan_operator():
    # Edge case: operator dalam komentar blok berisiko terbaca sebagai token SQL.
    toks = tokenize("/* SELECT a <> b */ SELECT nama FROM pelanggan")
    keywords = [
        t.value.upper() for t in toks
        if t.type == TokenType.KEYWORD
    ]
    assert keywords == ["SELECT", "FROM"]


def test_edge_mixed_case_left_outer_join():
    # Edge case: keyword mixed-case pada LEFT OUTER JOIN berisiko gagal dikenali Parser.
    sql = """
    SeLeCt p.nama
    FrOm pelanggan p
    LeFt OuTeR JoIn pesanan o
    On p.id = o.pelanggan_id
    """
    script = parse_sql(sql)
    assert script.errors == [], script.errors


def test_edge_presedensi_dengan_operator():
    # Edge case: kombinasi AND, OR, dan <> bisa membentuk AST yang salah.
    sql = """
    SELECT id FROM pelanggan
    WHERE status <> 0 OR aktif = 1 AND kota <> 2
    """
    script = parse_sql(sql)
    assert script.errors == [], script.errors

    where = script.statements[0].where
    assert where.op == "OR"
    assert where.right.op == "AND"


def test_edge_shadowing_dengan_kolom_tanpa_qualifier():
    # Edge case: kolom tanpa qualifier pada subquery berisiko di resolve ke scope luar.
    sql = """
    SELECT p.id
    FROM pelanggan p
    WHERE p.id IN (
        SELECT pelanggan_id
        FROM pesanan p
    )
    """
    script = parse_sql(sql)
    assert script.errors == [], script.errors

    resolver = Resolver()
    diagnostics = resolver.resolve_script(script)
    kolom = [
    node for node in ast.iter_nodes(script)
    if isinstance(node, ast.ColumnRef)
    ]
    kolom_dalam = [
        c for c in kolom
        if c.name == "pelanggan_id" and c.qualifier is None
    ]

    assert len(kolom_dalam) == 1
    assert kolom_dalam[0].resolved == "pesanan"
    assert diagnostics == []