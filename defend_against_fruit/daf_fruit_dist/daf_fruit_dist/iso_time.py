from datetime import datetime
import time


class ISOTime(object):
    def __init__(self, date, gmt_offset):
        self.__date = date
        self.__gmt_offset = gmt_offset

    @classmethod
    def now(cls, now_fn=datetime.now, time=time):
        gmt_offset = time.altzone if time.daylight else time.timezone
        return cls(date=now_fn(), gmt_offset=gmt_offset)

    @property
    def as_str(self):
        return (
            self.__date.isoformat()[:-3] +
            '{:+05}'.format(self.__gmt_offset / -36))
