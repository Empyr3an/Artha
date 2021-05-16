import ta
import pandas as pd
import numpy as np

def ichimoku(df, ichi):
    
    df["tenkan_sen"] = ichi.ichimoku_conversion_line()
    df["kijun_sen"] = ichi.ichimoku_base_line()
    df["senkou_span_a"] = ichi.ichimoku_a()
    df["senkou_span_b"] = ichi.ichimoku_b()
    df["chikou_span"] = ichi.ichimoku_chikou()
    return df