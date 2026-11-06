"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
from crud.pipeline import analyze_source
from crud.lexer import tokenize, TokenType

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