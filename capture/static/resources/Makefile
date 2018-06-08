cssFiles: $(patsubst %.css,%.min.css,$(shell ls *.css 2>/dev/null | grep -v min.css))
	echo done.

%.min.css: %.css
	#curl -X POST -s --data-urlencode input@$< http://cssminifier.com/raw > $@
	uglifycss $< > $@

clean:
	rm -f *.min.css

