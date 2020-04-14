(function() {
    PayVault.setAttachToken(true);
    var CARD_HOLDER_REGEXP = '^[A-Z\\s]+$';
    var CVV_REGEXP = '^\\d{3,4}$';

    function clearErrorMsgs() {
        $('span.error-message').empty();
    }

    function scrollToHead() {
        $('html, body').animate({scrollTop:0});
    }

    function isUseLatestCard() {
        var radioBtnUseLatestCardElm = $('#radioBtnUseLatestCard');
        return radioBtnUseLatestCardElm.length > 0 && radioBtnUseLatestCardElm.prop('checked');
    }

    function isUseNewCard() {
        var radioBtnUseNewCardElm = $('#radioBtnUseNewCard');
        return radioBtnUseNewCardElm.length === 0 || radioBtnUseNewCardElm.prop('checked');
    }

    function validateForm() {
        if (isUseLatestCard() === isUseNewCard()) {
            $('#radioBtnUseLatestCardError').text(i18nMsgs['unselected']);
            $('#radioBtnUseNewCardError').text(i18nMsgs['unselected']);
            return false;
        }

        if (isUseLatestCard()) {
            return _validateToUseLatestCard();
        } else {
            return _validateToUseNewCard();
        }
    }

    function _validateToUseLatestCard() {
        var result = true;
        var cvvUseLatestCard = $('#cvvUseLatestCard').val();

        if (cvvUseLatestCard.length === 0) {
            $('#cvvUseLatestCardError').text(i18nMsgs['required']);
            result = false;
        } else if (!cvvUseLatestCard.match(CVV_REGEXP)) {
            $('#cvvUseLatestCardError').text(i18nMsgs['invalid_cvv']);
            result = false;
        }

        return result;
    }

    function _validateToUseNewCard() {
        var result = true;
        var cardNumber = $('#cardNumber').val();
        var expirationMonth = $('#expirationMonth').val();
        var expirationYear = $('#expirationYear').val();
        var cardHolderName = $('#cardHolderName').val();
        var cvvUseNewCard = $('#cvvUseNewCard').val();


        if (cardNumber.length === 0) {
            $('#cardNumberError').text(i18nMsgs['required']);
            result = false;
        } else if (!PayVault.card.validateCardNumber(cardNumber)) {
            $('#cardNumberError').text(i18nMsgs['invalid_card_number']);
            result = false;
        }

        if (expirationMonth.length === 0 || expirationYear.length === 0) {
            $('#expirationError').text(i18nMsgs['required']);
            result = false;
        } else if (!PayVault.card.validateExpiration(expirationMonth, expirationYear)) {
            $('#expirationError').text(i18nMsgs['invalid_expiration']);
            result = false;
        }

        if (cardHolderName.length === 0) {
            $('#cardHolderNameError').text(i18nMsgs['required']);
            result = false;
        }else if (cardHolderName.length > 100)  {
            $('#cardHolderNameError').text(i18nMsgs['invalid_card_holder_name_length']);
            return false;
        } else if (!cardHolderName.match(CARD_HOLDER_REGEXP)) {
            $('#cardHolderNameError').text(i18nMsgs['invalid_card_holder_name']);
            result = false;
        }

        if (cvvUseNewCard.length === 0) {
            $('#cvvUseNewCardError').text(i18nMsgs['required']);
            result = false;
        } else if (!cvvUseNewCard.match(CVV_REGEXP)) {
            $('#cvvUseNewCardError').text(i18nMsgs['invalid_cvv']);
            result = false;
        }

        return result;
    }

    function payVaultResponseHandler(status, response) {
        var formElm = $('#cardForm');

        if (response.resultType === 'failure') {
            formElm.append($('<input>').attr({
                'type': 'hidden',
                'name': 'errorCode',
                'value': response.errorCode
            }));
            formElm.append($('<input>').attr({
                'type': 'hidden',
                'name': 'errorMessage',
                'value': response.errorMessage
            }));
        }

        formElm.get(0).submit();
    }

    $(function($) {
        $('#cardForm').submit(function() {
            clearErrorMsgs();

            if (validateForm()) {
                $('#cardForm').find('button').prop('disabled', true);

                if (isUseLatestCard()) {
                    PayVault.card.createToken({
                        'form': $('#cardForm'),
                        'cvv': $('#cvvUseLatestCard')
                    }, payVaultResponseHandler);
                } else {
                    PayVault.card.createToken({
                        'form': $('#cardForm'),
                        'card-number': $('#cardNumber'),
                        'expiration-month': $('#expirationMonth'),
                        'expiration-year': $('#expirationYear'),
                        'cvv': $('#cvvUseNewCard')
                    }, payVaultResponseHandler);
                }
            } else {
                scrollToHead();
            }

            return false;
        });
    });
})();