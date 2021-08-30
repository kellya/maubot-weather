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

pylint:
	pylint weather.py

release: build
	#Figure out what the last/most recent build is
	$(eval LATEST = $(shell ls -t1 ${BUILDDIR}/*|head -n1))
	$(eval TAG = $(shell git describe --tags --abbrev=0))
	@echo "Sending $(TAG) to github"
	${GH} release create -F CHANGELOG.md $(TAG) $(LATEST)

.PHONY: dir clean release build pylint
