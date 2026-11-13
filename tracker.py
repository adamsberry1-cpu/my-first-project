"""Print a greeting and the number of days left until the end of the year."""

from datetime import date


def days_until_end_of_year(today: date) -> int:
    """Return the number of days from today until December 31 of the same year."""
    end_of_year = date(today.year, 12, 31)
    return (end_of_year - today).days


def main() -> None:
    today = date.today()
    print("Hello! Welcome to the year tracker.")
    days_left = days_until_end_of_year(today)
    day_word = "day" if days_left == 1 else "days"
    print(f"Today is {today:%B %d, %Y}.")
    print(f"There are {days_left} {day_word} left until the end of {today.year}.")


if __name__ == "__main__":
    main()
