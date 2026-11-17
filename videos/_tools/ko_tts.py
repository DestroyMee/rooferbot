"""Koreanische Sprachausgabe: Mimic3-Stimme "KSS" (via sherpa-onnx-Release auf GitHub), Lautschrift über espeak-ng.
Modell: vits-mimic3-ko_KO-kss_low (Ordner über KO_TTS_DIR)."""
import json, os
import numpy as np

KO_DIR = os.environ.get("KO_TTS_DIR", "")
_sess = _ids = _backend = None


def _init():
    global _sess, _ids, _backend
    if _sess: return
    import onnxruntime as ort, espeakng_loader
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    from phonemizer.backend import EspeakBackend
    EspeakWrapper.set_library(espeakng_loader.get_library_path())
    EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
    _backend = EspeakBackend("ko", preserve_punctuation=True, with_stress=True)
    _sess = ort.InferenceSession(os.path.join(KO_DIR, "ko_KO-kss_low.onnx"))
    _ids = {}
    for line in open(os.path.join(KO_DIR, "tokens.txt"), encoding="utf-8"):
        tok, i = line.rstrip("\n").rsplit(" ", 1)
        _ids[tok if tok else " "] = int(i)


def phonemes(text):
    _init()
    return _backend.phonemize([text], strip=True)[0]


def synth(text, length_scale=1.0):
    """Gibt (samples float32, sample_rate) zurück."""
    _init()
    ph = phonemes(text)
    seq = [_ids["^"], _ids["_"]]
    for wi, word in enumerate(ph.split()):
        if wi: seq += [_ids["#"], _ids["_"]]
        for ch in word:
            if ch in _ids: seq += [_ids[ch], _ids["_"]]
    seq += [_ids["$"]]
    x = np.array([seq], dtype=np.int64)
    out = _sess.run(None, {"input": x, "input_lengths": np.array([x.shape[1]], dtype=np.int64),
                           "scales": np.array([0.667, length_scale, 0.8], dtype=np.float32)})[0]
    return out.squeeze().astype(np.float32), 22050


if __name__ == "__main__":
    import soundfile as sf, sys
    for t in sys.argv[1:] or ["안녕하세요", "감사합니다", "사랑해요"]:
        a, sr = synth(t); print(t, phonemes(t), round(len(a) / sr, 2), "s", "peak", round(float(np.abs(a).max()), 2))
