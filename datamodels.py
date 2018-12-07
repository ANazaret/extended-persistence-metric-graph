from enum import Enum


class IntervalType(Enum):
    ORDINARY = 0
    EXTENDED = 1
    RELATIVE = 2

    @staticmethod
    def from_tricked_interval(start, end, infinity_value):
        count = int(start > infinity_value) + int(end > infinity_value)
        return IntervalType(count)
