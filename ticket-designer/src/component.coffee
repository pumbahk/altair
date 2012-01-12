###
hoge
###
class @Component
  @events = -> @_events = arguments
 
  constructor: (@n) ->
    on_ = {}
    for event in @constructor._events
        on_[event] = new EventListeners
    @on = on_
