# Import libraries
from sentence_transformers import SentenceTransformer, util
import os

# Import files
from ..utils.logging_utils import setup_logging
from .threshold_router import apply_thresholds

class SemanticMatcher:
    def __init__(self, questions, model_name=SENTENCE_EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)
        self.questions = list(questions)
        if self.questions:
            self._qa_vecs = self.model.encode(self.questions)
        else:
            self._qa_vecs = None
    
    def refresh_if_changed(self, questions):
        q_list = list(questions or [])
        if q_list != self.questions:
            self.questions(q_list)

    def match(self, query):
        if (
            not query
            or self._qa_vecs is None
            or self._qa_vecs.size == 0
            or not self.questions
            ):
            return None, 0, "no_match"
        
        q_vec = self.model.encode(query)
        scores = util.cos_sim(q_vec, self._qa_vecs)[0]
        best_idx = scores.argmax().item()
        best_score = float(scores[best_idx])
        
        return best_score