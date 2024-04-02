from sentence_transformers import SentenceTransformer

class LabseApp:

    def __init__(self):
        """
            Load LABSE
        """
        self.model = SentenceTransformer('sentence-transformers/LaBSE')

    def predict(self, sentences):
        """
            Get Embebbings for list of sentences 768 Dimensions
            sentences: list of text
            @return [[em1],[em2]]
        """
        embeddings = [ [float(value) for value in embedding] for embedding in self.model.encode(sentences)]
        return embeddings