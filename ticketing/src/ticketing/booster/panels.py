def input_form(context, request, form, products):
    return {"form": form, "products": products}

def review_additional_messages(context, request, pm):
    return {"pm": pm}

def complete_notice(context, request, is_show_order_review=True):
    return {"is_show_order_review": is_show_order_review}
