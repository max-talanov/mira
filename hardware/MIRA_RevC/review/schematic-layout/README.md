# Schematic organization and annotation — KiCad 10.0.5

All three active RevC projects use independent page sequences starting at 100, in steps of 100. The numbers are native KiCad sheet-instance page fields, including root `sheet_instances`; they are present in PDF title blocks and the schematic navigator.

Component references use the page number followed by a two-digit sequence for each prefix: `R30001`, `C30001`, `U70001`. A physical multi-unit package retains one reference, based on the first page containing any of its units. `reference-map.json` maps the original references to the new ones separately for each project. Symbol UUIDs, values, footprints, unit assignments and electrical connections are retained. PCB edits only migrate reference text and schematic paths; geometry, pads, tracks, net assignments and footprint UUIDs are unchanged.

Local work remains outside the task commit. In the working copy, the original trial socket `J3` is now `J10003`, with its placement and unassigned contacts preserved. The working-copy Crossbar PDF includes that trial; the committed Crossbar PDF contains the committed circuit only.

## PDFs

- [Control](PDF/MIRA_Control.pdf) — 62 pages; complete CH48 channels on pages 2600–3700.
- [Power](PDF/MIRA_Power.pdf) — 57 pages; complete input protection path on page 300.
- [Crossbar](PDF/MIRA_Crossbar.pdf) — page 100.

## Merged sheets

Each original four-channel driver sheet is combined with its matching `CHxx_sense.kicad_sch` on A1 portrait. Shared quad amplifier/switch packages remain intact. The four channel columns run from drive and remote feedback through voltage/current sensing to comparator and fault latch; common buffers, bleed switches and reference are below. The original symbol UUIDs remain, and transferred symbols use the destination sheet path.

| Destination | Sources |
| --- | --- |
| C_AFE_BL0_BL3.kicad_sch | C_AFE_BL0_BL3.kicad_sch + CH00_sense.kicad_sch |
| C_AFE_BL4_BL7.kicad_sch | C_AFE_BL4_BL7.kicad_sch + CH04_sense.kicad_sch |
| C_AFE_BL8_BL11.kicad_sch | C_AFE_BL8_BL11.kicad_sch + CH08_sense.kicad_sch |
| C_AFE_BL12_BL15.kicad_sch | C_AFE_BL12_BL15.kicad_sch + CH12_sense.kicad_sch |
| C_AFE_BL16_BL19.kicad_sch | C_AFE_BL16_BL19.kicad_sch + CH16_sense.kicad_sch |
| C_AFE_BL20_BL23.kicad_sch | C_AFE_BL20_BL23.kicad_sch + CH20_sense.kicad_sch |
| C_AFE_BL24_BL27.kicad_sch | C_AFE_BL24_BL27.kicad_sch + CH24_sense.kicad_sch |
| C_AFE_BL28_BL31.kicad_sch | C_AFE_BL28_BL31.kicad_sch + CH28_sense.kicad_sch |
| C_AFE_NL0_NL3.kicad_sch | C_AFE_NL0_NL3.kicad_sch + CH32_sense.kicad_sch |
| C_AFE_NL4_NL7.kicad_sch | C_AFE_NL4_NL7.kicad_sch + CH36_sense.kicad_sch |
| C_AFE_NL8_NL11.kicad_sch | C_AFE_NL8_NL11.kicad_sch + CH40_sense.kicad_sch |
| C_AFE_NL12_NL15.kicad_sch | C_AFE_NL12_NL15.kicad_sch + CH44_sense.kicad_sch |
| POWER_INPUT.kicad_sch | 100_INPUT_CONNECTOR.kicad_sch + 200_INPUT_FUSE_PROTECTION.kicad_sch + 300_INPUT_EFUSE_PROTECTION.kicad_sch + 400_INPUT_FILTER_SENSE.kicad_sch |

The four Power input stages occupy a single A2 sheet in reading order: connector, fuse/TVS, eFuse/reverse protection, output filter/shunt. Original per-stage design notes are retained.

Converter sheets remain separate: regulator, output filter, feedback setting, enable and power-good already form a complete local functional unit. The shared enable gates, isolated VIN enables and rail monitor banks remain separate to avoid mixing unrelated rails and crowding the converter pages. Their sheets are grouped in Power Sequencing and Rail Monitoring. Zynq multi-bank and DDR circuitry also remains separate for readability.

## Validation

ERC is run with each project’s existing settings and exclusions. See `erc/` and `validation.json`. Electrical comparison treats each net as a set of `(original reference, pin number)` pairs, so hierarchy-dependent local net names may change without producing a false difference. It also compares component values/footprints, library pin definitions, pin numbers and population attributes. `audit_layout.py` separately checks every placed symbol UUID, native page number, annotation and existing PCB binding, and proves that PCB changes contain only reference/path migration.

