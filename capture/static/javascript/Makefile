#jsFiles:  $(patsubst %.js,%.min.js,$(shell ls *.js 2>/dev/null| grep -v min.js))
#	echo done.
#
#cssFiles: $(patsubst %.css,%.min.css,$(shell ls *.css 2>/dev/null | grep -v min.css))
#	echo done.
#
#%.min.js: %.js
#	curl -X POST -s --data-urlencode input@$< http://javascript-minifier.com/raw > $@
#
#%.min.css: %.css
#	curl -X POST -s --data-urlencode input@$< http://cssminifier.com/raw > $@


capture.min.js: $(shell ls *.js 2>/dev/null | grep -v min.js)
	# npm install -g uglify-js
	# npm install -g uglifycss
	uglifyjs $^   \
	    -o $@  \
	    --comments 'copyright'  \
	    --source-map ${@}.map \
	    -c sequences,properties,dead_code,evaluate,join_vars,drop_console \
	    -m  \
	    --screw-ie8

clean:
	rm -f *.min.js
	rm -f *.map

