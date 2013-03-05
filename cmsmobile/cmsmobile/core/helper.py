def exist_value(value):

    if value is None:
        return False

    if value == "":
        return False

    if value == "0":
        return False

    return True