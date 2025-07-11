from typing import Any

import pandas as pd

from .base import BaseResponse


class DataFrameResponse(BaseResponse):
    def __init__(self, value: Any = None, last_code_executed: str = None):
        value = self.format_value(value)
        super().__init__(value, "dataframe", last_code_executed)

    def format_value(self, value):
        return value
        # if isinstance(value, dict):
        #     for key,item in value.items():
        #         if isinstance(item,pd.DataFrame):

        #     return pd.DataFrame(value) if isinstance(value, dict) else value
        # else:
        #     return value