Pre-edit netlists and all original local files are retained under `/tmp/mira-schematic-review`. Baseline files are captured before editing. The final exported XML netlists are compressed losslessly as `netlists/*.xml.gz`.

From `hardware/MIRA_RevC`, repeat ERC/PDF/netlist exports with the installed KiCad 10.0.5 CLI:

```sh
kicad-cli sch erc --exit-code-violations -o /tmp/control-erc.rpt MIRA_Control/MIRA_Control.kicad_sch
kicad-cli sch erc --exit-code-violations -o /tmp/power-erc.rpt MIRA_Power/MIRA_Power.kicad_sch
kicad-cli sch erc --exit-code-violations -o /tmp/crossbar-erc.rpt MIRA_Crossbar/MIRA_Crossbar.kicad_sch
kicad-cli sch export netlist --format kicadxml -o /tmp/control.xml MIRA_Control/MIRA_Control.kicad_sch
kicad-cli sch export netlist --format kicadxml -o /tmp/power.xml MIRA_Power/MIRA_Power.kicad_sch
kicad-cli sch export netlist --format kicadxml -o /tmp/crossbar.xml MIRA_Crossbar/MIRA_Crossbar.kicad_sch
python3 review/ch48/verify_ch48.py /tmp/control.xml /tmp/crossbar.xml --reference-map review/schematic-layout/reference-map.json
python3 review/schematic-layout/compare_netlists.py MIRA_Control /tmp/mira-schematic-review/MIRA_Control-before.xml /tmp/control.xml
python3 review/schematic-layout/compare_netlists.py MIRA_Power /tmp/mira-schematic-review/MIRA_Power-before.xml /tmp/power.xml
python3 review/schematic-layout/compare_netlists.py MIRA_Crossbar /tmp/mira-schematic-review/MIRA_Crossbar-before.xml /tmp/crossbar.xml
python3 review/schematic-layout/audit_layout.py --baseline /tmp/mira-schematic-review/original/hardware/MIRA_RevC
```

PDF title-block page IDs are checked against `pages.json` on all pages. All 12 merged channel sheets and the Power input sheet were rendered and visually inspected; all PDF text lies inside the page bounds.

## MIRA_Control

