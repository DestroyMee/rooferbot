"""Allgemeine Sprachausgabe für Piper-Stimmen (sherpa-onnx-Releases auf GitHub), Lautschrift über espeak-ng.
Beispiel: synth("/pfad/vits-piper-pl_PL-gosia-medium", "pl", "Dzień dobry")"""
import glob, json, os
import numpy as np

_cache = {}


def _load(model_dir, lang):
    key = (model_dir, lang)
    if key in _cache: return _cache[key]
    import onnxruntime as ort, espeakng_loader
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    from phonemizer.backend import EspeakBackend
    EspeakWrapper.set_library(espeakng_loader.get_library_path())
    EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
    backend = EspeakBackend(lang, preserve_punctuation=True, with_stress=True)
    onnx = [f for f in glob.glob(os.path.join(model_dir, "*.onnx"))][0]
    cfg = json.load(open(onnx + ".json"))
    ids = {k: v[0] for k, v in cfg["phoneme_id_map"].items()}
    sess = ort.InferenceSession(onnx)
    _cache[key] = (backend, ids, sess, cfg)
    return _cache[key]


def phonemes(model_dir, lang, text):
    return _load(model_dir, lang)[0].phonemize([text], strip=True)[0]


def synth(model_dir, lang, text, length_scale=1.0):
    backend, ids, sess, cfg = _load(model_dir, lang)
    ph = backend.phonemize([text], strip=True)[0]
    seq = [ids["^"], ids["_"]]
    for ch in ph:
        if ch in ids: seq += [ids[ch], ids["_"]]
    seq.append(ids["$"])
    inf = cfg.get("inference", {})
    x = np.array([seq], dtype=np.int64)
    out = sess.run(None, {"input": x, "input_lengths": np.array([x.shape[1]], dtype=np.int64),
                          "scales": np.array([inf.get("noise_scale", 0.667), length_scale * inf.get("length_scale", 1), inf.get("noise_w", 0.8)], dtype=np.float32)})[0]
    return out.squeeze().astype(np.float32), cfg["audio"]["sample_rate"]


if __name__ == "__main__":
    import sys
    d, lang = sys.argv[1], sys.argv[2]
    for t in sys.argv[3:]:
        a, sr = synth(d, lang, t); print(t, "|", phonemes(d, lang, t), "|", round(len(a) / sr, 2), "s")
