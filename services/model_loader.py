import spacy
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from sklearn.preprocessing import normalize
import numpy as np


class ModelLoader:
    _instance = None

    SPACY_NLP_MODEL = 'el_core_news_sm'
    SENTENCE_MODEL = 'lighteternal/stsb-xlm-r-greek-transfer'

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._nlp = spacy.load(cls.SPACY_NLP_MODEL)
            cls._instance._model = SentenceTransformer(cls.SENTENCE_MODEL)
            cls._instance._tokenizer = AutoTokenizer.from_pretrained(cls.SENTENCE_MODEL)
        return cls._instance

    @property
    def nlp(self):
        return self._nlp

    @property
    def model(self):
        return self._model

    @property
    def tokenizer(self):
        return self._tokenizer

    @model.setter
    def model(self, value):
        self._model = value

    @nlp.setter
    def nlp(self, value):
        self._nlp = value

    @tokenizer.setter
    def tokenizer(self, value):
        self._tokenizer = value

    def tokenize(self, str):
        return self.tokenizer.tokenize(str)

    def round_decimal_points(self, float_list, decimal_points=4):
        rounded_list = [round(float_val, decimal_points) for float_val in float_list]
        return rounded_list

    def normalize_l2(self, vector):
        float_array = np.array(vector)
        reshaped_array = float_array.reshape(1, -1)
        normalized_array = normalize(reshaped_array, norm='l2')
        normalized_list = self.round_decimal_points(normalized_array.tolist()[0], 4)
        return normalized_list

    def generate_embeddings(self, query_text):
        sentence_embeddings = self.model.encode(query_text).tolist()
        return self.normalize_l2(sentence_embeddings)

    def generate_embeddings_euc(self, query_text):
        sentence_embeddings = self.model.encode(query_text).tolist()
        return self.round_decimal_points(sentence_embeddings)
