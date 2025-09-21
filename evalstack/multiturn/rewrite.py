# Import libraries
from typing import List, Optional
import pandas as pd

# Import files
from ..types import Turn, RewrittenQuery 
from .policies import QueryRewritePolicy
from .self_containment import SelfContainmentDetector
from .resolver import QueryProcessor
from ...utils.logging_utils import setup_logging

logger = setup_logging("rewrite", log_file="logs/multiturn.log")

def build_completed_query_from_turns(
        group: pd.DataFrame,
        msg_idx: int,
        is_query_complete_fn,
        processing_query_fn,
        safety_max_pairs: int | None = None,
        ):
    """
    Build a self-contained query for a multi-turn chat by backtracking through previous 
    user-assistant pairs within the same session until the query is deemed self-contained.
    
    Returns:
    - original_query: str
        The raw current user's message.
    - processed_query: str | None
        A condensed seld-contained question from the transcript block.
    - is_query_processed: bool
        True if we appended prior turns into a block for processing.
    - is_query_completed: bool
        True if the block is deemed self-contained by the llm checker.
    - bot_response: str
        The latest assistant reply that we are evaluating for ragas.
    - used_historuy: list[dict]
        Chronological turns included in the block (audit).
    """

    logger.info(f"Initiate building query with group: {group}, idx: {msg_idx}")

    n = len(group)

    # Step 1: Sanity check - current row must be user
    if group.iloc[msg_idx]["sender"] != "user":
        return None, None, False, False, None, []
    
    if msg_idx + 1 >= n or group.iloc[msg_idx + 1]["sender"] != "assistant":
        return None, None, False, False, None, []
    
    bot_response = group.iloc[msg_idx + 1]["text"]
    curr_user_query = group.iloc[msg_idx]["text"]
    is_processed = False
    
    # Step 2: Seed with the current user message, excluding current bot reply
    used_history = [{"role": "user", "text": curr_user_query}]
    block = f"User: {curr_user_query}"

    # Quick check: Is query already self-contained?
    is_completed = is_query_complete_fn(curr_user_query)
    if is_completed:
        return curr_user_query, None, is_processed, is_completed, bot_response, used_history
    
    # Step 3: Walk backward through pairs - previous user, previous assistant
    
    j = msg_idx - 1 # this is the previous assistant row
    pairs_added = 0

    # Step 4: Unlimited backtrack until we run out of history
    while j >= 1:
        prev_bot = group.iloc[j]
        prev_user = group.iloc[j-1]

        if prev_user["sender"] == "user" and prev_bot["sender"] == "assistant":
            is_processed = True
            # Prepend in chronological order
            used_history.insert(0, {"role": "assistant", "text": prev_bot["text"]})
            used_history.insert(0, {"role": "user", "text": prev_user["text"]})

            block = (
                f"User: {prev_user['text']}\n"
                f"Assistant: {prev_bot['text']}\n"
                f"{block}"
            )

            pairs_added += 1

            processed_query = processing_query_fn(block)
            is_completed = is_query_complete_fn(processed_query)
            if is_completed:
                return curr_user_query, processed_query, is_processed, is_completed, bot_response, used_history
            
            j -=2
        
        else:
            j -= 1 # malformed ordering

    logger.debug(f"Queries that are incomplete and require human review: {block}")
    
    #processed_query = processing_query_fn(block)
    #is_completed = is_query_complete_fn(processed_query)

    return curr_user_query, None, is_processed, False, bot_response, used_history # covered the entire session and query still not completed - human - review