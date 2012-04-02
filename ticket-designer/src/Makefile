HAXE = haxe
BUILDDIR = ../build
COMPILED_JS = $(BUILDDIR)/out.js
OPTS = -D noEmbedJS

$(COMPILED_JS): *.hx models/*.hx views/*.hx views/rendering/js/dom/*.hx
	$(HAXE) $(OPTS) -js $@ $^

clean:
	rm -f $(COMPILED_JS)

.PHONY: clean
