--_pkgPrerequisites
begin
    begin execute immediate 'drop sequence aqcTraceSeq'; exception when others then null; end;
    begin execute immediate 'drop table    aqcTraceMsg'; exception when others then null; end;
    execute immediate 'create sequence aqcTraceSeq nocache';
    execute immediate 'create table aqcTraceMsg ( aqcTraceSeq number not null
                                                , userName varchar2(30) not null
                                                , dateTime varchar2(20) not null
                                                , parm varchar2(2000) not null
                                                , val  varchar2(2000) not null )';
end;


--_pkgHeader
create or replace package aqcTrace is
    TRACE boolean := False;
    --
    procedure setTrace (p_trace boolean);
    procedure setTrace (p_trace number);
    procedure clear;
    procedure msg (p_parm varchar2, p_value varchar2);
end;


--_pkgBody
create or replace package body aqcTrace is
    --
    procedure setTrace (p_trace boolean) is
    begin
        aqcTrace.TRACE := p_trace;
    end;
    --
    procedure setTrace (p_trace number) is
    begin
        aqcTrace.TRACE := case p_trace when 0 then False else True end;
    end;
    --
    --
    procedure clear is
        pragma autonomous_transaction;
    begin
        if TRACE then
            delete from aqcTraceMsg;
            commit;
        end if;
    end;
    --
    --
    procedure msg (p_parm varchar2, p_value varchar2) is
        pragma autonomous_transaction;
    begin
        if TRACE then
            insert into aqcTraceMsg
                       ( aqcTraceSeq,         username, datetime,                                parm,   val      )
                values ( aqcTraceSeq.nextval, user,     to_char(sysdate, 'yyyy-mm-dd_hh24miss'), p_parm, p_value  );
            commit;
        end if;
    end;
end;

