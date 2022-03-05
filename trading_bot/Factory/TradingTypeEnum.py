from enum import Enum
from .SideSwitch.SideSwitchStrategyEnum import *
from .StaBasisArb.StaBasisArbStrategyEnum import *

class TradingTypeEnum(Enum):
    StaBasisArb = StaBasisArbStrategyEnum
    SideSwitch = SideSwitchStrategyEnum