| Page | Sheet | File |
| ---: | --- | --- |
| 100 | Control Overview | `MIRA_Control.kicad_sch` |
| 200 | MCU | `MCU.kicad_sch` |
| 300 | MCU Power and Debug | `100_MCU_POWER_CLOCKS_AND_DEBUG.kicad_sch` |
| 400 | MCU SDRAM | `200_MCU_FMC_AND_SDRAM.kicad_sch` |
| 500 | MCU Storage and Control | `300_MCU_QSPI_MICROSD_AND_CONTROL.kicad_sch` |
| 600 | Power Interface | `INTERCONNECT.kicad_sch` |
| 700 | Supervisor Interface | `400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch` |
| 800 | Digital Power Entry | `410_DISTRIBUTED_DIGITAL_POWER.kicad_sch` |
| 900 | Analog Power Entry | `420_DISTRIBUTED_ANALOG_POWER.kicad_sch` |
| 1000 | Zynq and Memory | `C_GROUP_ZYNQ.kicad_sch` |
| 1100 | Zynq PL I-O | `C_SOC0.kicad_sch` |
| 1200 | Zynq PS I-O | `C_SOC1.kicad_sch` |
| 1300 | Zynq Config and Power | `C_SOC2.kicad_sch` |
| 1400 | Zynq DDR3L | `C_DDR.kicad_sch` |
| 1500 | Zynq Boot and Reset | `C_Boot.kicad_sch` |
| 1600 | Zynq Decoupling | `C_Decoupling.kicad_sch` |
| 1700 | USB Interface | `C_GROUP_USB.kicad_sch` |
| 1800 | FX20 Bridge | `C_FX20.kicad_sch` |
| 1900 | USB-C Port | `C_USB_C.kicad_sch` |
| 2000 | DAC and ADC Banks | `C_GROUP_CONVERTERS.kicad_sch` |
| 2100 | CH00-15 Converters | `C_Bank0.kicad_sch` |
| 2200 | CH16-31 Converters | `C_Bank1.kicad_sch` |
| 2300 | CH32-47 Converters | `C_Bank2.kicad_sch` |
| 2400 | CH48 Analog Channels | `C_GROUP_LINES.kicad_sch` |
| 2500 | Channel Signal Flow | `C_ChannelGuide.kicad_sch` |
| 2600 | CH00-03 Drive and Sense | `C_AFE_BL0_BL3.kicad_sch` |
| 2700 | CH04-07 Drive and Sense | `C_AFE_BL4_BL7.kicad_sch` |
| 2800 | CH08-11 Drive and Sense | `C_AFE_BL8_BL11.kicad_sch` |
| 2900 | CH12-15 Drive and Sense | `C_AFE_BL12_BL15.kicad_sch` |
| 3000 | CH16-19 Drive and Sense | `C_AFE_BL16_BL19.kicad_sch` |
| 3100 | CH20-23 Drive and Sense | `C_AFE_BL20_BL23.kicad_sch` |
| 3200 | CH24-27 Drive and Sense | `C_AFE_BL24_BL27.kicad_sch` |
| 3300 | CH28-31 Drive and Sense | `C_AFE_BL28_BL31.kicad_sch` |
| 3400 | CH32-35 Drive and Sense | `C_AFE_NL0_NL3.kicad_sch` |
| 3500 | CH36-39 Drive and Sense | `C_AFE_NL4_NL7.kicad_sch` |
| 3600 | CH40-43 Drive and Sense | `C_AFE_NL8_NL11.kicad_sch` |
| 3700 | CH44-47 Drive and Sense | `C_AFE_NL12_NL15.kicad_sch` |
| 3800 | Masks and Protection | `C_GROUP_SAFETY.kicad_sch` |
| 3900 | CH00-07 Mask and Fault | `C_Mask0.kicad_sch` |
| 4000 | CH08-15 Mask and Fault | `C_Mask1.kicad_sch` |
| 4100 | CH16-23 Mask and Fault | `C_Mask2.kicad_sch` |
| 4200 | CH24-31 Mask and Fault | `C_Mask3.kicad_sch` |
| 4300 | CH32-39 Mask and Fault | `C_Mask4.kicad_sch` |
| 4400 | CH40-47 Mask and Fault | `C_Mask5.kicad_sch` |
| 4500 | Global Fault Latch | `C_Global.kicad_sch` |
| 4600 | Service DAC and Servo | `C_Service.kicad_sch` |
| 4700 | Mode Blanking | `C_Mode.kicad_sch` |
| 4800 | Logic Power 1 | `C_LogicPower0.kicad_sch` |
| 4900 | Unused Logic 1 | `C_SpareLogic0.kicad_sch` |
| 5000 | Logic Power Notes | `C_LogicPower1.kicad_sch` |
| 5100 | Logic Power 2 | `C_LogicPower2.kicad_sch` |
| 5200 | Unused Logic 2 | `C_SpareLogic1.kicad_sch` |
| 5300 | Forming Address Latch | `C_FormAddress.kicad_sch` |
| 5400 | Forming Routes | `C_GROUP_WORDLINES.kicad_sch` |
| 5500 | Gate Supply | `C_WL12.kicad_sch` |
| 5600 | Forming Interlock | `CH48_Interlock.kicad_sch` |
| 5700 | Forming Source | `CH48_Form_BL.kicad_sch` |
| 5800 | Forming Return | `CH48_Form_NL.kicad_sch` |
| 5900 | Forming Gate | `CH48_Form_WL.kicad_sch` |
| 6000 | Electrode Isolation | `CH48_Form_Isolation.kicad_sch` |
| 6100 | Module Interface | `C_GROUP_MODULE.kicad_sch` |
| 6200 | CH48 Module Connectors | `C_Crossbar.kicad_sch` |

## MIRA_Power

