--_pkgHeader
create or replace package aqcCaptureQC authid definer as
  procedure authUserSession(p_userId varchar2);
end;


--_pkgBody
create or replace package body aqcCaptureQC as
    --
    --
    procedure authUserSession(p_userId varchar2) as
        PRAGMA AUTONOMOUS_TRANSACTION;
        cur         qc_utl_pkg.cursor_type;
        l_user_name sys_users.user_name%type;
        l_pwd       sys_users.pwd%type;
        --
        l_sysur   number;
        l_sid     number;
        l_cid     number;
    begin
        select   user_name,   pwd
          into l_user_name, l_pwd
          from sys_users
         where user_id = p_userId;
        cur := qc_sc_pkg.VALIDATE_PASSWORD(l_user_name, l_pwd);
        --
        fetch cur into l_sysur, l_sid, l_cid;
        aqcTrace.msg('********************', 'aqcCaptureQC.authUserSession');
        aqcTrace.msg('p_userId',  p_userId);
        aqcTrace.msg('l_sysur',   l_sysur);
        commit;
    end;
    --
    --
end;
