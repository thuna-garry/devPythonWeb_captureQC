#https://blogs.oracle.com/opal/entry/python_cx_oracle_and_oracle

import os
import time
import cx_Oracle

# drcp3.py
# Example: Connection pooling with Oracle 11g DRCP and cx_Oracle

def do_connection():
    print 'Starting do_connection ' + str(os.getpid())
    mypool = cx_Oracle.SessionPool(user=user,password=pw,dsn=dsn,min=1,max=2,increment=1)
    con = cx_Oracle.connect(user=user, password=pw,
          dsn=dsn, pool = mypool, cclass="CJDEMO3", purity=cx_Oracle.ATTR_PURITY_SELF)
    cur = con.cursor()
    print 'Querying ' + str(os.getpid())
    cur.execute("select to_char(systimestamp) from dual")
    print cur.fetchall()
    cur.close()
    mypool.release(con)
    print 'Sleeping ' + str(os.getpid())
    #time.sleep(30)
    print 'Finishing do_connection ' + str(os.getpid())

#con = cx_Oracle.connect('aqcTest/quantum@10.0.100.11/cctl')
#con = cx_Oracle.connect('aqcTest', 'quantum', '10.0.100.11/cctl:pooled', cclass = "SYS_DEFAULT_CONNECTION_POOL", purity = cx_Oracle.ATTR_PURITY_SELF)

user = 'aqcTest'
pw = 'quantum'
dsn = 'avrotechnik'
for x in range(100):
 #   pid = os.fork()
 #   if not pid:
        do_connection()
 #       os._exit(0)


