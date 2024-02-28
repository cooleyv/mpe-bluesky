# BDP plans

Bluesky plans related to BDP activities in 2023-05.

- [BDP plans](#bdp-plans)
  - [Plans](#plans)
  - [Data Management for the BDP](#data-management-for-the-bdp)


## Plans

- Working example: `demo202305()`

Existing fly scans use the taxi/fly in the 1ide IOC.

```bash
(bluesky_2024_1) s1idtest@kurtag .../macros_PK/fastsweep_2018Jan22 $ grep PSOPV * | grep 1id
osc_fastsweep_FPGA_hydra.mac:    #PSOPV="1ide:PSOFly1:" # for aero
osc_fastsweep_FPGA_hydra.mac:    #PSOPV="1idrams1:PSOFly1:" # for ramsrot RAMS1
osc_fastsweep_FPGA_hydra.mac:    if (fs_type=="aero") PSOPV="1ide:PSOFly1:"  # For aero, Ensemble
osc_fastsweep_FPGA_hydra.mac:    if (fs_type=="rams1") PSOPV="1idrams1:PSOFly1:" # For ramsrot, RAMS1 with AeroTech dual loop
osc_fastsweep_FPGA_hydra.mac:    if (fs_type=="rams3") PSOPV="1idrams3:PSOFly1:" # For ramsrot, RAMS3 with A32000 single loop
osc_fastsweep_FPGA_hydra.mac:    PSOPV="1ide:PSOFly1:"
```

For reference, the IOC boots from this directory:

```bash
kurtag% pwd
/net/s1dserv/xorApps/epics/synApps_5_8/ioc/1ide/iocBoot/ioc1ide
kurtag% grep taxi dbl-all.txt 
1ide:PSOFly1:taxi
1ide:PSOOsc:taxi
1ide:hexFly1:taxi
1ide:hexFly2:taxi
kurtag% grep fly dbl-all.txt
1ide:PSOFly1:fly
1ide:PSOOsc:fly
1ide:hexFly1:fly
1ide:hexFly2:fly
kurtag% caget 1ide:PSOFly1:taxi.RTYP
1ide:PSOFly1:taxi.RTYP         busy
```

## Data Management for the BDP

See related [document](./README-DM.md)
