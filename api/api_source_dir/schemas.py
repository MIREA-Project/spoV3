from typing import Optional

from pydantic import BaseModel


class Statistic(BaseModel):
    steps: Optional[int] = None
