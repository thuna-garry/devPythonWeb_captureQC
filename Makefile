APP=capture
APPQC=${APP}QC
TMP=/tmp/buildout
BLD=${TMP}/${APP}QC
PYTHON=/cygdrive/c/Python27/python.exe

default: dist

version:
	PYTHONPATH="c:\\dev\\aqc" $(PYTHON) root/config.py -version

compileAll:
	$(PYTHON) -m compileall -f -q .
	$(MAKE) -C ${APP}/db
	$(MAKE) -C ${APP}/static

dist: compileAll
	#------------------------------------------------
	#- removing contents of ${BLD}
	#------------------------------------------------
	rm -rf   ${BLD}*
	mkdir -p ${BLD}
	#
	#
	#------------------------------------------------
	#- copying files into ${BLD}
	#------------------------------------------------
	rsync -a /cygdrive/c/dev/web/${APPQC}  ${TMP}
	rsync -a /cygdrive/c/dev/aqc/aqclib    ${BLD}
	chmod -R u+rwx ${BLD}
	#
	#
	#------------------------------------------------
	#- creating version file
	#------------------------------------------------
	cd ${BLD}; \
		PYTHONPATH="." ${PYTHON} root/config.py -version
	#
	#
	#------------------------------------------------
	#- collect static files
	#------------------------------------------------
	cd ${BLD}; \
		${PYTHON} manage.py  collectstatic  <<< "yes"
	#
	#
	#------------------------------------------------
	#- create the distribution database
	#------------------------------------------------
	mv -f ${BLD}/root/db.sqlite3 ${BLD}/root/db.dist.sqlite3
	#
	#
	#------------------------------------------------
	#- remove un-needed files/directories
	#------------------------------------------------
	find ${BLD} -type d -name '.idea'  -print | while read f; do echo deleting $$f; rm -rf $$f; done
	find ${BLD} -type d -name 'static' -print | while read f; do echo deleting $$f; rm -rf $$f; done
	#
	find ${BLD} -type f -name 'Makefile'   -print | while read f; do echo deleting $$f; rm -rf $$f; done
	#
	rm -rf ${BLD}/${APP}/db/templates
	rm -rf ${BLD}/${APP}/db/templates/wrapPackage.sh
	#
	#
	#------------------------------------------------
	#- remove all non-distributable .py files
	#------------------------------------------------
	find ${BLD} -name '*.py' | \
	    while read fname; do \
	        echo checking $$fname ;  \
	        echo $$fname | grep -q "^${BLD}/root/wsgi.py"       && continue ;  \
	        echo $$fname | grep -q "^${BLD}/${APP}/migrations/" && continue ;  \
	        echo "    deleting" ;  \
	        rm -f $$fname ;  \
	    done
	#
	#
	#------------------------------------------------
	#- package up
	#------------------------------------------------
	tar czf ${BLD}_`date +%Y-%m-%d`.tgz -C /tmp/buildout ${APPQC}
	#
	#
	#------------------------------------------------
	#- distribute
	#------------------------------------------------
	@echo rsync -v --progress ${BLD}_`date +%Y-%m-%d`.tgz root@${APPQC}.advanceQC.com:/var/webSites/${APPQC}.advanceQC.com
	@echo rsync -v --progress ${BLD}_`date +%Y-%m-%d`.tgz root@${APPQC}.avroTechnik.ca:/var/webSites/${APPQC}.avroTechnik.ca
	#


#fixperms:
#	echo Fixing local file permisssions
#	find /cygdrive/c/dev . -type d              -exec chmod u+rw,+x {} \;
#	find /cygdrive/c/dev . -type f -name '*.sh' -exec chmod +x      {} \;

