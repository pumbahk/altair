HAXE = haxe
BUILDDIR = ../build
COMPILED_JS = $(BUILDDIR)/out.js

$(COMPILED_JS): *.hx rendering/js/dom/*.hx
	$(HAXE) -js $@ $^

clean:
	rm -f $(COMPILED_JS)

.PHONY: clean
