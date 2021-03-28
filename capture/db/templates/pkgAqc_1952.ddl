--_pkgHeader
create or replace package aqc_1952 authid definer as
    -- customizations for AvroTechnik
    procedure advanceStatus (p_wotAutoKey number);
end;


--_pkgBody
create or replace package body aqc_1952 as
    --
    --
    -- AvroTechnik generally has only two tasks on their work orders.  The first relates to inspection and when it is
    -- started work order's status should advance to 'In Prog-Initial'.  Similarly when work starts on the second the
    -- work order status should advance to 'In-Prog. Final'.  To know if the work-order status should change when labour
    -- is being undertaken on a particular task, we use the 'severity' of the wo_status.  This routine will only advance
    -- the status if the current status is lower than what we would want to change it to (either in-prog-init or
    -- in-prog-final).
    procedure advanceStatus (p_wotAutoKey number) as
        IN_PROG_INIT  constant  varchar2(20) := 'In Prog-Initial';
        IN_PROG_FINI  constant  varchar2(20) := 'In-Prog.';
        l_ipi_wos_auto_key number;   l_ipi_severity  number;
        l_ipf_wos_auto_key number;   l_ipf_severity  number;
        l_wooAutoKey number;  l_wotSequence number;
        l_wot_severity  number;
        l_woo_severity  number;
        --
    begin
        -- get info about/from the task
        select woo_auto_key, sequence
          into l_wooAutoKey, l_wotSequence
          from wo_task
         where wot_auto_key = p_wotAutoKey;
        --
        if l_wotSequence not in (1,2) then
            -- only process this automated status advancement when the wot is
            -- sequence 1 or 2
            return;
        end if;
        --
        -- get the key and severity for IN_PROG_INIT
        select wos_auto_key,       nvl(severity, 0)
          into l_ipi_wos_auto_key, l_ipi_severity
          from wo_status
         where description = IN_PROG_INIT;
        --
        -- get the key and severity for IN_PROG_FINI
        select wos_auto_key,       nvl(severity, 0)
          into l_ipf_wos_auto_key, l_ipf_severity
          from wo_status
         where description = IN_PROG_FINI;
        --
        select nvl(WOS.severity, 0)
          into l_wot_severity
          from wo_task   WOT
             , wo_status WOS
         where WOT.wos_auto_key = WOS.wos_auto_key (+)
           and WOT.wot_auto_key = p_wotAutoKey ;
        --
        select nvl(WOS.severity, 0)
          into l_woo_severity
          from wo_operation WOO
             , wo_status    WOS
         where WOO.wos_auto_key = WOS.wos_auto_key (+)
           and WOO.woo_auto_key = l_wooAutoKey ;
        --
        update wo_task
           set wos_auto_key = decode(l_wotSequence, 1, l_ipi_wos_auto_key,
                                                    2, l_ipf_wos_auto_key)
         where wot_auto_key = p_wotAutoKey
           and sequence in (1,2)
           and l_wot_severity < decode(l_wotSequence, 1, l_ipi_severity,
                                                      2, l_ipf_severity) ;
        --
        update wo_operation
           set wos_auto_key = decode(l_wotSequence, 1, l_ipi_wos_auto_key,
                                                    2, l_ipf_wos_auto_key)
         where woo_auto_key = l_wooAutoKey
           and l_woo_severity < decode(l_wotSequence, 1, l_ipi_severity,
                                                      2, l_ipf_severity) ;
    end;
    --
end;
