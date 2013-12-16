# -*- coding:utf-8 -*-
from StringIO import StringIO
import sys
import re
from collections import namedtuple
from xml.sax import ContentHandler
from lxml.sax import ElementTreeContentHandler, saxify
from lxml import etree
from altair.svg.constants import SVG_NAMESPACE

import logging
logger = logging.getLogger(__name__)

"""
raw svg data -> cleaned svg data -> elminated needless tags svg data
"""


## tokenizer
Start = namedtuple("S", "val qname attrs")
End = namedtuple("E", "val qname")
LBrace = namedtuple("L", "val")
RBrace = namedtuple("R", "val")
Content = namedtuple("C", "val")

white_rx = re.compile(r"^[ \n]*$", re.M)
def lbrace(scanner, x):
    return LBrace(x)
def rbrace(scanner, x):
    return RBrace(x)
def content(scanner, x):
    return Content(x)

scanner = re.Scanner([
        (r"\{", lbrace),
        (r"\}", rbrace),
        (r"[^{}]+", content)], 
                     re.M)

def tokens_from_string(string, scanner=scanner):
    return scanner.scan(string)[0]

## state 
def on_external(helper, tokens):
    while tokens:
        token = tokens.pop(0)
        if isinstance(token, LBrace):
            helper.make_stack()#xxx:
            helper.content[-1].append(token)        
            return after_first_lbrace(helper, tokens)
        else:
            helper.heads[-1].append(token)        
    return on_external

def after_first_lbrace(helper, tokens):
    while tokens:
        token = tokens.pop(0)
        if isinstance(token, LBrace):
            helper.content[-1].append(token)
            return after_second_lbrace(helper, tokens)
        elif isinstance(token, RBrace):
            helper.merge_stack()
            helper.heads[-1].append(token)
            return on_external(helper, tokens)
        else:
            helper.content[-1].append(token)
    return after_first_lbrace

def after_second_lbrace(helper, tokens):
    while tokens:
        token = tokens.pop(0)
        helper.content[-1].append(token)
        if isinstance(token, LBrace):
            return in_place_holder(helper, tokens, level=1)
        elif isinstance(token, RBrace):
            return after_first_rbrace(helper, tokens)
        else:
            return in_place_holder(helper, tokens, level=0)
    return after_second_lbrace

def in_place_holder(helper, tokens, level=0):
    while tokens:
        token = tokens.pop(0)
        helper.content[-1].append(token)
        if isinstance(token, RBrace):
            return after_first_rbrace(helper, tokens)
    return in_place_holder

def after_first_rbrace(helper, tokens):
    while tokens:
        token = tokens.pop(0)
        # if isinstance(token, LBrace):
        #     raise Exception("Invalid input %s" % token)
        helper.content[-1].append(token)
        if isinstance(token, RBrace):
            return after_second_rbrace(helper, tokens)
    return after_first_rbrace

def after_second_rbrace(helper, tokens):
    while tokens:
        token = tokens.pop(0)
        if isinstance(token, LBrace):
            helper.make_stack()#xxx:
            helper.content[-1].append(token)            
            return after_first_lbrace(helper, tokens)
        else:
            helper.tails[-1].append(token)            
    return after_second_rbrace

class StateHandleHelper(object):
    def __init__(self, state=on_external):
        self.state = state
        self.content = [[]]
        self.heads = [[]]
        self.tails = [[]]
        self.body = []

    def make_stack(self):
        self.content.append([])
        self.heads.append([])
        self.tails.append([])

    def merge_stack(self):
        # self.display()
        self.heads[-1].extend(self.content.pop())
        self.content.append([])
        # self.display()

    def display(self):
        print "heads:%s" % self.heads
        print "content:%s" % self.content
        print "tails:%s" % self.tails
        print "----------------------------------------"

font_family_rx = re.compile("font-family ?: *?([^;]+;?)")
class ConvertXmlForTicketTemplateAttrsHook(object):
    @classmethod
    def startElementNS(cls, name, qname, attrs):
        if name[0] == SVG_NAMESPACE and name[1] == "svg":
            attrs._attrs[(None, "version")] = "1.2"
        return attrs._attrs

