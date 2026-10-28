import re


def replace_dates(str_input: str) -> str:
    """Replace each YYYY-MM-DD date in the input with 2025-03-17."""
    return re.sub(r"\d{4}-\d{2}-\d{2}", "2025-03-17", str_input)


if __name__ == "__main__":
    str_input = "1234562025-02-01ABDCTESFD2024-03-02432432e34532025-03-041234-11043"
    print(replace_dates(str_input))