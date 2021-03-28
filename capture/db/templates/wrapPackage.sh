#! /bin/sh

DDL_PATH=$1
PY_PATH=$2

script_1=/tmp/${0##*/}.$$.script_1;  sed -e '1,/[Ee]mbedded script 1/d;/[Ee]mbedded script/,$d;' $0 > $script_1

ddlFile=${DDL_PATH##*/}                    # strip off the leading dir
pyClass=${ddlFile#pkg}                     # strip off leading 'pkg'
pyClass=${pyClass%.ddl}                    # strip off trailing '.ddl'

DDL_DIR=${DDL_PATH%/*}
mkdir -p ${DDL_DIR}/wrapped                # ensure the wrapped subDir exists

{
    echo 'from dbPackage import *'
    echo
    echo "class ${pyClass}(DbPackage):"
    echo

    sectionFiles=`awk -f $script_1 $DDL_PATH`
    for sqlFile in $sectionFiles; do
        section=${sqlFile##*/}        #strip off leading dir and prefix
        section=${section%.sql}       #strip off suffix
        wrapFile=${DDL_DIR}/wrapped/${pyClass}.${section}.wrap.sql
        wrap iname=`cygpath -w ${sqlFile}` oname=`cygpath -w ${wrapFile}`  > /dev/null
        sed -i -e 's/\s*$//' ${wrapFile}   #remove any trailing whitespace within the wrapped file
        echo "    _pkg${section} = \"\"\"$(sed -e '$d' $wrapFile | base64 -w 0)\"\"\" "
    done
    echo
} > $PY_PATH


rm -f $script_1


#######################################################################################
# embedded seripts
#######################################################################################
exit

#-- embedded script 1 -------------------------------------------------------------------

# for each item start a separate temporary output file
/^--_pkg/ { object = substr($0, 7);
            outFile = "/tmp/" object ".sql"
            print outFile
            printf "" > outFile
          }

# write each line
          { if ( length(object) > 0 ) {
               print $0 >> outFile
            }
          }

# blank line ends the item
/^$/      { if ( length(object) > 0 ) {
                object = "" ;
            }
          }


