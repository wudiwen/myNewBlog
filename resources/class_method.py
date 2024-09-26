# coding=utf-8


class Date(object):

    def __init__(self, year=2021, month=4, day=30):
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def get_date(cls, string_date):
        year, month, day = map(int, string_date.split('-'))
        date = cls(year, month, day)
        return date

    def output_date(self):
        print("Year: %d, Month: %d, Day: %d" % (self.year, self.month, self.day))


if __name__ == "__main__":
    # x = Date(2022, 12, 25)
    # x.output_date()

    # 如果有 类方法
    d = Date.get_date('2022-12-25')
    d.output_date()
