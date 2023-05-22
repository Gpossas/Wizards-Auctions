def currency_format_to_int(price: str) -> int:
    """
    transform a string in currency format to int value. A ValueError is raised if string is entirely non-numeric
    """
    # edge-cases: price = '' -> 0; price = '-1' -> 1; price = 'fgh' -> raise ValueError; 

    value = ''
    for char in price:
        if '0' <= char <= '9': 
            value = ''.join((value, char))
    if value: 
        return int(value) 
    else: 
        raise ValueError('argument entirely non-numeric')


def format_to_price(num: str | int) -> str:
    """
    format a num to price format\n
    Examples: 
        '89' -> $ 0.89 \n
        '758954' -> $ 7,589.54\n
        'only_chars' -> $ 0.00
    """

    num = remove_left_zeroes_and_non_numeric_chars(num)
    num = put_cents(num)
    num = put_comma_every_three_digits(num)
      
    return num

def remove_left_zeroes_and_non_numeric_chars(num) -> str:
    """
    if the string only contains non-numeric chars, don't raise an error, return 0 instead
    """
    if isinstance(num, int):
        return str(num)

    cleaned = ''
    first_digit_found = False
    for char in num:
        if not first_digit_found and '1' <= char <= '9': 
            first_digit_found = True
        if first_digit_found and '0' <= char <= '9': 
            cleaned = ''.join((cleaned, char))
    return cleaned or '0'

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

# print(format_to_price('123456789000'))
print(currency_format_to_int('a'))
# print(int('ascas'))