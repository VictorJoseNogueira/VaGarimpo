import spacy

nlp = spacy.load("pt_core_news_sm")


class StopWordsRemove:
    def __init__(self, text: str):
        self.text = text

    @staticmethod
    def _normalize_text(text: str) -> str:
        doc = nlp(text)
        tokens = []
        for token in doc:
            if token.is_space or token.is_punct or token.is_stop:
                continue
            lemma = token.lemma_.lower().strip()
            if len(lemma) <= 1:
                continue
            tokens.append(lemma)
        return " ".join(tokens)

    def preprocess_text(self) -> str:
        return self._normalize_text(self.text)

    @classmethod
    def preprocess(cls, text: str) -> str:
        return cls._normalize_text(text)
