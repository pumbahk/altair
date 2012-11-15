# -*- coding:utf-8 -*-
import sys
import re
from collections import namedtuple
import xml.sax
from xml.sax.saxutils import XMLFilterBase, XMLGenerator

"""
raw svg data -> cleaned svg data -> elminated needless tags svg data
"""


## tokenizer
Start = namedtuple("S", "val attrs")
End = namedtuple("E", "val")
LBrace = namedtuple("L", "val")
RBrace = namedtuple("R", "val")
Content = namedtuple("C", "val")

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
            helper.content[-1].append(token)
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
        if isinstance(token, LBrace):
            level += 1
        elif isinstance(token, RBrace):
            if level <= 0:
                return after_first_rbrace(helper, tokens)
            level -= 1
    return in_place_holder

def after_first_rbrace(helper, tokens):
    while tokens:
        token = tokens.pop(0)
        if isinstance(token, LBrace):
            raise Exception("Invalid input")
        helper.content[-1].append(token)
        if isinstance(token, RBrace):
            return after_second_rbrace(helper, tokens)
    return after_first_rbrace

def after_second_rbrace(helper, tokens):
    while tokens:
        token = tokens.pop(0)
        if isinstance(token, RBrace):
            raise Exception("Invalid input")

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
        c = self.content.pop()
        self.content[-1].extend(c)
        h = self.heads.pop()
        self.heads[-1].extend(h)
        t = self.tails.pop()
        self.tails[-1].extend(t)

    def consume(self):
        ## 試しに
        pass
        # print self.heads, self.content, self.tails

class ConvertXmlForTicketTemplateRenderingFilter(XMLFilterBase):
    def __init__(self, upstream, downstream, eliminate=False):
        XMLFilterBase.__init__(self, upstream)
        self._downstream = downstream
        self.sm = StateHandleHelper()
        self.eliminate = eliminate

    def startDocument(self):
        pass

    def startElement(self, name, attrs):
        state = self.sm.state
        if state == on_external:
            self.sm.heads[-1].append(Start(name, attrs))
        elif state == after_first_lbrace:
            self.sm.heads[-1].append(Start(name, attrs))
        elif state == after_second_lbrace:
            self.sm.heads[-1].append(Start(name, attrs))
        elif state == in_place_holder:
            self.sm.heads[-1].append(Start(name, attrs))
            #peek last then tails << stag
        elif state == after_first_rbrace:
            self.sm.tails[-1].append(Start(name, attrs))
        elif state == after_second_rbrace:
            self.sm.tails[-1].append(Start(name, attrs))
            ## consume?
        else:
            raise Exception("invalid state")

    def endElement(self, name):
        state = self.sm.state
        if state == on_external:
            self.sm.heads[-1].append(End(name))
        elif state == after_first_lbrace:
            self.sm.heads[-1].append(End(name))
        elif state == after_second_lbrace:
            self.sm.heads[-1].append(End(name))
        elif state == in_place_holder:
            self.sm.tails[-1].append(End(name))
        elif state == after_first_rbrace:
            self.sm.tails[-1].append(End(name))
        elif state == after_second_rbrace:
            self.sm.tails[-1].append(End(name))
        else:
            raise Exception("invalid state")

    def characters(self, content):
        tokens = tokens_from_string(content)
        self.sm.state = self.sm.state(self.sm, tokens)
        
    def endDocument(self):
        sm = self.sm
        downstream = self._downstream
        if self.eliminate:
            return _eliminated_dump_to_downstream(sm, downstream)
        else:
            return _simple_dump_to_downstream(sm, downstream)


def _simple_dump_to_downstream(sm, downstream):
    for i in xrange(len(sm.heads)):
        for xs in (sm.heads[i], sm.content[i], sm.tails[i]):
            for x in xs:
                if isinstance(x, Start):
                    downstream.startElement(x.val, x.attrs)
                elif isinstance(x, End):
                    downstream.endElement(x.val)
                else:
                    downstream.characters(x.val)

def _eliminated_dump_to_downstream(sm, downstream):
    prev = None
    for i in xrange(len(sm.heads)):
        for xs in (sm.heads[i], sm.content[i], sm.tails[i]):
            for x in xs:
                if type(prev) == type(x) and prev.val == x.val:
                    continue
                if isinstance(x, Start):
                    downstream.startElement(x.val, x.attrs)
                elif isinstance(x, End):
                    downstream.endElement(x.val)
                else:
                    downstream.characters(x.val)
                prev = x

    
def _attach_header(inp, outp):
    while True:
        pos = inp.tell()
        line = inp.readline()
        if line.startswith("<?xml") or line.startswith("<!--"):
            outp.write(line)
        else:
            inp.seek(pos)
            break

def normalize(inp, outp=sys.stdout, encoding="UTF-8", header="", eliminate=True):
    _attach_header(inp, outp)
    return _normalize(inp, outp, encoding, eliminate=True)

def _normalize(inp, outp=sys.stdout, encoding="UTF-8", eliminate=False):
    downstream_handler = XMLGenerator(outp, encoding.lower())
    parser = xml.sax.make_parser()
    filter_handler = ConvertXmlForTicketTemplateRenderingFilter(parser, downstream_handler, eliminate=eliminate)
    filter_handler.parse(inp)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        with open(sys.argv[1]) as rf:
            with open(sys.argv[2], "w") as wf:
                normalize(rf, wf, encoding="utf-8")
