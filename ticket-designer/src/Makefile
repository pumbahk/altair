HAXE = haxe
BUILDDIR = ../build
COMPILED_JS = $(BUILDDIR)/out.js
OPTS = -D noEmbedJS

$(COMPILED_JS): *.hx rendering/js/dom/*.hx
	$(HAXE) $(OPTS) -js $@ $^

clean:
	rm -f $(COMPILED_JS)

.PHONY: clean
