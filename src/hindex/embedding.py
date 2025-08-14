from __future__ import annotations
import hashlib, re
from typing import Iterable
import numpy as np

TOKEN_RE = re.compile(r"[A-Za-z_]\w+|\d+")

def _tokens(text: str) -> Iterable[str]:
    tks = TOKEN_RE.findall(text.lower())
    for t in tks:
        yield t
        if len(t) >= 4:
            for i in range(len(t) - 2):
                yield t[i:i+3]

def hashing_vectorize(text: str, dim: int = 768, seed: int = 0) -> np.ndarray:
    rng_salt = seed.to_bytes(4, "little", signed=False)
    vec = np.zeros(dim, dtype=np.float32)
    for tok in _tokens(text):
        h = hashlib.blake2b(tok.encode("utf-8"), digest_size=16, person=b"hindex", salt=rng_salt).digest()
        idx = int.from_bytes(h[:8], "little") % dim
        sign = 1.0 if (h[8] & 1) == 0 else -1.0
        vec[idx] += sign
    n = float(np.linalg.norm(vec))
    if n > 0:
        vec /= n
    return vec
