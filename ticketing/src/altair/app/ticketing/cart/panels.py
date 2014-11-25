def input_form(context, request, form):
    return {"form": form}

def complete_notice(context, request, is_show_order_review=True):
    return {"is_show_order_review": is_show_order_review}
