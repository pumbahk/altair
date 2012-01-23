HAXE = haxe
BUILDDIR = ../build
COMPILED_JS = $(BUILDDIR)/out.js

$(COMPILED_JS): *.hx
	$(HAXE) -js $@ $^

clean:
	rm -f $(COMPILED_JS)

.PHONY: clean
