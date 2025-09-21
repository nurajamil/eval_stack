# Import libraries
import pandas as pd
from typing import List

# Import files
from ...types import Turn

def df_to_turn(group: pd.DataFrame) -> List[Turn]:
    return [Turn(role=row["sender"], text=row["text"]) for _, row in group.iterrows()]