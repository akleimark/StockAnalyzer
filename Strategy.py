from abc import ABC, abstractmethod

import pandas as pd
from matplotlib import pyplot as plt


class TradingStrategy(ABC):
    @abstractmethod
    def execute(self, stock_name, stock_data, start_value=10000):
        pass