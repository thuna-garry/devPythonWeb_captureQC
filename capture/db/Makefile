
ddlFiles = $(wildcard templates/pkg*.ddl)
pyFiles = $(patsubst %.ddl, %.py, $(notdir $(ddlFiles)))

all dist: $(pyFiles)

$(pyFiles): %.py : templates/%.ddl
	dos2unix $<
	templates/wrapPackage.sh  $<  $@

clean:
	rm -f $(pyFiles)
	rm -f templates/*.~ddl
	rm -f templates/wrapped/*.sql