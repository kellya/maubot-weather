# Set output dir
BUILDDIR=build

#GH/github command used to initiate a release
GH=/usr/bin/gh

build: dir
	mbc build -o build/

dir: 
	[ -d $(BUILDDIR) ] || mkdir -p $(BUILDDIR)


clean:
	rm -rf $(BUILDDIR)

release: build
	#Figure out what the last/most recent build is
	$(eval LATEST = $(shell ls -t1 ${BUILDDIR}/*|head -n1))
	@echo "Sending $(LATEST) to github"
	${GH} release create  $(LATEST)

.PHONY: dir clean release

