from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class Turn(BaseModel):
    role: str   #"user" | "assistant"
    text: str
    meta: Dict[str, Any] ={}

class PairIndex(BaseModel):
    msg_idx: int    # index of the user row (assistant is msg_idx+1)

class RewrittenQuery(BaseModel):
    original_query: str
    processed_query: Optional[str] = None
    is_query_processed: bool = False
    is_query_completed: bool = False
    ai_response: Optional[str] = None
    used_history: List[Turn] = []

class ContextPayload(BaseModel):
    system_prompt: str = ""
    context: str = ""

class MatchDecision(str):
    HARD = "hard"; SOFT = "soft"; REJECT = "reject", NONE = "none"

class MatchResult(BaseModel):
    idx: Optional[int]
    score: Optional[float]
    status: MatchDecision

class EngineInput(BaseModel):
    id: int
    user_id: int
    session_id: int
    query: str
    ai_output: str
    ground_truth: Optional[str] = None
    rag_context: Optional[str] = None
    system_prompt: str = ""
    used_history: List[Turn] = []
    meta: Dict[str, Any] = {}

class EngineOutputs(BaseModel):
    per_engine: Dict[str, Dict[str, Any]] # raw metric name -> value per engine



