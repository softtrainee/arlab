def add_sub_error_prop(errors):
    error = reduce(lambda a, b: (a ** 2 + b ** 2) ** 0.5, errors)
    return error
def mult_div_error_prop(values, errors):
    error = reduce(lambda a, b:((a[1] / a[0]) ** 2 + (b[1] / b[0]) ** 2) ** 0.5 , zip(values, errors))
    return error
