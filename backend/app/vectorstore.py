import faiss
import numpy as np
import os
from typing import List

class FaissStore:
    def __init__(self, dim=384, path="faiss.index"):
        self.dim = dim
        self.path = path
        if os.path.exists(path):
            self.index = faiss.read_index(path)
        else:
            self.index = faiss.IndexFlatIP(dim)
            faiss.write_index(self.index, path)

    def add(self, vecs: List[np.ndarray]):
        arr = np.vstack(vecs).astype('float32')
        self.index.add(arr)
        faiss.write_index(self.index, self.path)

    def search(self, vec, k=5):
        D, I = self.index.search(np.array([vec]).astype('float32'), k)
        return I[0], D[0]
