from django.utils import timezone
import calendar


class Day:
    def __init__(self, number, past=False):
        self.number = number
        self.past = past


class Calendar(calendar.Calendar):

    def __init__(self, year, month):
        super().__init__(firstweekday=6)
        self.year = year + (month // 12)
        self.month = month % 12
        self.day_name = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
        self.month_name = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
        self.now = timezone.now()

    def get_month(self):
        return self.month_name[self.month-1]

    def get_days(self):
        weeks = self.monthdays2calendar(self.year, self.month)
        days = []
        for week in weeks:
            for day, _ in week:
                if day == 0:
                    days.append('')
                else:
                    new_day = Day(day, self.check_past(day))
                    days.append(new_day)
        return days

    def check_past(self, day):
        if self.year-self.now.year > 0 or self.month-self.now.month > 0 or day-self.now.day >= 0:
            return False
        else:
            return True

if __name__ == '__main__':
    new_cal = Calendar(2020, 3)
    new_cal.get_days()