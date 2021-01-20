BUILDDIR=build
dir: 
	[ -d $(BUILDDIR) ] || mkdir -p $(BUILDDIR)
build: dir
	mbc build -o build/
clean:
	rm -rf $(BUILDDIR)
.PHONY: dir clean
