class @TextComponent extends @Component
    @events 'click', 'dblclick'

    constructor: ->
        super $('<div class="component-text"></div>')
        self = this
        @n.bind 'click', (e) -> self.on.click.call self, e
        @text_ = ''

    refresh: ->
        @n.text @text_

    text: (value) ->
        if typeof value == 'undefined'
            @text_
        else
            @text_ = value

    
