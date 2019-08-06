from altair.app.ticketing.cooperation.rakuten_live.utils import has_r_live_session, get_r_live_session, convert_type


def recaptcha_exempt(request):
    """Check if the request can be exempt from reCAPTCHA."""
    if not has_r_live_session(request):
        return False

    matchdict = request.matchdict
    if not matchdict:
        return False

    r_live_session = get_r_live_session(request)

    # The performance id is contained in the cart url path.
    # Check if the ID is same as the counterpart in session
    performance_id = matchdict.get('performance_id')
    if performance_id:
        return r_live_session.performance_id == convert_type(performance_id, int)

    # The lot id is contained in the lottery cart url path.
    # Check if the ID is same as the counterpart in session
    lot_id = matchdict.get('lot_id')
    if lot_id:
        return r_live_session.lot_id == convert_type(lot_id, int)

    return False
