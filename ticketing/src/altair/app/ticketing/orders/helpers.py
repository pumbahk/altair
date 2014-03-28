def build_candidate_id(token, seat, ordered_product_item, ticket):
    #token.id@seat@ordered_product_item.id@ticket.id
    return unicode(token.id if token else None) + u"@" + unicode(seat.id if seat else None) + u"@" + unicode(ordered_product_item.id) + u"@" + unicode(ticket.id)

def decode_candidate_id(candidate_id):
    #token@seat@ordered_product_item.id@ticket.id
    return tuple((None if e == "None" else unicode(e)) for e in candidate_id.split("@"))