| Page | Sheet | File |
| ---: | --- | --- |
| 100 | Power Overview | `MIRA_Power.kicad_sch` |
| 200 | Power Distribution | `POWER_SYSTEM.kicad_sch` |
| 300 | 24 V Input and Protection | `POWER_INPUT.kicad_sch` |
| 400 | Primary Converters | `PRIMARY_POWER.kicad_sch` |
| 500 | AON 3.3 V | `500_AON_3V3_BUCK.kicad_sch` |
| 600 | USB 5 V | `600_USB_5V.kicad_sch` |
| 700 | System 3.3 V | `700_SYS_3V3.kicad_sch` |
| 800 | FPGA 5.5 V | `800_FPGA_INTERMEDIATE_5V5.kicad_sch` |
| 900 | Analog 6 V | `900_ANALOG_PREREGULATOR_6V.kicad_sch` |
| 1000 | AFE +15 V | `1000_AFE_POSITIVE_15V.kicad_sch` |
| 1100 | AFE -15 V | `1100_AFE_NEGATIVE_15V.kicad_sch` |
| 1200 | Secondary Converters | `SECONDARY_POWER.kicad_sch` |
| 1300 | FPGA Core 1 V | `1200_POWER_MONITOR.kicad_sch` |
| 1400 | FPGA Aux 1.8 V | `1300_FPGA_AUX_1V8.kicad_sch` |
| 1500 | FPGA Aux 2.5 V | `1400_FPGA_AUX_2V5.kicad_sch` |
| 1600 | FPGA I-O 3.3 V | `1500_FPGA_IO_3V3.kicad_sch` |
| 1700 | DDR 1.35 V | `1600_DDR_1V35.kicad_sch` |
| 1800 | I-O 1.8 V | `1700_IO_1V8.kicad_sch` |
| 1900 | DDR VTT and VREF | `1800_DDR_VTT_REFERENCE.kicad_sch` |
| 2000 | Analog 5 V | `1900_ANALOG_5V.kicad_sch` |
| 2100 | Analog 3.3 V | `2000_ANALOG_3V3.kicad_sch` |
| 2200 | Programming Rails | `PROGRAM_SWITCHES.kicad_sch` |
| 2300 | Program Positive | `2100_PROGRAM_POSITIVE.kicad_sch` |
| 2400 | Program Negative | `2200_PROGRAM_NEGATIVE.kicad_sch` |
| 2500 | Program Interface | `2300_PROGRAM_INTERFACE.kicad_sch` |
| 2600 | Control Board Outputs | `4900_POWER_CONTROL_INTERFACE.kicad_sch` |
| 2700 | Digital Power Outputs | `5000_DISTRIBUTED_DIGITAL_POWER.kicad_sch` |
| 2800 | Analog Power Outputs | `5100_DISTRIBUTED_ANALOG_POWER.kicad_sch` |
| 2900 | Power Sequencing | `POWER_CONTROL.kicad_sch` |
| 3000 | Power Manager MCU | `2400_PM_CONTROLLER.kicad_sch` |
| 3100 | Supply Watchdogs | `2500_PM_WATCHDOGS.kicad_sch` |
| 3200 | Host Link Watchdog | `5400_HOST_LINK_WATCHDOG.kicad_sch` |
| 3300 | Host Input Isolation | `5500_AON_HOST_INPUT_ISOLATION.kicad_sch` |
| 3400 | Startup Qualifier | `5200_PM_STARTUP_QUALIFIER.kicad_sch` |
| 3500 | Permit Interlocks | `2600_PM_PERMIT_INTERLOCKS.kicad_sch` |
| 3600 | Primary Enable Gates | `2700_PM_ENABLE_GATES_PRIMARY.kicad_sch` |
| 3700 | Aux Enable Gates | `2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch` |
| 3800 | Startup Output Gates | `5300_PM_STARTUP_OUTPUTS.kicad_sch` |
| 3900 | VIN Enables 1 | `5800_VIN_REFERENCED_ENABLES.kicad_sch` |
| 4000 | VIN Enables 2 | `5900_VIN_REFERENCED_ENABLES.kicad_sch` |
| 4100 | FPGA Aux Interlock | `6000_FPGA_AUX_IO_INTERLOCK.kicad_sch` |
| 4200 | Analog Power Good | `2900_PM_ANALOG_POWER_GOOD.kicad_sch` |
| 4300 | Rail Ready | `3000_PM_RAIL_READY.kicad_sch` |
| 4400 | Command Ready | `3100_PM_COMMAND_READY.kicad_sch` |
| 4500 | Negative Overcurrent | `3200_PM_NEGATIVE_OVERCURRENT.kicad_sch` |
| 4600 | PM Debug and Host | `3300_PM_DEBUG_HOST_INTERFACE.kicad_sch` |
| 4700 | Rail Monitoring | `POWER_MONITOR.kicad_sch` |
| 4800 | Negative Rail Sense | `3400_NEGATIVE_RAIL_MONITOR.kicad_sch` |
| 4900 | Input and System Sense | `3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch` |
| 5000 | Primary Rail Sense | `3600_MONITOR_FPGA_ANA_AFE.kicad_sch` |
| 5100 | FPGA Rail Sense | `3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch` |
| 5200 | DDR and Analog Sense | `3800_MONITOR_DDR_IO_ANALOG.kicad_sch` |
| 5300 | Analog Isolation 1 | `5600_AON_ANALOG_INPUT_ISOLATION.kicad_sch` |
| 5400 | Analog Isolation 2 | `5700_AON_ANALOG_INPUT_ISOLATION.kicad_sch` |
| 5500 | Monitor Enable Buffer | `6100_AON_MONITOR_ENABLE_BUFFER.kicad_sch` |
| 5600 | Telemetry Selectors | `3900_TELEMETRY_MULTIPLEXERS.kicad_sch` |
| 5700 | Telemetry ADC Buffers | `4000_TELEMETRY_ADC_BUFFERS.kicad_sch` |

## MIRA_Crossbar

| Page | Sheet | File |
| ---: | --- | --- |
| 100 | CH48 Crossbar | `MIRA_Crossbar.kicad_sch` |