class ConvertXmlForTicketTemplateRenderingFilter(ContentHandler):
    def __init__(self, eliminate=False, attrs_hook=ConvertXmlForTicketTemplateAttrsHook):
        self._downstream = ElementTreeContentHandler()
        self.sm = StateHandleHelper()
        self.eliminate = eliminate
        self.attrs_hook  = attrs_hook

    @property
    def result(self):
        return self._downstream.etree

    def startDocument(self):
        self._downstream.startDocument()

    def startElementNS(self, name, qname, attrs):
        # todo: refactoring
        attrs = self.attrs_hook.startElementNS(name, qname, attrs)
        state = self.sm.state
        if state == on_external:
            self.sm.heads[-1].append(Start(name, qname, attrs))
        elif state == after_first_lbrace:
            self.sm.heads[-1].append(Start(name, qname, attrs))
        elif state == after_second_lbrace:
            self.sm.heads[-1].append(Start(name, qname, attrs))
        elif state == in_place_holder:
            self.sm.heads[-1].append(Start(name, qname, attrs))
            #peek last then tails << stag
        elif state == after_first_rbrace:
            self.sm.tails[-1].append(Start(name, qname, attrs))
        elif state == after_second_rbrace:
            self.sm.tails[-1].append(Start(name, qname, attrs))
            ## consume?
        else:
            raise Exception("invalid state")

    def endElementNS(self, name, qname):
        state = self.sm.state
        if state == on_external:
            self.sm.heads[-1].append(End(name, qname))
        elif state == after_first_lbrace:
            self.sm.heads[-1].append(End(name, qname))
        elif state == after_second_lbrace:
            self.sm.heads[-1].append(End(name, qname))
        elif state == in_place_holder:
            self.sm.tails[-1].append(End(name, qname))
        elif state == after_first_rbrace:
            self.sm.tails[-1].append(End(name, qname))
        elif state == after_second_rbrace:
            self.sm.tails[-1].append(End(name, qname))
        else:
            raise Exception("invalid state")

    def characters(self, content):
        tokens = tokens_from_string(content)
        self.sm.state = self.sm.state(self.sm, tokens)
        
    def endDocument(self):
        sm = self.sm
        downstream = self._downstream
        if self.eliminate:
            _eliminated_dump_to_downstream(sm, downstream)
        else:
            _simple_dump_to_downstream(sm, downstream)
        self._downstream.endDocument()

    def __call__(self, tree):
        saxify(tree, self)

class DocumentAlreadyEnd(Exception):
    pass

def _simple_dump_to_downstream(sm, downstream):
    # print "**end**"
    # sm.display()
    if not sm.heads or not sm.heads[0]:
        return
    fst = sm.heads[0][0].val
    fst_cnt = 0
    try:
        for i in xrange(len(sm.heads)):
            for xs in (sm.heads[i], sm.content[i], sm.tails[i]):
                for x in xs:
                    if isinstance(x, Start):
                        downstream.startElementNS(x.val, x.qname, x.attrs)
                    elif isinstance(x, End):
                        downstream.endElementNS(x.val, x.qname)
                    else:
                        downstream.characters(x.val)
                    if x.val == fst:
                        fst_cnt += 1
                        if fst_cnt>1:
                            raise DocumentAlreadyEnd(x.val)
    except DocumentAlreadyEnd:
        ## todo: useful message.
        logger.info("reach. end document element")


def _eliminated_dump_to_downstream(sm, downstream):
    prev = None
    if not sm.heads or not sm.heads[0]:
        return
    fst = sm.heads[0][0].val
    fst_cnt = 0
    try:
        for i in xrange(len(sm.heads)):
            for xs in (sm.heads[i], sm.content[i], sm.tails[i]):
                for x in xs:
                    if isinstance(x, (Start, End)) and type(prev) == type(x) and prev.val == x.val:
                        continue
                    if isinstance(x, Start):
                        downstream.startElementNS(x.val, x.qname, x.attrs)
                        prev = x
                    elif isinstance(x, End):
                        downstream.endElementNS(x.val, x.qname)
                        prev = x
                    else:
                        downstream.characters(x.val)
                    if x.val == fst:
                        fst_cnt += 1
                        if fst_cnt>1:
                            raise DocumentAlreadyEnd(x.val)
    except DocumentAlreadyEnd:
        ## todo: useful message.
        logger.info("reach. end document element")

def normalize(inp, outp=sys.stdout, encoding="UTF-8", header="", eliminate=False):
    return _normalize(inp, outp, encoding, eliminate=eliminate)

def _normalize(inp, outp=sys.stdout, encoding="UTF-8", eliminate=False):
    outp.write(etree.tostring(normalize_etree(etree.parse(inp), eliminate), encoding=encoding))

def normalize_etree(tree, eliminate=False):
    attrs_hook = ConvertXmlForTicketTemplateAttrsHook
    filter_handler = ConvertXmlForTicketTemplateRenderingFilter(
        eliminate=eliminate, attrs_hook=attrs_hook
        )
    filter_handler(tree)
    return filter_handler.result


if __name__ == "__main__":
    import sys
    with open(sys.argv[1]) as rf:
        with open(sys.argv[2], "w") as wf:
            normalize(rf, wf, encoding="utf-8", eliminate=True)
