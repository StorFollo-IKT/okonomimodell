SELECT BIOS.SerialNumber0,
       csys.Manufacturer0,
       csys.Model0,
       sys.Name0,
       sys.User_Name0,
       sys.User_Domain0,
       sys.Creation_Date0,
       sys.Last_Logon_Timestamp0
FROM v_r_system as sys
         join v_GS_COMPUTER_SYSTEM as csys on sys.resourceid = csys.resourceid
         join v_gs_pc_bios as bios on sys.resourceid = bios.resourceid
ORDER BY sys.Last_Logon_Timestamp0