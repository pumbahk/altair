from .interfaces import IPageFlowPredicate, IPageFlowPredicateUnaryOp, IPageFlowAction
from zope.interface import implementer

def get_route_name(request):
        return getattr(getattr(request, 'matched_route', None), 'name', None)

@implementer(IPageFlowPredicate)
class RouteIs(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '(route_name == %s)' % self.name

    def __call__(self, pe, flow_context, context, request):
        return get_route_name(request) == self.name

@implementer(IPageFlowPredicateUnaryOp)
class Not(object):
    def __init__(self, predicate):
        self.predicate = predicate

    def __str__(self):
        return '!%s' % self.predicate

    def __call__(self, pe, flow_context, context, request):
        return not pe(self.predicate, flow_context, context, request)

class PageFlowActionBase(object):
    def __init__(self, predicates):
        self.predicates = predicates

class Transition(object):
    def __init__(self, context, request, route_args=None, url_or_path=None):
        if route_args is None and url_or_path is None:
            raise TypeError('either route_args or url_or_path can be none')
        self.context = context
        self.request = request
        self.route_args = route_args
        self.url_or_path = url_or_path

    def __call__(self, url_wanted=False):
        if self.url_or_path:
            return self.url_or_path
        else:
            if url_wanted:
                return self.request.route_url(**self.route_args)
            else:
                return self.request.route_path(**self.route_args)
        

@implementer(IPageFlowAction)
class SimpleTransitionAction(PageFlowActionBase):
    def __init__(self, predicates, route_name, **kwargs):
        super(SimpleTransitionAction, self).__init__(predicates)
        self.args = dict(route_name=route_name, **kwargs)

    def __call__(self, flow_context, context, request):
        return Transition(context, request, route_args=self.args)

    def __str__(self):
        return '(%s) => %r' % (', '.join(self.predicates), self.args)

class MultipleFlowActionFound(Exception):
    pass

class UnsupportedPageFlow(Exception):
    pass

class PredicateEvaluator(object):
    def __init__(self):
        self.results = {}

    def __call__(self, predicate, flow_context, context, request):
        result = self.results.get(predicate)
        if result is None:
            self.results[predicate] = result = predicate(self, flow_context, context, request)
        return result

class PageFlowGraph(object):
    def __init__(self, flow_context_factory, actions):
        self.flow_context_factory = flow_context_factory
        route_bound_actions = {}
        non_route_bound_actions = []
        for action in actions:
            route_bound = False
            for predicate in action.predicates:
                if isinstance(predicate, RouteIs):
                    route_bound_actions.setdefault(predicate.name, []).append(action)
                    route_bound = True
            if not route_bound:
                non_route_bound_actions.append(action)
        self.route_bound_actions = route_bound_actions
        self.non_route_bound_actions = non_route_bound_actions

    def __call__(self, context, request):
        flow_context = self.flow_context_factory(context, request)

        while True:
            candidates = []
            pe = PredicateEvaluator()
            route_name = get_route_name(request)
            if route_name is not None:
                actions = self.route_bound_actions.get(route_name)
                for _action in actions:
                    if all(pe(predicate, flow_context, context, request) for predicate in _action.predicates):
                        candidates.append(_action)

            if len(candidates) == 0:
                for _action in self.non_route_bound_actions:
                    if all(pe(predicate, flow_context, context, request) for predicate in _action.predicates):
                        candidates.append(_action)

            if len(candidates) > 1:
                raise MultipleFlowActionFound(candidates)
            elif len(candidates) == 0:
                return None

            action = candidates[0]
            r = action(flow_context, context, request)
            if r is not None:
                return r
