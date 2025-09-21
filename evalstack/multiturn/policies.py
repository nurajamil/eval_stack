# Import libraries
from pydantic import BaseModel
from typing import Optional

class QueryRewritePolicy(BaseModel):
    safety_max_pairs: Optional[int] = None # None means unlimited
    allow_malformed_skip: bool = True # skip out of order rows