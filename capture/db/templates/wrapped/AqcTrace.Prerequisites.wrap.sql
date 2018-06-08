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


