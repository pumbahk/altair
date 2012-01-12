class EventListeners extends Function
    constructor: ->
        @listeners = []

    do: (listener) ->
        @listeners.push listener

    apply: (self, arguments) ->
        exceptions = []
        for listener in @listeners
            try
                listener.apply self, arguments
            catch e
                exceptions.push e
        if exceptions.length
            throw new Exceptions(exceptions)

    call: ->
        @apply [].shift.apply(arguments), arguments
