HAXE = haxe
BUILDDIR = ../build
COMPILED_JS = $(BUILDDIR)/out.js
OPTS = -D noEmbedJS

$(COMPILED_JS): *.hx fashion/*.hx model/*.hx render/*.hx render/impl/*.hx
	$(HAXE) $(OPTS) -js $@ $^

clean:
	rm -f $(COMPILED_JS)

.PHONY: clean
