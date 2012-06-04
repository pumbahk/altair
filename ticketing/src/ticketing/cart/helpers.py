from webhelpers.number import format_number as _format_number

def format_number(num, thousands=","):
    return _format_number(int(num), thousands)
