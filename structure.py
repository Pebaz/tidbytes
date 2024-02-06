from tidbytes import *

class Struct(Mem):
    def __init__(self, *args, **kwargs):
        self.buffer = Mem(sum(args))


class Ieee754(Struct):
    Sign: Unsigned[1]
    Exponent: Unsigned[23]
    Mantissa: Unsigned[12]

    def __float__(self):
        return float(self.buffer)
