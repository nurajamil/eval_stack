# Import libraries
import pandas as pd
from typing import List, Dict, Any
import ast

# Import files
from ..multiturn.policies import QueryRewritePolicy
from .pair import iter_user_assistant_pairs
from ..utils.logging_utils import setup_logging

logger = setup_logging("orchestrator", log_file="logs/pipeline.log")

def evaluate_sessions(
        master_df: pd.DataFrame,
        eval_df: pd.DataFrame,
        hard_thr: float,
        soft_thr: float,
        engines: List[str],
        policy: QueryRewritePolicy = QueryRewritePolicy(safety_max_pairs=None)
) -> pd.DataFrame:
    """
    Evaluate user-bot exchanges in eval_df against master_df questions.
    Returns a DataFrame of evaluation results. 
    """

    results = []
    master_qa = master_df["question"].tolist()

    # Step 1: Filter and sort
    eval_df = eval_df[eval_df["evaluated"] == False].copy()
    eval_df = eval_df.sort_values(by=["user_id", "session_id", "id"]).reset_index(drop=True)

    # Step 2: Group by user and session
    grouped = eval_df.groupby(["user_id", "session_id"], sort=False)

    for (user_id, session_id), group in grouped:
        group = group.sort_values(by="id").reset_index(drop=True)

        for msg_idx, user_row, ai_row in iter_user_assistant_pairs(group):

            # Step 3: Build completed query for this pair
            original_query, processed_query, is_processed, is_completed, bot_answer, used_history  = build_completed_query(
                group=group, 
                msg_idx=i, 
                is_query_complete_fn=is_query_complete, 
                processing_query_fn=processing_query
                )
            logger.info(f"Completed building query. Original query: {original_query}, processed query: {processed_query}")

            # If the LLM still can't produce a self-contained query, we still proceed
            # Can also enqueue for human review here as a policy choice.
            if is_processed:
                query_for_match = processed_query
            else:
                query_for_match = original_query
            
            # Step 4: Extract system prompt and context.
            context_raw = user_row.get("context", [])

            try:
                context_data = ast.literal_eval(context_raw) if isinstance(context_raw, str) else context_raw
                sp = context_data.get("system_prompt", "")
                if isinstance(sp, list):
                    system_prompt = " ".join([entry.get("content", "") for entry in sp])
                elif isinstance(sp, dict):
                    system_prompt = sp.get("content", "") 
                else:
                    system_prompt = str(sp)
                
                clist = context_data.get("context", [])
                if isinstance(clist, list):
                    context = " ".join([c.get("content", "") for c in clist])
                elif isinstance(clist, dict):
                    context = clist.get("content", "")
                else:
                    context = str(clist) if clist else ""
                
            except Exception as e:
                logger.error(f"Error parsing context for session {session_id}, row {i}: {context_raw}, {e}")


            # Step 5: Semantic match
            match_idx, score, match_status = (None, None, "no_match")
            if query_for_match:
                match_idx, score, match_status = semantic_match(query_for_match, master_qa, hard_threshold=HARD_THR, soft_threshold=SOFT_THR)
                
                
            logger.info(f"[session {session_id} i={i}] semantic_match -> idx={match_idx}, score={score}, status={match_status}")


            ground_truth = master_df.iloc[int(match_idx)]["ground_truth"] if match_idx is not None else None
            matched_id = master_df.iloc[int(match_idx)]["id"] if match_idx is not None else None

            # Build batch and run metrics
            batch = {
                "id": int(user_row.get("id")),
                "user_id": int(user_row.get("user_id")),
                "session_id": int(user_row.get("session_id")),
                "original_user_query": original_query,
                "processed_user_query": processed_query,
                "is_query_processed": is_processed,
                "is_query_completed": is_completed,
                "model_answer": bot_answer,
                "context": context,
                "system_prompt": system_prompt,
                "ground_truth": ground_truth,
                "used_history": used_history,
                "clean_pair": clean_pair,
            }

            logger.debug(f"Processing batch: {batch}")

            #metrics_scores = run_all_metrics(batch)
            engine_results = run_selected_engines(batch)

            # flatten
            flat_engine_results = {}
            for engine_name, metrics in (engine_results or {}).items():
                if not isinstance(metrics, dict):
                    logger.warning(f"Skipping engine because metrics is not a dict: {engine_name}")
                    continue
                for metric_name, value in metrics.items():
                    col_name = f"{metric_name}_{engine_name}"
                    flat_engine_results[col_name] = value

            # Store result
            results.append({
                **batch,
                "match_score": score,
                "match_found": match_idx is not None,
                "matched_masterqa_id": matched_id,
                "semantic_match_status": match_status,
                "engine_results": engine_results,
                **flat_engine_results
            })

            # Move to next potential pair
            i += 2
            

    logger.info(f"Evaluated all results.")

    return pd.DataFrame(results)
        

             




    
