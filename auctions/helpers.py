class ListingNotActive(Exception):
    pass
class BidTooLow(Exception):
    pass


def trim_non_numeric_and_cast_int(string: str) -> int:
    """
    remove non-numeric characters and cast string to int value. A ValueError is raised if string is entirely non-numeric\n
    Examples:\n
        '$ 89.45' -> 8945\n
        '0000' -> 0\n
        '45bar64' -> 4564\n
        'foo' -> raise ValueError
    """

    num = ''
    for char in string:
        if '0' <= char <= '9': 
            num = ''.join((num, char))
    if not num: 
        raise ValueError('argument entirely non-numeric')
    return int(num) 


def format_to_currency(num: str | int) -> str:
    """
    format a num to currency format\n
    Examples: 
        '89' -> $ 0.89 \n
        '758954' -> $ 7,589.54\n
        'only_chars' -> $ 0.00
    """

    num = format_string_as_int(num)
    num = put_cents(num)
    num = put_comma_every_three_digits(num)
      
    return num

def format_string_as_int(string: str) -> str:
    """
    remove non-numeric characters and left zeroes\n
    A ValueError is raised if string is entirely non-numeric\n
    Examples:\n
        '$ 89.45' -> 8945\n
        '0000' -> 0\n
        '45bar64' -> 4564\n
        'foo' -> raise ValueError
    """
    if isinstance(string, int):
        return str(string)

    num = ''
    first_digit_found = False
    for char in string:
        if not first_digit_found and '1' <= char <= '9': 
            first_digit_found = True
        if first_digit_found and '0' <= char <= '9': 
            num = ''.join((num, char))
    if not num: 
        raise ValueError('argument entirely non-numeric')
    return num

def put_cents(num: str) -> str:
    digits = len(num)
    match digits:
        case 1:
            num = ''.join(('0.0', num))
        case 2:
            num = ''.join(('0.', num))
        case _:
            num = '.'.join((num[:-2], num[-2::]))
    return num

def put_comma_every_three_digits(num: str) -> str:
    digits, DECIMAL_PLACES, MIN_DIGITS_TO_PUT_COMMA = len(num), 3, 4
    if digits - DECIMAL_PLACES < MIN_DIGITS_TO_PUT_COMMA: return num

    count = 0
    formated_num = ''
    for i in range(digits - DECIMAL_PLACES - 1, -1, -1):
        if count % 3 == 0 and count != 0:
            formated_num = ''.join(('.', formated_num))
        formated_num = ''.join((num[i], formated_num))
        count += 1
    return ''.join((formated_num, num[-DECIMAL_PLACES::]))