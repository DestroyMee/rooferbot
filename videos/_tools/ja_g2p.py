"""Japanische Lautschrift für Kokoro ohne MeCab-Wörterbuch.
Erwartet die Aussprache als Katakana (mit ー für lange Vokale), z. B. "アリガトー".
Nutzt die Kana→IPA-Tabelle von misaki (dieselbe, mit der Kokoro trainiert wurde)."""
from types import SimpleNamespace
from misaki import ja


class _FakeTagger:
    def __call__(self, text):
        return [SimpleNamespace(surface=text, feature=SimpleNamespace(pron=text, kana=text), char_type=6, is_unk=False)]


class KanaG2P(ja.JAG2P):
    def __init__(self):
        self.tagger = _FakeTagger()
        self.table = dict(ja.HEPBURN)
        self.exceptions = {}


_g = None
def phonemize(kana):
    global _g
    _g = _g or KanaG2P()
    return _g(kana)


if __name__ == "__main__":
    for k in ["コンニチワ!", "アリガトー!", "ハイ", "イイエ", "オネガイシマス", "サヨーナラ", "ゴメンナサイ", "ダイスキ!", "トモダチ", "スゴイ!"]:
        print(k, phonemize(k))
