def input_form(context, request, form, products):
    return {"form": form, "products": products}

def review_additional_messages(context, request, pm):
    return {"pm": pm}
