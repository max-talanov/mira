# Power design notes

Original schematic guide content, moved out of the drawing area. References are updated to the current annotation. Repeated section headings are retained to preserve context. Numeric operating conditions are also summarized beside the corresponding circuit.

## 5400_HOST_LINK_WATCHDOG.kicad_sch

5400  APPLICATION HEARTBEAT AND HOST RESET

## 5400_HOST_LINK_WATCHDOG.kicad_sch

HOST RESET
U280005 adds an open-drain LOW from HOST_WDO_N.
U270001 and manual reset remain connected.
HOST_RESET_N pullups stay on SYS3V3.

## 5400_HOST_LINK_WATCHDOG.kicad_sch

U280001

## 5400_HOST_LINK_WATCHDOG.kicad_sch

U280002

## 5400_HOST_LINK_WATCHDOG.kicad_sch

U280004

## 5400_HOST_LINK_WATCHDOG.kicad_sch

U280003

## 5400_HOST_LINK_WATCHDOG.kicad_sch

U280005

## 5400_HOST_LINK_WATCHDOG.kicad_sch

HEARTBEAT CONTRACT
HOST_ALIVE is a periodic application pulse,
not a static ready level. Pinout retained.
Falling edges every 50 ms; firmware gap
<=100 ms. No free-running PWM or DMA.
Each edge requires valid link and progress.

HARDWARE TIMEOUT
R280001=10k selects 170..230 ms timeout.
Missing edges, stuck HIGH/LOW or an open
source remove LINK_READY_H.

FIRST EDGE / RESTART
U280004 starts cleared by LINK_RESET_N.
A heartbeat edge sets readiness.
WDO expiry clears it; WDO recovery alone
does not restore it. A new edge is needed.
Power matrix permission still needs ARM;
Control needs a fresh valid configuration.

CONNECTIONS
LINK_READY_H -> U310003.13 and PM PC15.
PC15: input, no pull; LSE disabled.
Read readiness before MATRIX_ARM.

SUPPLIES / PLACEMENT
All added logic is powered by AON.
Put C540x at matching U540x VCC.
Keep clear and clock routes short.
Reserve another 2 mA and 0.5 uF on AON.

LIMITS
The circuit detects edges, not message
validity. Firmware must stop heartbeat
on loss of link, session or task progress.
Ramp and back-power tests remain open.

## 600_USB_5V.kicad_sch

R60004 (0.05 Ohm) causes a 50 mV/A drop: USB5 is about 4.95 V at 1 A. Feedback
is before the shunt. U60001 is a 1 A IC with internal current, short-circuit
and thermal protection. D60001 indicates rail presence; R60004 does not set the
current limit.

## 600_USB_5V.kicad_sch

Buck stage

## 600_USB_5V.kicad_sch

Conversion and filtering

## 600_USB_5V.kicad_sch

SHEET GUIDE / USB 5 V

## 600_USB_5V.kicad_sch

BUS24 feeds U60001 (LMR51610XDBVR). CMD_USB drives Q60001 as an active-high
source follower. R60002 (100 kOhm) pulls EN_USB low when Q60001 is off. The
command must not float; verify its high-level margin.

## 600_USB_5V.kicad_sch

Output and protection

## 600_USB_5V.kicad_sch

U60001 operates at 400 kHz with PFM at light load. L60001 (33 uH) and C60003/C60002
(47 uF each) filter USB_RAW. C60004/C60001 bypass the input; C60005 (100 nF) is the
CB-to-SW bootstrap capacitor.

## 600_USB_5V.kicad_sch

Purpose and role

## 600_USB_5V.kicad_sch

Output voltage setting

## 600_USB_5V.kicad_sch

R60005 (105 kOhm) and R60003 (20 kOhm) set USB_RAW:
VRAW = 0.8 V x (1 + R60005/R60003) = 5.00 V.
To change the voltage: R60005 = R60003 x (VRAW/0.8 V - 1). Increasing the upper
resistor raises VRAW.

## 600_USB_5V.kicad_sch

Input and enable

## 600_USB_5V.kicad_sch

400 kHz / PFM

## 600_USB_5V.kicad_sch

Enable control

## 600_USB_5V.kicad_sch

Output setting

## 600_USB_5V.kicad_sch

R60005/R60003: 5.00 V before R60004.
R60004 causes a 50 mV/A drop.

## 600_USB_5V.kicad_sch

Controlled USB supply, 5.00 V before shunt

## 600_USB_5V.kicad_sch

CMD_USB drives Q60001 as a source follower.
R60002 pulls EN low when Q60001 is off.
The command must have a defined level.

## 600_USB_5V.kicad_sch

Generates USB5 from BUS24 for local USB-related circuitry. CMD_USB controls
whether this supply is enabled.

## 600_USB_5V.kicad_sch

USB 5 V

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

BUS24 feeds U80001 (LM76005RNPR). CMD_FPGA drives Q80001 as an active-high source
follower; R80003 (100 kOhm) pulls EN_FPGA low when Q80001 is off. R80002 (10 kOhm)
pulls the open-drain PG_FPGA output up to AON.

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

Output filter and feedback

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

RT is open: nominal switching frequency is 400 kHz. MODE is grounded: PFM is
allowed at light load. C80005 (22 nF) extends soft-start. L80001 (6.8 uH) and
C80007-C80012 (6 x 47 uF) filter FPGA_RAW; C80001 shapes the feedback response.

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

400 kHz with RT open.
MODE = GND: PFM at light load.

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

SHEET GUIDE / FPGA 5.5 V

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

Output and protection

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

R80006/R80005: 5.525 V nominal at RAW. R80004: 10 mV/A.

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

Regulator core

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

Output voltage setting

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

Generates FPGA5V5 from BUS24 as an intermediate supply for downstream FPGA
power converters. CMD_FPGA enables the supply; PG_FPGA reports regulator
power-good status.

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

Input and enable

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

FPGA 5.5 V

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

R80004 (0.01 Ohm) causes a 10 mV/A drop. Feedback and PG_FPGA refer to FPGA_RAW
before the shunt. U80001 is a 5 A IC with internal current, short-circuit and
thermal protection. At 5 A, R80004 dissipates 0.25 W: verify thermal margin.
D80001 indicates rail presence.

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

Purpose and role

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

CMD_FPGA drives EN through Q80001.
PG_FPGA is pulled up to AON.

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

R80006 (100 kOhm) and R80005 (22.1 kOhm) set FPGA_RAW:
VRAW = VREF x (1 + R80006/R80005).
With VREF = 1 V, VRAW = 5.525 V (5.558 V using the typical 1.006 V PWM
reference). To change voltage: R80006 = R80005 x (VRAW/VREF - 1).

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

FPGA intermediate supply, approximately 5.5 V

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

Conversion and filtering

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

Enable and status

## 800_FPGA_INTERMEDIATE_5V5.kicad_sch

Feedback senses FPGA_RAW before R80004.

## 3000_PM_RAIL_READY.kicad_sch

Protection and fault response

## 3000_PM_RAIL_READY.kicad_sch

SHEET GUIDE / Rail Ready

## 3000_PM_RAIL_READY.kicad_sch

Live status; no settling timer or fault memory.

## 3000_PM_RAIL_READY.kicad_sch

Four local groups -> ALL_RAILS_PG

## 3000_PM_RAIL_READY.kicad_sch

Any included status going LOW deasserts ALL_RAILS_PG and removes one condition
for matrix operation. The permit and fault-memory circuitry determines shutdown
behavior. Intentionally disabling any included supply also removes readiness;
this tree provides no per-rail bypass.

## 3000_PM_RAIL_READY.kicad_sch

The tree receives PG_SYS, PG_FPGA, PG_ANA, PG_P15, PG_N15 and nine PGR
signals for the secondary rails. ALL_RAILS_PG is an active-high, push-pull
output. All three SN74HCS21 devices use AON; C390001, C390002 and C390003 provide 100
nF bypassing.

## 3000_PM_RAIL_READY.kicad_sch

Rail Ready

## 3000_PM_RAIL_READY.kicad_sch

All fifteen PG / PGR signals are required.

## 3000_PM_RAIL_READY.kicad_sch

Purpose and role

## 3000_PM_RAIL_READY.kicad_sch

Inputs and outputs

## 3000_PM_RAIL_READY.kicad_sch

Timing and settings

## 3000_PM_RAIL_READY.kicad_sch

Measured rail readiness

## 3000_PM_RAIL_READY.kicad_sch

Control logic

## 3000_PM_RAIL_READY.kicad_sch

Final AND stage

## 3000_PM_RAIL_READY.kicad_sch

There is no resistor-set threshold, timer or latch on this sheet. The aggregate
changes after two logic stages when a status changes. Schmitt inputs accept
slower status transitions. The unused U390003 gate has its inputs tied to GND and
its output left unconnected.

## 3000_PM_RAIL_READY.kicad_sch

Combined rail power-good logic

## 3000_PM_RAIL_READY.kicad_sch

U390001 combines USB/SYS/FPGA/ANA and P15/N15/CORE/AUX18. U3002 combines
AUX25/IO33/DDR/IO18 and VTT/ANA5/ANA33. AON fixes the fourth input of the last
group HIGH. U3003 ANDs PG_GROUP_0-PG_GROUP_3; every one of the fifteen status
inputs must be HIGH.

## 3000_PM_RAIL_READY.kicad_sch

This block combines MIRA's measured rail status into ALL_RAILS_PG. It tells the
power controller, matrix interlock and host interface that every included supply
reports ready. It works with the separate command aggregate so an enable request
alone cannot establish supply readiness.

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

This AON-powered hardware chain grants two latched permissions.
GLOBAL_PWR_PERMIT enables the switched MIRA supplies; MATRIX_PERMIT
allows the downstream matrix and programming circuits to operate.
A fault clears permission and requires an explicit re-arm.

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

Explicit rising-edge re-arm after a fault

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

Global fault chain
Clears all switched-rail permission

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

Matrix fault chain
Requires rails, commands and host ready

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

U310001 combines the global conditions; U310003 combines matrix conditions.
Their outputs drive the two active-low clears of U310002. With D HIGH
and preset inactive, a rising PWR_ARM_PULSE or MATRIX_ARM_PULSE
sets the corresponding permission only while its clear is HIGH.

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

Inputs and outputs

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

R310006/R310001 (10 kOhm) pull the stop lines HIGH; closing J310002/J310001
or asserting a kill GPIO pulls them LOW. R310002/R310004/R310007/R310003
(100 kOhm) hold kill and arm inputs LOW when released. There is no
RC delay: firmware must send clean arm edges after conditions settle.

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

A global fault clears both permissions; a matrix fault clears only
matrix permission. Fault recovery alone does not re-arm either latch.
Sheets 5200/5300 block startup outputs and qualify GLOBAL_CLEAR_N.
AON_RESET_N remains in the clear chain. The stop connectors trip
when closed; an open cable is not detected as a stop.

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

Timing and settings

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

Hardware permit interlocks

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

SHEET GUIDE / Permit Interlocks

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

Purpose and role

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

Protection and fault response

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

Control logic

## 2600_PM_PERMIT_INTERLOCKS.kicad_sch

Global inputs cover input power, AON reset, PM watchdog/reset,
overcurrent and global stop. Matrix inputs add rail/command
readiness, host watchdog/reset, LINK_READY_H and matrix stop.
J310003 exports MATRIX_PERMIT and raw MATRIX_KILL_H.
Application heartbeat qualification is on sheet 5400.

## 700_SYS_3V3.kicad_sch

R70006 (0.01 Ohm) causes a 10 mV/A drop. Feedback and PG_SYS refer to SYS_RAW
before the shunt. U70001 is a 5 A IC with internal current, short-circuit and
thermal protection. At 5 A, R70006 dissipates 0.25 W: verify thermal margin.
D70001 indicates rail presence.

## 700_SYS_3V3.kicad_sch

R70004/R70005: 3.315 V nominal at RAW. R70006: 10 mV/A.

## 700_SYS_3V3.kicad_sch

R70004 (100 kOhm) and R70005 (43.2 kOhm) set SYS_RAW:
VRAW = VREF x (1 + R70004/R70005).
With VREF = 1 V, VRAW = 3.315 V (3.335 V using the typical 1.006 V PWM
reference). To change voltage: R70004 = R70005 x (VRAW/VREF - 1).

## 700_SYS_3V3.kicad_sch

BUS24 feeds U70001 (LM76005RNPR). CMD_SYS drives Q70001 as an active-high source
follower; R70002 (100 kOhm) pulls EN_SYS low when Q70001 is off. R70001 (10 kOhm)
pulls the open-drain PG_SYS output up to AON.

## 700_SYS_3V3.kicad_sch

CMD_SYS drives EN through Q70001.
PG_SYS is pulled up to AON.

## 700_SYS_3V3.kicad_sch

System 3.3 V

## 700_SYS_3V3.kicad_sch

Output and protection

## 700_SYS_3V3.kicad_sch

Conversion and filtering

## 700_SYS_3V3.kicad_sch

RT is open: nominal switching frequency is 400 kHz. MODE is grounded: PFM is
allowed at light load. C70003 (22 nF) extends soft-start. L70001 (6.8 uH) and
C70013-C70012 (6 x 47 uF) filter SYS_RAW; C70006 shapes the feedback response.

## 700_SYS_3V3.kicad_sch

Generates SYS3V3 from BUS24 for system logic. CMD_SYS enables the supply;
PG_SYS reports regulator power-good status to external control circuitry.

## 700_SYS_3V3.kicad_sch

Controlled system supply, approximately 3.3 V

## 700_SYS_3V3.kicad_sch

Output filter and feedback

## 700_SYS_3V3.kicad_sch

Input and enable

## 700_SYS_3V3.kicad_sch

Purpose and role

## 700_SYS_3V3.kicad_sch

400 kHz with RT open.
MODE = GND: PFM at light load.

## 700_SYS_3V3.kicad_sch

Output voltage setting

## 700_SYS_3V3.kicad_sch

Regulator core

## 700_SYS_3V3.kicad_sch

Feedback senses SYS_RAW before R70006.

## 700_SYS_3V3.kicad_sch

Enable and status

## 700_SYS_3V3.kicad_sch

SHEET GUIDE / System 3.3 V

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

Purpose and role

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

This AON-powered gate bank turns the power manager requests into
hardware-qualified commands for the primary MIRA supply domains.
It enables staged startup while the global permit remains valid,
and removes all eight commands when that permit is cleared.

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

Timing and settings

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

SHEET GUIDE / Primary Enable Gates

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

USB / system / FPGA / analog requests

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

Control logic

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

Clearing GLOBAL_PWR_PERMIT drives every command LOW, even if
a firmware request remains HIGH. A request released by the MCU
also goes LOW through its pull-down. Rail shutdown time depends
on the connected converter or switch and its output capacitance.

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

Every channel uses the same rule:
CMD_x_RAW = GLOBAL_PWR_PERMIT AND EN_REQ_x.
Sheet 5300 passes these commands only after STARTUP_READY_H.
The power manager chooses the sequence and explicitly arms permits.

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

U320001 generates CMD_USB_RAW, CMD_SYS_RAW, CMD_FPGA_RAW and CMD_ANA_RAW.
U320002 generates CMD_P15_RAW, CMD_N15_RAW, CMD_CORE_RAW and CMD_AUX18_RAW.
Each channel receives GLOBAL_PWR_PERMIT and its corresponding
EN_REQ signal from the power manager.

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

Protection and fault response

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

Primary Enable Gates

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

AFE / FPGA core / AUX1V8 requests

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

Raw CMD = request AND global permit; qualified on sheet 5300

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

Inputs and outputs

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

Primary rail enable gates

## 2700_PM_ENABLE_GATES_PRIMARY.kicad_sch

All request and command lines have 100 kOhm pull-downs.
C320001/C320002 (100 nF) bypass the two SN74HC08 supplies to GND.
This sheet contains no startup delay or voltage/current setting;
those settings belong to the sequencer and the rail circuits.

## 1700_IO_1V8.kicad_sch

Regulated 1.8 V for FX20 GPIF, USB3 analog supply, Zynq banks 13/33
and the ADC/DAC digital interfaces. Verify the voltage margin at the load.

## 1700_IO_1V8.kicad_sch

FPGA5V5 -> IO18_RAW; L160001 + C160002 filter the output.
VOS and feedback sense RAW before R160006.

## 1700_IO_1V8.kicad_sch

Output and protection

## 1700_IO_1V8.kicad_sch

I-O 1.8 V

## 1700_IO_1V8.kicad_sch

CMD_IO18 drives Q160001; R160005 pulls EN low.

## 1700_IO_1V8.kicad_sch

R160002 (20 kOhm) and R160001 (16 kOhm) set the RAW voltage:
V(IO18_RAW)=0.8 V x (1+R160002/R160001) = 1.8 V.
To change it: R160002 = R160001 x (VRAW / 0.8 V - 1). Increasing R160002 raises the
voltage. DEF is grounded; the +5% margin is disabled.

## 1700_IO_1V8.kicad_sch

Output sensing

## 1700_IO_1V8.kicad_sch

Buck conversion and filtering

## 1700_IO_1V8.kicad_sch

Conversion and filtering

## 1700_IO_1V8.kicad_sch

R160006 (0.02 Ohm) drops 20 mV/A outside feedback. At 3 A, IO1V8 is about
1.740 V. R160003 (10 kOhm) bleeds the output. PGR_IO18 is open drain, pulled to
AON by R160004 (10 kOhm); use its RAW status only with FPGA5V5 present. The IC
supports up to 3 A, subject to thermal and shared-input limits. Current and
thermal protection are internal.

## 1700_IO_1V8.kicad_sch

SHEET GUIDE / I-O 1.8 V

## 1700_IO_1V8.kicad_sch

USB and converter I/O core supply, approximately 1.8 V

## 1700_IO_1V8.kicad_sch

Input and enable

## 1700_IO_1V8.kicad_sch

Output voltage setting

## 1700_IO_1V8.kicad_sch

L160001 and C160002 filter the output. Verify the control mode, transient
response and effective capacitance at the new 1.8 V setpoint.

## 1700_IO_1V8.kicad_sch

Purpose and role

## 1700_IO_1V8.kicad_sch

RAW: 1.800 V nominal; shunt: 20 mV/A.
PGR_IO18: RAW status, pulled up to AON.

## 1700_IO_1V8.kicad_sch

Enable control

## 1700_IO_1V8.kicad_sch

U160001 (TPS62130A) receives FPGA5V5 at AVIN and both PVIN pins. C160004 (10 uF)
and C160001 (100 nF) bypass the input. CMD_IO18 drives Q160001; a high command
enables EN_IO18. R160005 (100 kOhm) pulls EN low when Q160001 is off. FPGA5V5 must
be available first.

## 500_AON_3V3_BUCK.kicad_sch

AON 3.3 V

## 500_AON_3V3_BUCK.kicad_sch

Output voltage setting

## 500_AON_3V3_BUCK.kicad_sch

Always-on conversion

## 500_AON_3V3_BUCK.kicad_sch

Conversion and filtering

## 500_AON_3V3_BUCK.kicad_sch

Always-on control supply, 3.28 V before shunt

## 500_AON_3V3_BUCK.kicad_sch

Input and enable

## 500_AON_3V3_BUCK.kicad_sch

U50001 operates at 400 kHz with PFM at light load. L50001 (33 uH) and C50004/C50005
(47 uF each) filter AON_RAW. C50001 (100 nF) is the CB-to-SW bootstrap
capacitor.

## 500_AON_3V3_BUCK.kicad_sch

R50003 (0.1 Ohm) causes a 100 mV/A drop: AON is about 3.18 V at 1 A. Feedback
is before the shunt. U50001 is a 1 A IC with internal current, short-circuit
and thermal protection. D50001 indicates rail presence; R50003 does not set the
current limit.

## 500_AON_3V3_BUCK.kicad_sch

Purpose and role

## 500_AON_3V3_BUCK.kicad_sch

R50001/R50004: 3.28 V before R50003.
R50003 causes a 100 mV/A drop.

## 500_AON_3V3_BUCK.kicad_sch

BUS24 feeds U50001 (LMR51610XDBVR) VIN and EN directly. No separate enable
command is required. C50003 (100 nF) and C50002 (4.7 uF) bypass the input.

## 500_AON_3V3_BUCK.kicad_sch

Starts automatically while BUS24 is present.
U50001 operates at 400 kHz; PFM at light load.

## 500_AON_3V3_BUCK.kicad_sch

R50001 (62 kOhm) and R50004 (20 kOhm) set AON_RAW:
VRAW = 0.8 V x (1 + R50001/R50004) = 3.28 V.
To change the voltage: R50001 = R50004 x (VRAW/0.8 V - 1). Increasing the upper
resistor raises VRAW.

## 500_AON_3V3_BUCK.kicad_sch

Output and protection

## 500_AON_3V3_BUCK.kicad_sch

Output setting

## 500_AON_3V3_BUCK.kicad_sch

SHEET GUIDE / AON 3.3 V

## 500_AON_3V3_BUCK.kicad_sch

Generates AON for control and protection circuitry. AON is available while
BUS24 is present, even when command-controlled supplies are disabled.
Removing BUS24 also removes AON.

## 5200_PM_STARTUP_QUALIFIER.kicad_sch

5200  AON STARTUP QUALIFIER

## 5200_PM_STARTUP_QUALIFIER.kicad_sch

STARTUP BLOCKING
U300001 senses AON: 590k / 100k divider.
Nominal falling threshold: 2.7945 V.
CT via 100k to AON: 180..420 ms delay.
Existing TPS3851 AON reset is retained.

LOW-VOLTAGE PATH
150k RESET pull-up feeds one AUP input.
U300002 and U340001..U340008 operate from 0.8 V.
Do not substitute HC/HCS or LVC here.
RESET fanout must remain isolated by U300002.

RE-ARM
GLOBAL_CLEAR_N = GLOBAL_CLEAR_RAW_N
                    AND STARTUP_READY_H.
After a detected AON fault, a fresh PWR_ARM
and then MATRIX_ARM edge are required.
No automatic permit restoration.

VALIDATION
Design review envelope: -40..+85 degC.
Verify ramp/fault timing on the prototype.
See docs/pcb-preparation/startup/README.md.

## 2300_PROGRAM_INTERFACE.kicad_sch

R210003 (47 kOhm) and R210001 (10 kOhm) attenuate the positive rail. R210002 (10
kOhm) limits ADC-node source current; C210001 (100 nF) filters PROG_V_P15.
Including the divider resistance, tau is about 1.82 ms. This path monitors
the rail level and averages short programming pulses.

## 2300_PROGRAM_INTERFACE.kicad_sch

SHEET GUIDE / Program Interface

## 2300_PROGRAM_INTERFACE.kicad_sch

Positive rail monitor

## 2300_PROGRAM_INTERFACE.kicad_sch

The divider measures voltage; it does not set the programming rails.
V(PROG_V_P15) = V(PROG_P15) x R210001 / (R210003 + R210001) = V(PROG_P15) / 5.7. A
15 V positive output gives about 2.632 V. Update the ADC conversion scale if
either divider value changes.

## 2300_PROGRAM_INTERFACE.kicad_sch

Output and protection

## 2300_PROGRAM_INTERFACE.kicad_sch

Programming rail output

## 2300_PROGRAM_INTERFACE.kicad_sch

Input and enable

## 2300_PROGRAM_INTERFACE.kicad_sch

BAT54S: 1 = GND, 2 = AON, 3 = ADC node.
Keep AON valid while the programming rail is present.

## 2300_PROGRAM_INTERFACE.kicad_sch

15 V -> 2.632 V at PROG_V_P15
Rail-level check; tau about 1.82 ms.

## 2300_PROGRAM_INTERFACE.kicad_sch

D210001 (BAT54S) clamps PROG_V_P15 toward GND and AON: pin 1 = GND, pin 2 =
AON, pin 3 = monitor node. The upper clamp can inject current into AON during
faults or power-off. Rail switching and power protection remain upstream;
this sheet measures only the positive output.

## 2300_PROGRAM_INTERFACE.kicad_sch

1: PROG_P15   2: GND   3: PROG_N15
Switched rails arrive from upstream.

## 2300_PROGRAM_INTERFACE.kicad_sch

Programming rail interface and monitor

## 2300_PROGRAM_INTERFACE.kicad_sch

Program Interface

## 2300_PROGRAM_INTERFACE.kicad_sch

Conversion and filtering

## 2300_PROGRAM_INTERFACE.kicad_sch

Output voltage setting

## 2300_PROGRAM_INTERFACE.kicad_sch

PROG_P15 and PROG_N15 are generated and enabled on the upstream
programming-switch sheets. This interface contains no local enable logic.
J210001 exports pin 1 = PROG_P15, pin 2 = GND, pin 3 = PROG_N15. The actual
voltage follows the upstream sources, switches and load.

## 2300_PROGRAM_INTERFACE.kicad_sch

Purpose and role

## 2300_PROGRAM_INTERFACE.kicad_sch

This sheet brings MIRA's switched positive and negative programming rails to
J210001 and provides a scaled monitor of the positive output. It links the
programming power switches to the matrix-drive hardware, allowing the power
controller to check rail availability before a programming operation.

## POWER_INPUT.kicad_sch

Correct input polarity

## POWER_INPUT.kicad_sch

DC input
J30001 connects the external 24 V supply
to +24V_RAW and GND.

## POWER_INPUT.kicad_sch

J30001 is the external DC input connector. Pin 1 connects to +24V_RAW; pin 2
connects to GND, the input return. The +24V_RAW net supplies the downstream
input-protection circuitry. R30001, D30002 and D30001 form a polarity
indicator connected across the input terminals.

## POWER_INPUT.kicad_sch

Polarity indication
D30001 (green): correct input polarity.
D30002 (red): reversed input polarity.

## POWER_INPUT.kicad_sch

NAME: Input Connector

## POWER_INPUT.kicad_sch

Green indicates correct input polarity; red indicates reversed input polarity.
Both LEDs are off when no input voltage is present.

This circuit indicates polarity but does not prevent reverse voltage from
reaching downstream components. Reverse-polarity protection is provided by a
separate protection stage. The green LED does not confirm that a fuse is
intact, that an eFuse is enabled, or that downstream power rails are
operating.

## POWER_INPUT.kicad_sch

24 V Input Connector and Polarity Indicator

## POWER_INPUT.kicad_sch

Meaning of the indication

## POWER_INPUT.kicad_sch

R30001 is 10 kOhm. At an input magnitude of 24 V and an assumed LED forward
voltage of 2.0 V, the current is approximately 2.2 mA. R30001 dissipates
approximately 48 mW. Actual current depends on the forward voltage of the
conducting LED.

## POWER_INPUT.kicad_sch

Reversed input polarity

## POWER_INPUT.kicad_sch

If the supply leads are reversed, +24V_RAW becomes negative relative to GND.
Current flows from GND through the red LED D30002 and R30001 to J30001 pin 1.
D30002 illuminates, indicating reversed input polarity; D30001 remains off.

In this condition, D30002 limits the reverse voltage across D30001. R30001
limits the indicator current in either direction.

## POWER_INPUT.kicad_sch

When J30001 pin 1 is positive relative to pin 2, current flows from +24V_RAW
through R30001 and the green LED D30001 to GND. D30001 illuminates, indicating
correct input polarity. The red LED D30002 is reverse-biased and remains off.

The LEDs are connected in antiparallel, so D30001 limits the reverse voltage
across D30002 approximately to its own forward voltage.

## POWER_INPUT.kicad_sch

Purpose and connections

## POWER_INPUT.kicad_sch

SHEET GUIDE / Input Connector

## POWER_INPUT.kicad_sch

LED current and resistor setting

## POWER_INPUT.kicad_sch

LED reverse-voltage protection

## POWER_INPUT.kicad_sch

If F30001 opens and +24V_FUSED falls towards zero, R30002 discharges the gate
of Q30001. Q30001 turns off, allowing current to flow from +24V_RAW through
R30003 and the red LED D30004 to GND. D30004 illuminates and D30005 turns off.

## POWER_INPUT.kicad_sch

D30006 is an SMBJ36CA bidirectional TVS diode connected after F30001. It
diverts positive or negative surge current between +24V_FUSED and GND.

## POWER_INPUT.kicad_sch

Purpose and power path

## POWER_INPUT.kicad_sch

Transient suppression

## POWER_INPUT.kicad_sch

Fuse and TVS

## POWER_INPUT.kicad_sch

24 V Input Fuse, Status Indicators and Transient Protection

## POWER_INPUT.kicad_sch

With correct input polarity and an intact fuse, +24V_FUSED is approximately
equal to +24V_RAW. Current flows through R30005 and the green LED D30005 to
GND, so D30005 illuminates.

R30004 and R30002 form a divider that drives the gate of Q30001. Q30001 is an
N-channel BSS138N MOSFET: pin 1 is the gate, pin 2 is the source connected to
GND, and pin 3 is the drain connected to the red LED anode and R30003.

The positive gate voltage turns Q30001 on. Its drain-source channel bypasses
D30004 and holds the red LED anode close to GND, keeping D30004 off. Current
from +24V_RAW then flows through R30003 and Q30001 to GND.

## POWER_INPUT.kicad_sch

D30003 and D30007 are CD0603-B0240R Schottky diodes connected in antiparallel
with D30004 and D30005, respectively. They limit reverse voltage across the
LEDs approximately to their forward voltage.

## POWER_INPUT.kicad_sch

Normal operation

## POWER_INPUT.kicad_sch

F30001 connects +24V_RAW to +24V_FUSED. It is marked 5 A / 125 V and provides
overcurrent protection according to its time-current characteristic. The
+24V_FUSED net supplies the downstream input circuitry.

D30005 indicates voltage after the fuse. D30004 indicates loss of the fused
supply while the raw input remains present. D30006 suppresses voltage
transients between +24V_FUSED and GND.

## POWER_INPUT.kicad_sch

SHEET GUIDE / Fuse and TVS

## POWER_INPUT.kicad_sch

Fuse-open indication

## POWER_INPUT.kicad_sch

C30004 (100 nF) sets an output slew rate of approximately 0.5 V/ms, giving a
nominal 48 ms ramp to 24 V. Increasing C30004 slows startup and reduces
capacitive inrush. Closing JP30001 grounds SHDN_N and disables U30001.
Reopening JP30001 enables operation and can reset an overload latch.

## POWER_INPUT.kicad_sch

18-36 V input. UVLO 16.47 V rising; OVP 38.51 V rising. R30015 = 4.02k sets
4.48 A nominal.

## POWER_INPUT.kicad_sch

Voltage and current limits

## POWER_INPUT.kicad_sch

SHEET GUIDE / eFuse and Reverse Protection

## POWER_INPUT.kicad_sch

Status output

## POWER_INPUT.kicad_sch

eFuse and Reverse Protection

## POWER_INPUT.kicad_sch

R30006-R30007 set the PGTH threshold to approximately 16.20 V rising and 15.16
V falling. PG_INPUT asserts only when the output passes this threshold and
U30001's internal pass transistor is fully enhanced. R30011 pulls this
open-drain signal up to AON.

## POWER_INPUT.kicad_sch

+24V_FUSED supplies U30001 (TPS26631) through Q30003 (IRFR3410). U30001
controls Q30003 via B_GATE; Q30002 provides gate pull-down under DRV control.
Together with U30001, these transistors provide reverse-polarity and
reverse-current protection. The protected output is EFUSE_OUT. C30005-C30002
decouple the input; C30003 decouples the output. D30009 clamps negative output
transients.

## POWER_INPUT.kicad_sch

Purpose and power path

## POWER_INPUT.kicad_sch

Startup and shutdown

## POWER_INPUT.kicad_sch

24 V Electronic Fuse and Reverse-Polarity Protection

## POWER_INPUT.kicad_sch

SHEET GUIDE / Bus Filter and Shunt

## POWER_INPUT.kicad_sch

R30019 (20 mOhm / 1 W) carries the current delivered to BUS24. Its voltage
drop is proportional to current: 20 mV per ampere. Current is calculated as I
= (BUS24_PRE_SHUNT - BUS24) / 0.02 Ohm. At 3.5 A, the drop is 70 mV and
dissipation is approximately 0.245 W. Increasing R30019 increases measurement
sensitivity, voltage drop and heat. The current-measurement circuitry connects
elsewhere in the project.

## POWER_INPUT.kicad_sch

EFUSE_OUT feeds L30001, a ferrite bead rated 120 Ohm at 100 MHz / 6 A. L30001
attenuates high-frequency noise; its stated impedance is not its DC
resistance. C30008 (100 uF), C30006 (1 uF) and C30007 (100 nF) provide local
energy storage and bypass noise to GND. BUS24_PRE_SHUNT is the filtered supply
before R30019; BUS24 is the supply after R30019.

## POWER_INPUT.kicad_sch

Power path and filtering

## POWER_INPUT.kicad_sch

R30017 (10 kOhm) limits current through the green LED D30010. The LED
indicates voltage on BUS24, downstream of the shunt. At 24 V and approximately
2 V LED forward voltage, LED current is 2.2 mA.

R30018 and R30016 (100 kOhm each) form a 200 kOhm discharge path from BUS24 to
GND. They draw 120 uA at 24 V and slowly discharge the connected capacitance
after power removal. Reducing their resistance accelerates discharge and
increases continuous power consumption.

## POWER_INPUT.kicad_sch

24 V Bus Filtering and Current Sensing

## POWER_INPUT.kicad_sch

Current-sense shunt

## POWER_INPUT.kicad_sch

Bus Filter and Shunt

## POWER_INPUT.kicad_sch

Bus indicator and discharge

## POWER_INPUT.kicad_sch

24 V INPUT: connector -> fuse / TVS -> eFuse / reverse protection -> filter / shunt -> BUS24

## 5500_AON_HOST_INPUT_ISOLATION.kicad_sch

5500 / HOST INPUTS INTO AON

## 5500_AON_HOST_INPUT_ISOLATION.kicad_sch

SYS3V3 may remain present while AON is absent.

## 5500_AON_HOST_INPUT_ISOLATION.kicad_sch

RESET RECEIVE PATH
U290001 feeds U310003.10 only.
Host NRST and the open-drain watchdog
remain on the original HOST_RESET_N net.
R290001 defines an undriven input LOW.
R290002 defines an undriven output LOW.

## 5500_AON_HOST_INPUT_ISOLATION.kicad_sch

UART RECEIVE PATH
R420003 remains the 1 kOhm input resistor.
R420002 holds HOST_UART_TX_RAW LOW.
U290002 drives PM_UART_RX; R290003 pulls down.
C290001/C290002: place at each VCC pin.
Reserve +2 mA and +0.2 uF on AON.

## 5500_AON_HOST_INPUT_ISOLATION.kicad_sch

74LVC1G17GV,125: Ioff; input 0..5.5 V, including VCC=0. Common GND required.
No claim of valid logic below minimum VCC. Existing AON supervisor/clear still governs startup.
ANALOG REMEDIATION: see sheets 5600-6100 and Control 2300-3300; docs/pcb-preparation/signal-remediation.

## 1900_ANALOG_5V.kicad_sch

FB senses ANA5_RAW before R170003.
50 mV/A shunt drop is uncompensated.

## 1900_ANALOG_5V.kicad_sch

Analog 5 V

## 1900_ANALOG_5V.kicad_sch

CMD_ANA5 drives Q170001.
R170005 pulls EN_ANA5 low.
Enable after ANA6 is stable.

## 1900_ANALOG_5V.kicad_sch

PGR_ANA5 is valid only while ANA6 is powered.

## 1900_ANALOG_5V.kicad_sch

Output and protection

## 1900_ANALOG_5V.kicad_sch

Conversion and filtering

## 1900_ANALOG_5V.kicad_sch

C170001 and C170003 (47 uF each) bypass the input and regulated output. C170004
(100 nF) at NR/SS filters reference noise and controls the ramp. SS_CTRL is
grounded, giving about 13 ms nominal soft start. C170002 (10 nF), from OUT to
FB, improves noise and ripple rejection.

## 1900_ANALOG_5V.kicad_sch

Purpose and role

## 1900_ANALOG_5V.kicad_sch

ANA6 -> ANA5 (5.000 V raw)
NR/SS controls the startup ramp.

## 1900_ANALOG_5V.kicad_sch

R170004 (10.5 kOhm) and R170002 (2.00 kOhm) sense ANA5_RAW. V(ANA5_RAW) = 0.8 V x
(1 + R170004 / R170002) = 5.00 V. Increasing R170004 raises the voltage; increasing
R170002 lowers it. For another setpoint, use R170004 = R170002 x (VOUT / 0.8 V -
1).

## 1900_ANALOG_5V.kicad_sch

Low-noise regulation

## 1900_ANALOG_5V.kicad_sch

Output setting and current sense

## 1900_ANALOG_5V.kicad_sch

Low-noise analog supply, 5.00 V before shunt

## 1900_ANALOG_5V.kicad_sch

SHEET GUIDE / Analog 5 V

## 1900_ANALOG_5V.kicad_sch

Enable control

## 1900_ANALOG_5V.kicad_sch

Input and enable

## 1900_ANALOG_5V.kicad_sch

Output voltage setting

## 1900_ANALOG_5V.kicad_sch

U170001 (TPS7A9101) takes power from ANA6. CMD_ANA5 drives Q170001; R170005 (100
kOhm) pulls EN_ANA5 low when Q170001 is off. Enable this stage after ANA6 is
stable. PGR_ANA5 is pulled to AON by R170006 (10 kOhm); qualify its status with
input availability.

## 1900_ANALOG_5V.kicad_sch

R170003 (0.05 Ohm) drops 50 mV/A after feedback: V(ANA5) = 5.00 V - I x 0.05
Ohm. R170001 (10 kOhm) bleeds the output. U170001 has internal current limiting,
UVLO, thermal shutdown and active discharge. Its 1 A rating must cover ANA5
loads and the downstream ANA3V3 stage.

## 1900_ANALOG_5V.kicad_sch

This is the first low-noise stage after the ANA6 switching preregulator. ANA5
supplies MIRA's 5 V analog domain and feeds the ANA3V3 regulator. The LDO
reduces switching ripple reaching the matrix-drive and measurement circuits,
helping preserve DAC and ADC accuracy.

## 2000_ANALOG_3V3.kicad_sch

C170008 and C170006 (47 uF each) bypass the input and regulated output. C170007
(100 nF) at NR/SS filters reference noise and controls the ramp. SS_CTRL is
grounded, giving about 13 ms nominal soft start. C170005 (10 nF), from OUT to
FB, improves noise and ripple rejection.

## 2000_ANALOG_3V3.kicad_sch

R170010 (0.05 Ohm) drops 50 mV/A after feedback: V(ANA3V3) = 3.295 V - I x 0.05
Ohm. R170009 (10 kOhm) bleeds the output. U170002 has internal current limiting,
UVLO, thermal shutdown and active discharge. Usable load current depends on
thermal design and the shared ANA5/ANA6 budget.

## 2000_ANALOG_3V3.kicad_sch

Enable control

## 2000_ANALOG_3V3.kicad_sch

Purpose and role

## 2000_ANALOG_3V3.kicad_sch

FB senses ANA33_RAW before R170010.
50 mV/A shunt drop is uncompensated.

## 2000_ANALOG_3V3.kicad_sch

Output and protection

## 2000_ANALOG_3V3.kicad_sch

Output voltage setting

## 2000_ANALOG_3V3.kicad_sch

Analog 3.3 V

## 2000_ANALOG_3V3.kicad_sch

U170002 (TPS7A9101) takes power from ANA5. CMD_ANA33 drives Q170002; R170012 (100
kOhm) pulls EN_ANA33 low when Q170002 is off. Enable this stage after ANA5 is
stable. PGR_ANA33 is pulled to AON by R170011 (10 kOhm); qualify its status
with input availability.

## 2000_ANALOG_3V3.kicad_sch

R170007 (49.9 kOhm) and R170008 (16.0 kOhm) sense ANA33_RAW. V(ANA33_RAW) = 0.8 V
x (1 + R170007 / R170008) = 3.295 V. Increasing R170007 raises the voltage;
increasing R170008 lowers it. For another setpoint, use R170007 = R170008 x (VOUT /
0.8 V - 1).

## 2000_ANALOG_3V3.kicad_sch

ANA5 -> ANA3V3 (3.295 V raw)
NR/SS controls the startup ramp.

## 2000_ANALOG_3V3.kicad_sch

Low-noise regulation

## 2000_ANALOG_3V3.kicad_sch

CMD_ANA33 drives Q170002.
R170012 pulls EN_ANA33 low.
Enable after ANA5 is stable.

## 2000_ANALOG_3V3.kicad_sch

Output setting and current sense

## 2000_ANALOG_3V3.kicad_sch

Input and enable

## 2000_ANALOG_3V3.kicad_sch

PGR_ANA33 is valid only while ANA5 is powered.

## 2000_ANALOG_3V3.kicad_sch

This is the second stage of MIRA's ANA6 -> ANA5 -> ANA3V3 supply chain.
ANA3V3 provides a low-noise 3.3 V class rail for analog acquisition and
conversion circuits. Cascaded regulation reduces ripple before it reaches the
measurement path; it remains distinct from the digital 3.3 V domains.

## 2000_ANALOG_3V3.kicad_sch

Low-noise analog supply, 3.295 V before shunt

## 2000_ANALOG_3V3.kicad_sch

SHEET GUIDE / Analog 3.3 V

## 2000_ANALOG_3V3.kicad_sch

Conversion and filtering

## 1200_POWER_MONITOR.kicad_sch

L130001 (1 uH) and C130004-C130001 (6 x 47 uF) filter CORE_RAW.
C130012 (100 nF) is the bootstrap capacitor; C130002 (4.7 uF) bypasses VREG5.
R130008 (200 kOhm) / R130003 (10 kOhm) select 400 kHz FCCM and ILIM.
C130005 (22 nF) sets about 2.2 ms soft start. The 8 A IC capability
requires sufficient input power and verified board thermal performance.

## 1200_POWER_MONITOR.kicad_sch

Conversion and filtering

## 1200_POWER_MONITOR.kicad_sch

Mode setting

## 1200_POWER_MONITOR.kicad_sch

CORE1V0 supplies the FPGA internal logic used by the MIRA matrix engine,
precise switching and ADC timing, and fast USB data handling.
It is separate from the FPGA auxiliary and I/O supplies. Generating it
from FPGA5V5 keeps the core in the controlled FPGA power branch.

## 1200_POWER_MONITOR.kicad_sch

FPGA Core 1 V / FPGA core supply

## 1200_POWER_MONITOR.kicad_sch

Output voltage setting

## 1200_POWER_MONITOR.kicad_sch

Output sensing

## 1200_POWER_MONITOR.kicad_sch

R130004 remains a 2 mOhm current shunt; its voltage drop is
inside the positive-sense loop when J230001.17 is connected.
Ground-return drop is NOT compensated: target <=3 mOhm.
PGR_CORE reports regulation at FB, not remote ground.
Verify loop stability, load release and cable faults on prototype.

## 1200_POWER_MONITOR.kicad_sch

1.008 V at positive sense node.
C130005: about 2.2 ms soft start.

## 1200_POWER_MONITOR.kicad_sch

Enable control

## 1200_POWER_MONITOR.kicad_sch

CMD_CORE drives Q130001.
FPGA5V5 must be available.
R130005 pulls EN_CORE low.

## 1200_POWER_MONITOR.kicad_sch

Output and protection

## 1200_POWER_MONITOR.kicad_sch

U130001 (TPS568215RNNR) converts FPGA5V5 into the core supply.
CMD_CORE drives Q130001; R130005 (100 kOhm) pulls EN_CORE low.
The source follower allows enable only with the input rail available;
the command driver must provide a defined state and enough EN margin.
C130007/C130006 (47 uF each) and C130010 (100 nF) bypass the input.

## 1200_POWER_MONITOR.kicad_sch

Input and enable

## 1200_POWER_MONITOR.kicad_sch

FB: CORE_SENSE_P via J230001.17.
Kelvin trace at FPGA; local GND reference.

## 1200_POWER_MONITOR.kicad_sch

R130006 (10.2 kOhm) / R130002 (15 kOhm) regulate CORE_SENSE_P:
V(sense) = 0.6 V x (1 + R130006 / R130002) = 1.008 V.
R130009 (100 Ohm) provides a local path if the sense wire opens:
local no-load nominal becomes 1.012 V. Open sense may cause
undervoltage under load; this fallback is not fault-tolerant OVP.

## 1200_POWER_MONITOR.kicad_sch

200 kOhm / 10 kOhm:
400 kHz, FCCM, ILIM.

## 1200_POWER_MONITOR.kicad_sch

FPGA core supply, positive remote sense

## 1200_POWER_MONITOR.kicad_sch

SHEET GUIDE / FPGA Core 1 V

## 1200_POWER_MONITOR.kicad_sch

Core conversion and filtering

## 1200_POWER_MONITOR.kicad_sch

Purpose and role

## 1200_POWER_MONITOR.kicad_sch

Positive sense: J230001.17 -> J80001.17 -> FPGA CORE decoupling. GND is not remotely sensed.

## 1200_POWER_MONITOR.kicad_sch

R130009 fallback: sense open -> local nominal 1.012 V. Validate loop response before PCB release.

## 2100_PROGRAM_POSITIVE.kicad_sch

Q190004/Q190001 switch P15 to PROG_P15.
R190006 + C190002 slow the output rise.

## 2100_PROGRAM_POSITIVE.kicad_sch

Fast-off gate clamp

## 2100_PROGRAM_POSITIVE.kicad_sch

Output and protection

## 2100_PROGRAM_POSITIVE.kicad_sch

Positive programming supply switch

## 2100_PROGRAM_POSITIVE.kicad_sch

This path provides PROG_P15 to MIRA's bipolar stimulus circuitry for
memristor READ/SET/RESET operations. It connects P15 under hardware
authorization and disconnects the output when permission is removed.
Downstream matrix electronics define stimulus amplitude and pulse timing;
forming uses a separate branch.

## 2100_PROGRAM_POSITIVE.kicad_sch

With permit low, Q190006 ties the pass gates to their common sources.
Q190007 discharges PROG_P15 through R190007 || R190009 = 340 Ohm;
R190008/C190001 give a 10 ms gate RC. The 4.7 uF output decay is about
1.60 ms only after Q190007 turns on. D190004/D190002 protect MOSFET gates;
D190001 clamps negative excursions and R190001 provides residual bleed.
The opposed pass pair blocks reverse current while OFF.

## 2100_PROGRAM_POSITIVE.kicad_sch

Purpose and role

## 2100_PROGRAM_POSITIVE.kicad_sch

Output discharge

## 2100_PROGRAM_POSITIVE.kicad_sch

Output voltage setting

## 2100_PROGRAM_POSITIVE.kicad_sch

Permit LOW: Q190007 discharges PROG_P15.
Q190005 inhibits discharge while permit is HIGH.

## 2100_PROGRAM_POSITIVE.kicad_sch

SHEET GUIDE / Program Positive

## 2100_PROGRAM_POSITIVE.kicad_sch

PROG_P15 follows P15 minus the pass-pair voltage drop while enabled.
The nominal +15 V is set by the upstream supply, not this switch.
R190006/C190002 shape the startup ramp; they do not set output voltage.
D190003 limits pass-pair gate-source voltage to a nominal 10 V.
There is no programmable voltage or current-trip setting here.

## 2100_PROGRAM_POSITIVE.kicad_sch

Input and enable

## 2100_PROGRAM_POSITIVE.kicad_sch

Hardware permit driver

## 2100_PROGRAM_POSITIVE.kicad_sch

Program Positive

## 2100_PROGRAM_POSITIVE.kicad_sch

Q190004/Q190001 are an opposed, common-source PMOS pair. R190006 and
C190002 (47 nF) slow turn-on; R190002 (680 Ohm) isolates the Miller
capacitor during fast transitions. C190003 (4.7 uF) bypasses the output
and R190010 (1 MOhm) provides backup gate-source bias.
No voltage conversion takes place on this sheet.

## 2100_PROGRAM_POSITIVE.kicad_sch

Q190002 sinks U190001 and U200002-U200001 LED currents.
R190004 defines permit LOW if released.

## 2100_PROGRAM_POSITIVE.kicad_sch

MATRIX_PERMIT drives Q190003, Q190002 and Q190005. Q190003 pulls the pass gates down
through R190006 (330 kOhm). Q190002 sinks U190001 and U200002-U200001 LED currents
through MATRIX_OPTO_K; R190003 (300 Ohm) feeds the local LED from AON. U190001
inhibits the OFF clamp; Q190005 inhibits discharge. R190004 (100 kOhm) pulls
permit LOW if its driver is released.

## 2100_PROGRAM_POSITIVE.kicad_sch

Conversion and filtering

## 2100_PROGRAM_POSITIVE.kicad_sch

Pass pair and controlled turn-on

## 2100_PROGRAM_POSITIVE.kicad_sch

LED off: Q190006 ties pass G-S together.
U190001 inhibits the clamp while permitted.

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

Host status and UART transmit
SYS3V3-powered outputs

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

Host UART receive to U290002
Series resistor and local pull-down

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

PM debug access
AON reference; SWD and PM reset

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

This sheet links the AON power manager to the STM32H745
application controller. It carries UART, permits, rail status
and a watchdog heartbeat, and provides SWD access to STM32G0B1.
The separate VTT monitor checks the DDR termination supply.

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

Partial power down
Outputs high impedance if SYS3V3 is OFF

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

J420001 provides AON reference, GND, SWDIO, SWCLK and PM reset.
J420002 provides SYS3V3 reference, GND, UART in both directions,
HOST_WDI and three buffered status signals. The reference pins
are connected to board rails; external tools must only sense
them.

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

SHEET GUIDE / PM Debug and Host

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

U420001 buffers PM_UART_TX, MATRIX_PERMIT, ALL_RAILS_PG and
GLOBAL_PWR_PERMIT into the SYS3V3 host domain. All enables are
LOW. Host TX reaches U290002 through R420003; R420002 holds the raw
input LOW when undriven. R420007 holds PM transmit idle HIGH.

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

VTT monitor
1 kOhm / 10 nF; rail clamps

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

Protection and fault response

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

Inputs and outputs

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

PM Debug and Host

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

Power manager debug and host interface

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

SWDIO / SWCLK use 33 Ohm series resistors; SWCLK has a 100 kOhm
pull-down. R420005 / C420002 filter ADC_VTT with a nominal 10 us
time constant. The host must send falling HOST_WDI edges within
the watchdog interval set on sheet 2500.

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

Purpose and role

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

Control logic

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

Timing and settings

## 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch

D420001 is downstream of the VTT isolation switch; see sheet 5700. U420001
supports partial power down; its outputs become high impedance
when SYS3V3 is OFF. Host reset is routed separately from J420002.
UART LOW during host power loss must be handled by firmware.

## 5000_DISTRIBUTED_DIGITAL_POWER.kicad_sch

Distributed digital power: Power below / Control above

## 5000_DISTRIBUTED_DIGITAL_POWER.kicad_sch

12 mm facing-surface gap. Sockets: Power F.Cu; headers: Control B.Cu. Place by consumer zone, not by schematic coordinates.

## 5000_DISTRIBUTED_DIGITAL_POWER.kicad_sch

J230001 <-> J80001 | FPGA

## 5000_DISTRIBUTED_DIGITAL_POWER.kicad_sch

J230002 <-> J80002 | DDR

## 5000_DISTRIBUTED_DIGITAL_POWER.kicad_sch

J230003 <-> J80003 | MCU

## 5000_DISTRIBUTED_DIGITAL_POWER.kicad_sch

J230004 <-> J80004 | USB

## 5000_DISTRIBUTED_DIGITAL_POWER.kicad_sch

J230005 <-> J160001 | ETHERNET

## 5000_DISTRIBUTED_DIGITAL_POWER.kicad_sch

FPGA J230001 / J80001:
Odd 1..15: eight CORE force contacts.
17: positive sense; route separately to FPGA.
19,21: AUX1V8. 23,25: IO3V3.
Every even pin: GND.

DDR VREF: keep quiet beside GND.
VTT must source and sink near termination.
Place Power converters below their zones.
Coordinate and height tolerances need checking.

## 6000_FPGA_AUX_IO_INTERLOCK.kicad_sch

FPGA Aux Interlock

## 6000_FPGA_AUX_IO_INTERLOCK.kicad_sch

EN_IO33_QUAL = EN_IO33 AND PGR_AUX18 AND EN_AUX18.
PG alone is insufficient: TPS62130 PG is high impedance while disabled.
R370002 discharges IO3V3 even if the processor or PM firmware has stopped.
At C_IO <= 1 mF, 1k reduces 3.465 V to 2.625 V in < 0.28 s, plus relay delay.
Verify the fitted bulk capacitance and ramp timing against AMD DS181 before board sign-off.

## 3100_PM_COMMAND_READY.kicad_sch

All fifteen CMD signals are required.

## 3100_PM_COMMAND_READY.kicad_sch

Final AND stage

## 3100_PM_COMMAND_READY.kicad_sch

Protection and fault response

## 3100_PM_COMMAND_READY.kicad_sch

Four local groups -> ALL_COMMANDS_ON

## 3100_PM_COMMAND_READY.kicad_sch

Enable-command readiness

## 3100_PM_COMMAND_READY.kicad_sch

U400002 combines USB/SYS/FPGA/ANA and P15/N15/CORE/AUX18 commands. U400003 combines
AUX25/IO33/DDR/IO18 and VTT/ANA5/ANA33 commands. AON fixes the unused fourth
group input HIGH. U400001 ANDs all four local groups; all fifteen commands must be
HIGH.

## 3100_PM_COMMAND_READY.kicad_sch

Inputs and outputs

## 3100_PM_COMMAND_READY.kicad_sch

The inputs are CMD_SYS, CMD_FPGA, CMD_ANA, CMD_P15, CMD_N15 and nine
secondary-rail CMD signals. ALL_COMMANDS_ON is active HIGH and feeds the permit
logic. U400002-U400001 use AON; C400002-C400001 provide 100 nF bypassing.

## 3100_PM_COMMAND_READY.kicad_sch

The circuit is a live, two-stage AND tree with Schmitt inputs. It contains no
startup delay or command memory. The unused U400001 gate inputs are tied to GND
and its output is unconnected. Rail sequencing and the times between commands
are set by the power controller.

## 3100_PM_COMMAND_READY.kicad_sch

Control logic

## 3100_PM_COMMAND_READY.kicad_sch

Command state must also pass measured rail readiness.

## 3100_PM_COMMAND_READY.kicad_sch

Timing and settings

## 3100_PM_COMMAND_READY.kicad_sch

Combined enable-command logic

## 3100_PM_COMMAND_READY.kicad_sch

Any command going LOW deasserts ALL_COMMANDS_ON and removes one matrix-enable
condition. This output cannot confirm voltage, current or pulse quality;
physical rail status and the other hardware interlocks remain required. An
intentionally disabled included rail also prevents the aggregate.

## 3100_PM_COMMAND_READY.kicad_sch

Command Ready

## 3100_PM_COMMAND_READY.kicad_sch

Purpose and role

## 3100_PM_COMMAND_READY.kicad_sch

This block confirms that all MIRA rail-enable commands are asserted.
ALL_COMMANDS_ON supplies the command-side condition of the matrix interlock. The
separate ALL_RAILS_PG signal supplies measured readiness, so the interlock
checks both intended power state and actual supply status.

## 3100_PM_COMMAND_READY.kicad_sch

SHEET GUIDE / Command Ready

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

Analog 5 V supply; feeds ANA3V3

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

R160006: 20 mOhm; 0.4 V/A; OC 2 A.

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

Protection and fault response

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

R170010: 50 mOhm; 1 V/A; OC 0.8 A.

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

U480003-U480002 sense DDR_RAW/DDR1V35, ANA5_RAW/ANA5,
IO18_RAW/IO1V8 and ANA33_RAW/ANA3V3 across upstream shunts.
MON_I_* outputs report forward current; MON_V_* outputs report half
the post-shunt rail voltage. AON supplies all four monitors.

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

DDR: 10 mOhm, gain 50, 0.500 V/A, R480015 13.7k -> 2.192 A. Other rails on this sheet use gain 20.

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

USB and converter I/O 1.8 V core supply

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

BAT54S clamps each voltage node to GND and AON; 10 kOhm resistors
limit the injected current. ANA5 current includes the downstream ANA3V3
load. These monitors report faults; they do not interrupt power locally.
Qualify all readings with AON availability and the commanded rail state.

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

DDR: 10 mOhm, gain 50, 0.500 V/A, R480015 13.7k -> 2.192 A. Other rails on this sheet use gain 20.

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

Purpose and role

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

Inputs and outputs

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

SHEET GUIDE / DDR and Analog Sense

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

DDR, IO18 and analog rail monitoring

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

DDR 1.35 V memory supply

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

Timing and settings

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

Analog 3.3 V conversion supply

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

DDR: 10 mOhm, gain 50, 0.500 V/A, R480015 13.7k -> 2.192 A. Other rails on this sheet use gain 20.

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

This sheet supervises DDR1V35, IO1V8, ANA5 and ANA3V3. These rails
support MIRA's memory, USB interface and analog conversion circuits.
Load-side voltage and current telemetry lets the power manager verify
startup and diagnose faults in the digital and low-noise analog branches.

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

R170003: 50 mOhm; 1 V/A; OC 0.8 A.

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

Control logic

## 3800_MONITOR_DDR_IO_ANALOG.kicad_sch

DDR and Analog Sense

## 2400_PM_CONTROLLER.kicad_sch

Timing and settings

## 2400_PM_CONTROLLER.kicad_sch

Protection and fault response

## 2400_PM_CONTROLLER.kicad_sch

Control logic

## 2400_PM_CONTROLLER.kicad_sch

PM_RESET_N combines AON reset and the PM watchdog fault.
Hardware permits qualify enable requests independently of code.
Firmware must initialize requests safely, verify ready signals,
and arm the matrix only after supplies and host status are valid.

## 2400_PM_CONTROLLER.kicad_sch

SHEET GUIDE / Power Manager MCU

## 2400_PM_CONTROLLER.kicad_sch

PWR_ARM_PULSE and MATRIX_ARM_PULSE clock the permit latches.
GLOBAL_PWR_PERMIT and MATRIX_PERMIT are status inputs.
PWR_KILL_GPIO and MATRIX_KILL_GPIO request hardware shutdown.
PM_UART_TX / RX use USART3 on PD8 / PD9, alternate function 0.

## 2400_PM_CONTROLLER.kicad_sch

Requests startup; hardware latches retain the permits.
Matrix timing and neural computation are handled elsewhere.

## 2400_PM_CONTROLLER.kicad_sch

PC14: GLOBAL_CLEAR_N; PC15: LINK_READY_H. Inputs, no pull; LSE OFF.
Wait for CLEAR before PWR_ARM; LINK_READY before MATRIX_ARM.
Read HOST_ALIVE_PM as a heartbeat; verify both permit outputs.

## 2400_PM_CONTROLLER.kicad_sch

Power management controller

## 2400_PM_CONTROLLER.kicad_sch

Purpose and role

## 2400_PM_CONTROLLER.kicad_sch

AON is also the ADC reference.
Keep the internal VREFBUF output disabled.

## 2400_PM_CONTROLLER.kicad_sch

Inputs and outputs

## 2400_PM_CONTROLLER.kicad_sch

AON-powered rail sequencer

## 2400_PM_CONTROLLER.kicad_sch

Wait for PC14 CLEAR before PWR_ARM; PC15 LINK_READY before MATRIX_ARM.
Service PM_WDI throughout startup and shutdown.
Use internal clocking; PF0, PC14 and PC15 are GPIO, not HSE/LSE.
See docs/pcb-preparation/sequencing/README.md for rail order.

## 2400_PM_CONTROLLER.kicad_sch

EN_REQ_* requests the individual converter enables.
PG_*, PGR_* and ALL_RAILS_PG report supply readiness.
PA0 / PA1 / PA2 / PA3 measure current, voltage, VTT and PROG_P15.
MUX_A0..A3 select telemetry channels; MUX_DISABLE gates the mux.

## 2400_PM_CONTROLLER.kicad_sch

Power Manager MCU

## 2400_PM_CONTROLLER.kicad_sch

AON supply and local decoupling

## 2400_PM_CONTROLLER.kicad_sch

U260001 is the dedicated STM32G0B1 power sequencer for MIRA.
It remains active on AON while the switched rails are disabled,
so it can coordinate startup, monitor supplies and handle faults.
The FPGA controls matrix timing; STM32H745 runs neuron models.

## 5900_VIN_REFERENCED_ENABLES.kicad_sch

VIN Enables 2

## 5900_VIN_REFERENCED_ENABLES.kicad_sch

LED driver is in AON; the relay contact sources EN only from the converter VIN.
VIN=0 therefore cannot receive an AON logic HIGH. 22k holds EN LOW with relay open.
Budget +100 mA AON for ten LEDs (worst corner); reserve 3 ms each for enable/disable propagation.
Matrix clear remains direct hardware; optical relay latency applies to rail shutdown only.

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

Inputs and outputs

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

Timing and settings

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

BAT54S diode pairs clamp voltage nodes toward GND and AON. The P15 divider
provides normal-range headroom without continuous clamp current. Alert response
bypasses the telemetry filters; actual shutdown also depends on the interlocks
and power switches.

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

Current scales are FPGA 0.2 V/A, ANA 1 V/A and P15 2 V/A. The 10k / 10k / 30.1k LIMIT
resistors set nominal trips of 4 A, 0.8 A and 1.204 A. FPGA and ANA voltage
dividers use 1/2; R460006/R460012 use 47 kOhm / 10 kOhm for P15/5.7, giving 2.63 V
at 15 V. Current filters have a 10 us time constant.

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

Positive AFE rail monitor

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

Protection and fault response

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

Primary Rail Sense

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

0.1 Ohm: 2 V/A. Nominal trip 1.204 A.

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

FPGA, analog and positive AFE monitoring

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

0.01 Ohm: 0.2 V/A. Nominal trip 4 A.

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

Analog preregulator monitor

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

The INA301 ALERT outputs share OC_OK_N and pull it low on an overcurrent.
Grounded RESET pins select transparent mode. The interlock sheet stores faults
and removes supply permits; telemetry polling is not required for the hardware
alert.

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

P15 voltage scale
47 kOhm / 10 kOhm: 15 V -> 2.63 V
Also feeds hardware power-good.

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

0.05 Ohm: 1 V/A. Nominal trip 0.8 A.

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

Control logic

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

SHEET GUIDE / Primary Rail Sense

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

These channels monitor the FPGA intermediate supply, the analog preregulator and
the positive AFE supply. MIRA uses their telemetry to track rail loading during
startup and operation; the analog voltage signals also qualify hardware
readiness.

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

FPGA intermediate rail monitor

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

U460003-U460001 sense FPGA_RAW/FPGA5V5, ANA_RAW/ANA6 and P15_RAW/P15 across the
upstream shunts. MON_I_* and MON_V_* feed the telemetry multiplexers. MON_V_ANA6
and MON_V_P15 also feed the analog power-good sheet. AON powers all three
monitors.

## 3600_MONITOR_FPGA_ANA_AFE.kicad_sch

Purpose and role

## 5300_PM_STARTUP_OUTPUTS.kicad_sch

5300  DEFAULT-OFF STARTUP OUTPUTS

## 5300_PM_STARTUP_OUTPUTS.kicad_sch

OUTPUT CONTRACT
OE=0: outputs high impedance;
pull-downs define the disabled state.
OE=1: outputs follow the raw commands.

VTT
CMD_VTT now drives EN_VTT directly
through R150011 (0R). No VGS loss.

MATRIX
Only the buffered MATRIX_PERMIT
drives the switches and interface.
MATRIX_KILL_H on J310003 is a raw
latch diagnostic; valid after AON ready.

PLACEMENT
Put each bypass capacitor at VCC.
Keep OE and command traces short.
Route STARTUP_RESET_N locally
between U300001 and U300002.

STATUS
Schematic repair; board routing and
ramp/brownout measurements pending.

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

This sheet lets the MIRA power manager scan voltage and current for 16 supply
domains. The paired selectors reduce 32 monitor signals to two ADC paths for
startup checks, load tracking and fault diagnostics.

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

The selectors carry conditioned monitor signals within GND..AON. Upstream
dividers and clamps provide signal protection. Disabled or unpowered selectors
do not provide valid telemetry; dedicated hardware fault logic acts separately.

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

Control logic

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

Timing and settings

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

Telemetry Selectors

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

Voltage monitor selection
U520001 / same channel order

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

Both CD74HC4067 devices share MUX_A0..MUX_A3 and MUX_DISABLE. A0 is the least
significant bit: channel = A0 + 2*A1 + 4*A2 + 8*A3. LOW on MUX_DISABLE connects
the selected pair; HIGH disconnects both.

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

Current monitor selection
U520002 / 16 supply domains

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

Purpose and role

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

Inputs and outputs

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

Protection and fault response

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

SHEET GUIDE / Telemetry Selectors

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

Voltage and current telemetry multiplexers

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

U520002 selects MON_I_* current signals; U520001 selects matching MON_V_* voltage
signals. Their outputs, MUX_I_COM and MUX_V_COM, feed the ADC buffers. Channel
order runs from INPUT and AON to ANA5 and ANA33.

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

Shared address
A0 is the LSB
HIGH disables both

## 3900_TELEMETRY_MULTIPLEXERS.kicad_sch

C520001 and C520002 bypass the AON supply with 100 nF each. Firmware should disable
the selectors, change the address, enable them and allow the source, buffer and
ADC to settle before accepting either sample.

## 1100_AFE_NEGATIVE_15V.kicad_sch

N15: isolated module output referenced to system GND; +VOUT = GND, -VOUT = N15_RAW.

## 1100_AFE_NEGATIVE_15V.kicad_sch

CMD_N15 high enables the module via Q110001. R110003 pulls the gate low. An open remote pin is OFF.

## 1100_AFE_NEGATIVE_15V.kicad_sch

TRIM open. Use the negative-logic, no-bus model ECB40W18-72S15N.

## 1100_AFE_NEGATIVE_15V.kicad_sch

System trip about 1.29 A. Use separate Kelvin traces to the shunt.

## 1100_AFE_NEGATIVE_15V.kicad_sch

Module body 50.8 x 25.4 x 12.7 mm. Verify thermal clearance.

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

SHEET GUIDE / Negative Overcurrent

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

Control logic

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

Negative rail overcurrent comparator

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

U410001 is powered from AON. OC_I_N15 must be a conditioned,
positive current-sense voltage within the AON input range.
OC_OK_N feeds the permit interlock and the power controller.

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

Threshold reference
VREF = AON / 2.37

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

R410003/R410002 = 2.74k/10k. Trip = AON x 10/12.74 / (20 x 0.1 ohm), about 1.29 A at AON = 3.28 V.

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

Timing and settings

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

R410003/R410002 = 2.74k/10k. Trip = AON x 10/12.74 / (20 x 0.1 ohm), about 1.29 A at AON = 3.28 V.

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

Current-sense input
Conditioned 0...AON signal only

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

Inputs and outputs

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

Unused comparator channels
Inputs fixed; outputs disconnected

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

HIGH = healthy
LOW = fault

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

Negative Overcurrent

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

Protection and fault response

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

This hardware comparator checks the negative AFE rail current.
It can clear the power permit latch without waiting for STM32G0B1
firmware, protecting the supplies used by the matrix drivers.

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

Purpose and role

## 3200_PM_NEGATIVE_OVERCURRENT.kicad_sch

Channel 1 compares OC_I_N15 at IN1- with the reference at IN1+.
Above the threshold, the open-collector output pulls OC_OK_N LOW.
R410001 (10 kOhm) pulls the released output HIGH. The other three
channels have fixed inputs and disconnected outputs.

## 5100_DISTRIBUTED_ANALOG_POWER.kicad_sch

Distributed analog power: Power below / Control above

## 5100_DISTRIBUTED_ANALOG_POWER.kicad_sch

12 mm facing-surface gap. Sockets: Power F.Cu; headers: Control B.Cu. Place by consumer zone, not by schematic coordinates.

## 5100_DISTRIBUTED_ANALOG_POWER.kicad_sch

J240001 <-> J90001 | DAC_MATRIX

## 5100_DISTRIBUTED_ANALOG_POWER.kicad_sch

J240002 <-> J90002 | ADC_AFE

## 5100_DISTRIBUTED_ANALOG_POWER.kicad_sch

DAC_MATRIX: place near DAC buffers and matrix power entry.
PROG_P15 / PROG_N15 remain switched supplies for the forming source.
ADC_AFE: place beside the TIA / ADC / reference power filters.

Repeated rail names are the same protected source, with multiple entry points.
Keep a continuous GND plane; local returns must not cross the FPGA/DDR load path.
Route quiet analog supply branches from the proper post-regulator/post-shunt output.
No connector-level isolation or independent zone protection is implied.

This sheet defines the electrical interface, not final XY placement or qualified current.
See docs/pcb-preparation/distributed-power for pinout, budgets and placement requirements.

## 6100_AON_MONITOR_ENABLE_BUFFER.kicad_sch

Monitor Enable Buffer

## 6100_AON_MONITOR_ENABLE_BUFFER.kicad_sch

U510001 keeps the 15 analog-switch SEL loads off the low-current AUP startup buffer.
STARTUP_READY_H adds one LVC input only: worst static load 18 uA < 20 uA.
Existing startup/reset topology and no-automatic-rearm behavior are preserved.

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

Enable control

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

Output voltage setting

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

Output and protection

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

Purpose and role

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

Buck stage

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

R90002/R90005: 6.00 V before R90004.
R90004 causes a 50 mV/A drop.

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

R90002 (130 kOhm) and R90005 (20 kOhm) set ANA_RAW:
VRAW = 0.8 V x (1 + R90002/R90005) = 6.00 V.
To change the voltage: R90002 = R90005 x (VRAW/0.8 V - 1). Increasing the upper
resistor raises VRAW.

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

SHEET GUIDE / Analog 6 V

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

Output setting

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

Conversion and filtering

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

400 kHz / PFM

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

Input and enable

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

R90004 (0.05 Ohm) causes a 50 mV/A drop: ANA6 is about 5.95 V at 1 A. Feedback
is before the shunt. U90001 is a 1 A IC with internal current, short-circuit
and thermal protection. D90001 indicates rail presence; R90004 does not set the
current limit.

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

CMD_ANA drives Q90001 as a source follower.
R90003 pulls EN low when Q90001 is off.
The command must have a defined level.

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

Generates ANA6 from BUS24 as an intermediate supply for downstream low-noise
analog LDO stages. CMD_ANA controls whether this supply is enabled.

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

U90001 operates at 400 kHz with PFM at light load. L90001 (33 uH) and C90001/C90005
(47 uF each) filter ANA_RAW. C90002/C90004 bypass the input; C90003 (100 nF) is the
CB-to-SW bootstrap capacitor.

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

Analog 6 V

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

Analog preregulator, 6.00 V before shunt

## 900_ANALOG_PREREGULATOR_6V.kicad_sch

BUS24 feeds U90001 (LMR51610XDBVR). CMD_ANA drives Q90001 as an active-high
source follower. R90003 (100 kOhm) pulls EN_ANA low when Q90001 is off. The
command must not float; verify its high-level margin.

## 1000_AFE_POSITIVE_15V.kicad_sch

400 kHz FPWM, 47 uH. Three 10 uF / 50 V ceramics and 100 uF bulk at P15_RAW.

## 1000_AFE_POSITIVE_15V.kicad_sch

Output voltage setting

## 1000_AFE_POSITIVE_15V.kicad_sch

Buck stage

## 1000_AFE_POSITIVE_15V.kicad_sch

Conversion and filtering

## 1000_AFE_POSITIVE_15V.kicad_sch

Generates P15 from BUS24 for the positive AFE supply. CMD_P15 controls
whether this rail is enabled. The nominal pre-shunt voltage is approximately
+15 V.

## 1000_AFE_POSITIVE_15V.kicad_sch

BUS24 feeds U100001. The VIN-domain enable switch on sheet 5800 drives EN_P15_VIN.

## 1000_AFE_POSITIVE_15V.kicad_sch

Output setting

## 1000_AFE_POSITIVE_15V.kicad_sch

SHEET GUIDE / AFE +15 V

## 1000_AFE_POSITIVE_15V.kicad_sch

AFE positive supply, +14.99 V before shunt

## 1000_AFE_POSITIVE_15V.kicad_sch

100k / 7.15k gives 14.986 V at P15_RAW.

## 1000_AFE_POSITIVE_15V.kicad_sch

Input and enable

## 1000_AFE_POSITIVE_15V.kicad_sch

400 kHz / FPWM

## 1000_AFE_POSITIVE_15V.kicad_sch

Output and protection

## 1000_AFE_POSITIVE_15V.kicad_sch

R100002: 0.1 ohm, 1 W, Kelvin sense. External trip 1.204 A nominal.

## 1000_AFE_POSITIVE_15V.kicad_sch

14.99 V before the shunt; drop 100 mV/A.

## 1000_AFE_POSITIVE_15V.kicad_sch

Enable control

## 1000_AFE_POSITIVE_15V.kicad_sch

Purpose and role

## 1000_AFE_POSITIVE_15V.kicad_sch

AFE +15 V

## 1000_AFE_POSITIVE_15V.kicad_sch

EN_P15_VIN follows the hardware-isolated P15 command.

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

Control logic

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

Current scales: input 0.4 V/A with the stated external 0.02 Ohm shunt; AON 2
V/A; USB 1 V/A; SYS 0.2 V/A. The 10 kOhm LIMIT resistors set 0.8 V, giving
nominal trips of 0.4 A, 0.8 A and 4 A. Voltage scales are input/16 and other
rails/2. Each 1 kOhm / 10 nF current filter has a 10 us time constant.

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

0.1 Ohm: 2 V/A. Nominal trip 0.4 A.

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

The BAT54S pairs clamp voltage nodes toward GND and AON. Telemetry filters do
not delay the INA301 internal comparator. OC_OK_N uses external AON pullups on
the ADC-buffer and negative-overcurrent sheets; trip settings must be checked
against load and inrush budgets.

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

Inputs and outputs

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

AON rail monitor

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

System rail monitor

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

0.01 Ohm: 0.2 V/A. Nominal trip 4 A.

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

These four channels let the MIRA power controller monitor the protected input
bus and the AON, USB and system rails. Current alerts also feed the hardware
interlocks, allowing switched supplies to be disabled without waiting for
firmware.

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

Input bus monitor

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

SHEET GUIDE / Input and System Sense

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

Purpose and role

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

U450003 senses BUS24_PRE_SHUNT to BUS24. U450004-U450002 sense AON_RAW/AON,
USB_RAW/USB5 and SYS_RAW/SYS3V3. MON_I_* and MON_V_* feed the telemetry
multiplexers; MON_V_USB also feeds the analog power-good comparator. All
monitors use AON and GND.

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

Protection and fault response

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

Input, AON, USB and system monitoring

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

USB rail monitor

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

Input and System Sense

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

INA301 ALERT outputs share OC_OK_N: a low level signals an overcurrent. RESET is
grounded, selecting transparent mode; fault memory is on the interlock sheet.
U450003 provides input-current telemetry without a hardware alert.

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

0.05 Ohm: 1 V/A. Nominal trip 0.8 A.

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

Timing and settings

## 3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch

External 0.02 Ohm: 0.4 V/A. Voltage divided by 16.

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

Negative rail voltage and current monitor

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

N15_RAW is the converter output before the 0.1 Ohm shunt R110001.
N15 is the delivered rail after that shunt. U440001 uses AON and
N15_RAW as its supply rails. Channel A measures the shunt drop;
channel B scales N15. The outputs are referenced to system GND.

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

Inputs and outputs

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

Purpose and role

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

Negative voltage scaling
MON_V_N15 = -0.1 x N15; -15 V gives +1.50 V.
This measures rail voltage, not programming pulses.

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

Control logic

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

SHEET GUIDE / Negative Rail Sense

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

Channel B gives MON_V_N15 = -0.1 x N15: -15 V becomes +1.50 V.
Each telemetry branch uses 10 kOhm and 100 nF: tau = 1.0 ms.
With the 3200 threshold AON/5.7, the nominal trip is 0.288 A
at AON = 3.28 V. Preserve the four 0.1% gain-network resistors.

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

Negative current sensing
20 x (N15 - N15_RAW); 2.0 V/A with R110001 = 0.1 Ohm.
OC_I_N15 bypasses the telemetry RC filter.

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

Negative Rail Sense

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

Protection and fault response

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

D440001-D440002 clamp the signal nodes toward GND and AON;
series resistors limit sustained clamp current. This sheet senses
conditions; the comparator and interlock sheets disconnect power.
Threshold accuracy needs an error budget. Treat rail transitions
and AON loss as invalid telemetry states until supplies settle.

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

The monitor has no enable or permit input. Channel A produces
20 x (N15 - N15_RAW), or nominally 2.0 V/A of return current.
OC_I_N15 reaches the comparator through R440004 without the
telemetry capacitor. MON_I_N15 uses a separate filtered branch.

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

Timing and settings

## 3400_NEGATIVE_RAIL_MONITOR.kicad_sch

U440001 monitors the negative AFE supply used by MIRA matrix drivers.
It translates the rail voltage and shunt drop into positive signals.
MON_I_N15 and MON_V_N15 feed power-controller telemetry;
OC_I_N15 feeds the independent hardware overcurrent comparator.

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

BAT54S clamps each voltage node to GND and AON; 10 kOhm resistors
limit the injected current. The current-output RC does not delay the
internal overcurrent comparator. These monitors report faults; they do
not interrupt power locally. Qualify all readings with AON availability.

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

Inputs and outputs

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

Timing and settings

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

Control logic

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

FPGA 2.5 V auxiliary domain

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

FPGA 3.3 V I/O domain

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

U470001-U470002 sense CORE_RAW/CORE1V0, AUX18_RAW/AUX1V8,
AUX25_RAW/AUX2V5 and IO33_RAW/IO3V3 across upstream shunts.
MON_I_* outputs report forward current; MON_V_* outputs report half
the post-shunt rail voltage. AON supplies all four monitors.

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

SHEET GUIDE / FPGA Rail Sense

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

R140010: 20 mOhm; 0.4 V/A; OC 2 A.

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

CORE: 2 mOhm, gain 50, 0.100 V/A, R470012 7.50k -> 6.00 A. Other rails on this sheet use gain 20.

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

FPGA core, auxiliary and I/O monitoring

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

FPGA Rail Sense

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

R140015: 20 mOhm; 0.4 V/A; OC 2 A.

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

Protection and fault response

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

This sheet supervises the FPGA core, 1.8 V and 2.5 V auxiliary domains
and the 3.3 V I/O supply. These domains support MIRA's matrix timing,
ADC capture and host data path. Current and load-side voltage telemetry
lets the power manager check startup and diagnose domain faults.

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

FPGA 1.8 V auxiliary domain

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

R140005: 20 mOhm; 0.4 V/A; OC 2 A.

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

CORE: 2 mOhm, gain 50, 0.100 V/A, R470012 7.50k -> 6.00 A. Other rails on this sheet use gain 20.

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

Purpose and role

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

FPGA core: matrix timing and data engine

## 3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch

CORE: 2 mOhm, gain 50, 0.100 V/A, R470012 7.50k -> 6.00 A. Other rails on this sheet use gain 20.

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

R530003/C530002 and R530005/C530001 each use 100 Ohm and 1 nF: nominal RC = 0.10 us.
These resistors isolate the buffer from ADC capacitance. ADC acquisition time
and channel-switch delay must include amplifier and source settling.

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

Purpose and role

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

Timing and settings

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

MUX defaults OFF
OC_OK_N: 10k pull-up

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

Inputs and outputs

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

SHEET GUIDE / Telemetry ADC Buffers

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

Protection and fault response

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

Control logic

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

U530001 channel A follows MUX_I_COM and drives ADC_I; channel B follows MUX_V_COM
and drives ADC_V. The controller receives ADC_I on PA0/ADC_IN0 and ADC_V on
PA1/ADC_IN1. U530001 and C530003 use AON and GND.

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

Telemetry ADC buffers and default states

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

This sheet drives the power-manager ADC from the selected MIRA supply monitors.
Two unity-gain buffers keep ADC sampling current out of the high-impedance
telemetry sources and preserve the current/voltage channel pairing.

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

Current and voltage buffers
PA0 = ADC_I; PA1 = ADC_V

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

Telemetry ADC Buffers

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

R530008..R530006 hold MUX_A0..MUX_A3 LOW when the controller releases them. R530001
pulls MUX_DISABLE HIGH, keeping both selectors disconnected by default. R530002
pulls the shared open-drain OC_OK_N signal up to AON.

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

Feedback returns directly to each amplifier output before the 100 Ohm resistor.
Input protection is upstream; the buffers do not add a clamp. Samples require
valid AON and enabled selectors. OC_OK_N is a separate hardware fault path.

## 4000_TELEMETRY_ADC_BUFFERS.kicad_sch

Address defaults
A0..A3 = LOW

## 5800_VIN_REFERENCED_ENABLES.kicad_sch

VIN Enables 1

## 5800_VIN_REFERENCED_ENABLES.kicad_sch

LED driver is in AON; the relay contact sources EN only from the converter VIN.
VIN=0 therefore cannot receive an AON logic HIGH. 22k holds EN LOW with relay open.
Budget +100 mA AON for ten LEDs (worst corner); reserve 3 ms each for enable/disable propagation.
Matrix clear remains direct hardware; optical relay latency applies to rail shutdown only.

## 1300_FPGA_AUX_1V8.kicad_sch

Output and protection

## 1300_FPGA_AUX_1V8.kicad_sch

SHEET GUIDE / FPGA Aux 1.8 V

## 1300_FPGA_AUX_1V8.kicad_sch

R140005 (0.02 Ohm) drops 20 mV/A outside feedback. At 3 A, AUX1V8 is about 1.74
V. R140002 (10 kOhm) bleeds the output. PGR_AUX18 is open drain, pulled to AON
by R140006 (10 kOhm); use its RAW status only with FPGA5V5 present. The IC
supports up to 3 A, subject to thermal and shared-input limits. Current and
thermal protection are internal.

## 1300_FPGA_AUX_1V8.kicad_sch

FPGA Aux 1.8 V

## 1300_FPGA_AUX_1V8.kicad_sch

FPGA auxiliary supply, 1.8 V

## 1300_FPGA_AUX_1V8.kicad_sch

CMD_AUX18 drives Q140001; R140003 pulls EN low.

## 1300_FPGA_AUX_1V8.kicad_sch

Output sensing

## 1300_FPGA_AUX_1V8.kicad_sch

Output voltage setting

## 1300_FPGA_AUX_1V8.kicad_sch

Input and enable

## 1300_FPGA_AUX_1V8.kicad_sch

Purpose and role

## 1300_FPGA_AUX_1V8.kicad_sch

Conversion and filtering

## 1300_FPGA_AUX_1V8.kicad_sch

This converter supplies the 1.8 V auxiliary domain of MIRA's FPGA subsystem.
The FPGA coordinates memristor-matrix timing, receives ADC data and handles
fast host links. Separate enable and status signals let the power manager
sequence this domain with the other FPGA supplies.

## 1300_FPGA_AUX_1V8.kicad_sch

FPGA5V5 -> AUX18_RAW; L140001 + C140001 filter the output.
VOS and feedback sense RAW before R140005.

## 1300_FPGA_AUX_1V8.kicad_sch

RAW: 1.8 V nominal; shunt: 20 mV/A.
PGR_AUX18: RAW status, pulled up to AON.

## 1300_FPGA_AUX_1V8.kicad_sch

R140001 (20 kOhm) and R140004 (16 kOhm) set the RAW voltage:
V(AUX18_RAW)=0.8 V x (1+R140001/R140004) = 1.8 V.
To change it: R140001 = R140004 x (VRAW / 0.8 V - 1). Increasing R140001 raises the
voltage. DEF is grounded; the +5% margin is disabled.

## 1300_FPGA_AUX_1V8.kicad_sch

Buck conversion and filtering

## 1300_FPGA_AUX_1V8.kicad_sch

U140001 (TPS62130A) receives FPGA5V5 at AVIN and both PVIN pins. C140004 (10 uF)
and C140003 (100 nF) bypass the input. CMD_AUX18 drives Q140001; a high command
enables EN_AUX18. R140003 (100 kOhm) pulls EN low when Q140001 is off. FPGA5V5
must be available first.

## 1300_FPGA_AUX_1V8.kicad_sch

L140001 (2.2 uH) and C140001 (47 uF nominal) filter the switched output. VOS
senses AUX18_RAW; FSW tied to RAW selects the approximately 1.25 MHz mode as
RAW rises. Power-save operation is automatic at light load. C140002 (10 nF) on
SS/TR gives an approximately 5 ms ramp.

## 1300_FPGA_AUX_1V8.kicad_sch

Enable control

## 1400_FPGA_AUX_2V5.kicad_sch

Output sensing

## 1400_FPGA_AUX_2V5.kicad_sch

U140002 (TPS62130A) receives FPGA5V5 at AVIN and both PVIN pins. C140007 (10 uF)
and C140005 (100 nF) bypass the input. CMD_AUX25 drives Q140002; a high command
enables EN_AUX25. R140012 (100 kOhm) pulls EN low when Q140002 is off. FPGA5V5
must be available first.

## 1400_FPGA_AUX_2V5.kicad_sch

R140010 (0.02 Ohm) drops 20 mV/A outside feedback. At 3 A, AUX2V5 is about 2.44
V. R140009 (10 kOhm) bleeds the output. PGR_AUX25 is open drain, pulled to AON
by R140011 (10 kOhm); use its RAW status only with FPGA5V5 present. The IC
supports up to 3 A, subject to thermal and shared-input limits. Current and
thermal protection are internal.

## 1400_FPGA_AUX_2V5.kicad_sch

RAW: 2.5 V nominal; shunt: 20 mV/A.
PGR_AUX25: RAW status, pulled up to AON.

## 1400_FPGA_AUX_2V5.kicad_sch

Output voltage setting

## 1400_FPGA_AUX_2V5.kicad_sch

Enable control

## 1400_FPGA_AUX_2V5.kicad_sch

FPGA5V5 -> AUX25_RAW; L140002 + C140008 filter the output.
VOS and feedback sense RAW before R140010.

## 1400_FPGA_AUX_2V5.kicad_sch

FPGA auxiliary supply, 2.5 V

## 1400_FPGA_AUX_2V5.kicad_sch

Buck conversion and filtering

## 1400_FPGA_AUX_2V5.kicad_sch

CMD_AUX25 drives Q140002; R140012 pulls EN low.

## 1400_FPGA_AUX_2V5.kicad_sch

L140002 (2.2 uH) and C140008 (47 uF nominal) filter the switched output. VOS
senses AUX25_RAW; FSW tied to RAW selects the approximately 1.25 MHz mode as
RAW rises. Power-save operation is automatic at light load. C140006 (10 nF) on
SS/TR gives an approximately 5 ms ramp.

## 1400_FPGA_AUX_2V5.kicad_sch

SHEET GUIDE / FPGA Aux 2.5 V

## 1400_FPGA_AUX_2V5.kicad_sch

Output and protection

## 1400_FPGA_AUX_2V5.kicad_sch

This converter supplies the 2.5 V auxiliary domain of MIRA's FPGA subsystem.
Keeping it separate from AUX1V8 and IO3V3 allows domains with different
voltage requirements to be enabled and checked independently. CMD_AUX25 and
PGR_AUX25 support startup sequencing and fault supervision.

## 1400_FPGA_AUX_2V5.kicad_sch

FPGA Aux 2.5 V

## 1400_FPGA_AUX_2V5.kicad_sch

R140007 (34 kOhm) and R140008 (16 kOhm) set the RAW voltage:
V(AUX25_RAW)=0.8 V x (1+R140007/R140008) = 2.5 V.
To change it: R140007 = R140008 x (VRAW / 0.8 V - 1). Increasing R140007 raises the
voltage. DEF is grounded; the +5% margin is disabled.

## 1400_FPGA_AUX_2V5.kicad_sch

Conversion and filtering

## 1400_FPGA_AUX_2V5.kicad_sch

Input and enable

## 1400_FPGA_AUX_2V5.kicad_sch

Purpose and role

## 1500_FPGA_IO_3V3.kicad_sch

Conversion and filtering

## 1500_FPGA_IO_3V3.kicad_sch

FPGA I/O supply, approximately 3.3 V

## 1500_FPGA_IO_3V3.kicad_sch

CMD_IO33 drives Q140003; R140014 pulls EN low.

## 1500_FPGA_IO_3V3.kicad_sch

RAW: 3.295 V nominal; shunt: 20 mV/A.
PGR_IO33: RAW status, pulled up to AON.

## 1500_FPGA_IO_3V3.kicad_sch

L140003 (2.2 uH) and C140012 (47 uF nominal) filter the switched output. VOS
senses IO33_RAW; FSW tied to RAW selects the approximately 1.25 MHz mode as
RAW rises. Power-save operation is automatic at light load. C140011 (10 nF) on
SS/TR gives an approximately 5 ms ramp.

## 1500_FPGA_IO_3V3.kicad_sch

Buck conversion and filtering

## 1500_FPGA_IO_3V3.kicad_sch

Output sensing

## 1500_FPGA_IO_3V3.kicad_sch

Output voltage setting

## 1500_FPGA_IO_3V3.kicad_sch

FPGA5V5 -> IO33_RAW; L140003 + C140012 filter the output.
VOS and feedback sense RAW before R140015.

## 1500_FPGA_IO_3V3.kicad_sch

Purpose and role

## 1500_FPGA_IO_3V3.kicad_sch

Input and enable

## 1500_FPGA_IO_3V3.kicad_sch

R140015 (0.02 Ohm) drops 20 mV/A outside feedback. At 3 A, IO3V3 is about 3.235
V. R140013 (10 kOhm) bleeds the output. PGR_IO33 is open drain, pulled to AON
by R140016 (10 kOhm); use its RAW status only with FPGA5V5 present. The IC
supports up to 3 A, subject to thermal and shared-input limits. Current and
thermal protection are internal.

## 1500_FPGA_IO_3V3.kicad_sch

Enable control

## 1500_FPGA_IO_3V3.kicad_sch

FPGA I-O 3.3 V

## 1500_FPGA_IO_3V3.kicad_sch

U140003 (TPS62130A) receives FPGA5V5 at AVIN and both PVIN pins. C140010 (10 uF)
and C140009 (100 nF) bypass the input. CMD_IO33 drives Q140003; a high command
enables EN_IO33. R140014 (100 kOhm) pulls EN low when Q140003 is off. FPGA5V5
must be available first.

## 1500_FPGA_IO_3V3.kicad_sch

Output and protection

## 1500_FPGA_IO_3V3.kicad_sch

SHEET GUIDE / FPGA I-O 3.3 V

## 1500_FPGA_IO_3V3.kicad_sch

This converter supplies the 3.3 V I/O domain of MIRA's FPGA subsystem and its
board interfaces. The FPGA exchanges commands and data with the STM32 and
manages the fast matrix/ADC path. An independent I/O rail supports controlled
startup and monitoring alongside the auxiliary supplies.

## 1500_FPGA_IO_3V3.kicad_sch

R140017 (49.9 kOhm) and R140018 (16 kOhm) set the RAW voltage:
V(IO33_RAW)=0.8 V x (1+R140017/R140018) = 3.295 V.
To change it: R140017 = R140018 x (VRAW / 0.8 V - 1). Increasing R140017 raises the
voltage. DEF is grounded; the +5% margin is disabled.

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Analog rail power-good detection

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Conditioned monitor inputs

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Thresholds apply to MON_V signals.
Translate the negative rail before sensing.

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

USB rail status

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Timing and settings

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

SHEET GUIDE / Analog Power Good

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Analog preregulator status

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

+15 V AFE status

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Vref = AON x 10k / (Rtop + 10k). At AON = 3.28 V: USB 2.231 V; ANA6 2.689 V; P15
2.360 V; N15 1.312 V. C380005-C380003 filter the references, with tau about 32, 18,
28 and 60 us. Actual rail trip voltages depend on upstream monitor scaling.

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

-15 V AFE status

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Purpose and role

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

U380001 creates hardware supply-status signals for MIRA's USB, analog preregulator
and bipolar AFE power domains. The power controller and rail-ready logic use
these signals before allowing matrix operation. This block checks supply levels;
fast matrix pulse timing is handled elsewhere.

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Inputs and outputs

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

MON_V_USB, MON_V_ANA6, MON_V_P15 and MON_V_N15 connect to the four non-inverting
inputs. PG_USB, PG_ANA, PG_P15 and PG_N15 are open-collector outputs pulled to
AON by R380012-R380002 (10 kOhm). U380001 and C380002 (100 nF) use AON and GND.

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Analog Power Good

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Control logic

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Each channel compares its monitor voltage with an AON-derived reference. A
monitor above the reference releases its output HIGH; a monitor below it pulls
the output LOW. These are four independent status channels. No overvoltage
window or fault memory is implemented here.

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

Protection and fault response

## 2900_PM_ANALOG_POWER_GOOD.kicad_sch

MON inputs require conditioning into the GND-to-AON range; the negative rail
must be translated before MON_V_N15. There is no feedback resistor for analog
hysteresis. Validate monitor noise, AON startup and brownout behavior with the
full interlock circuit; these capacitors do not set a PG qualification delay.

## 2500_PM_WATCHDOGS.kicad_sch

Protection and fault response

## 2500_PM_WATCHDOGS.kicad_sch

Supply Watchdogs

## 2500_PM_WATCHDOGS.kicad_sch

PM_WDI falling edges service the 1.60 s timer.

## 2500_PM_WATCHDOGS.kicad_sch

Purpose and role

## 2500_PM_WATCHDOGS.kicad_sch

Power and host watchdog supervision

## 2500_PM_WATCHDOGS.kicad_sch

PM reset combining

## 2500_PM_WATCHDOGS.kicad_sch

SYS3V3 supervisor and host watchdog

## 2500_PM_WATCHDOGS.kicad_sch

AON reset or PM watchdog fault
pulls the PM controller reset low.
Host reset coupling is on sheet 5400.

## 2500_PM_WATCHDOGS.kicad_sch

D270001 combines AON_RESET_N and PM_WDO_N into PM_RESET_N.
Either LOW resets U260001 through the common-anode diode.
Host WDO now also pulls HOST_RESET_N LOW through U280005
on sheet 5400; both host faults clear matrix permission.

## 2500_PM_WATCHDOGS.kicad_sch

AON supervisor and PM watchdog

## 2500_PM_WATCHDOGS.kicad_sch

Timing and settings

## 2500_PM_WATCHDOGS.kicad_sch

PM_WDI and HOST_WDI are heartbeat inputs.
AON_RESET_N and HOST_RESET_N report supply / manual reset.
PM_WDO_N and HOST_WDO_N report watchdog expiry.
J270002 and J270001 provide PM and host manual reset contacts.

## 2500_PM_WATCHDOGS.kicad_sch

SET1 is high and CWD is open on both supervisors.
Watchdog timeout: 1.60 s nominal, 1.36 to 1.84 s specified.
Provide falling WDI edges sooner than the minimum timeout.
Reset release delay and WDO low pulse are 200 ms nominal.

## 2500_PM_WATCHDOGS.kicad_sch

SHEET GUIDE / Supply Watchdogs

## 2500_PM_WATCHDOGS.kicad_sch

Supply undervoltage or manual reset asserts RESET.
PM expiry resets PM; host expiry also resets host via U280005.
HOST_RESET_N pullups stay on SYS3V3; WDO pullups use AON.
Sheet 5400 adds application-heartbeat timeout and first-edge latch.

## 2500_PM_WATCHDOGS.kicad_sch

Inputs and outputs

## 2500_PM_WATCHDOGS.kicad_sch

Control logic

## 2500_PM_WATCHDOGS.kicad_sch

U270002 supervises the AON-powered MIRA power controller.
U270001 supervises the SYS3V3 host domain and its heartbeat.
These independent monitors feed the permit interlocks so a
stalled controller or host can inhibit operation without software.

## 2500_PM_WATCHDOGS.kicad_sch

J270001 requests a host manual reset.
R270007 pulls HOST_RESET_N to SYS3V3, not AON.

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

A cleared global permit forces all seven commands LOW.
A LOW request disables its own rail while other requested rails
may remain enabled. Matrix permission is separate and can be
removed while these auxiliary supplies remain powered.

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

DDR termination / analog LDO requests

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

Each used channel follows the same rule:
CMD_x_RAW = GLOBAL_PWR_PERMIT AND EN_REQ_x.
Sheet 5300 also requires STARTUP_READY_H before outputs are driven.
The unused U330001 inputs are grounded and its output is not connected.

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

Purpose and role

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

Inputs and outputs

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

This second AON-powered gate bank qualifies the auxiliary supply
requests for FPGA I/O, memory, IO18 and analog circuitry in MIRA.
Together with the primary bank, it lets the power manager stage
startup and revoke all switched-rail enables through one permit.

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

Timing and settings

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

SHEET GUIDE / Aux Enable Gates

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

Auxiliary rail enable gates

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

Aux Enable Gates

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

All request and command lines have 100 kOhm pull-downs.
C330002/C330001 (100 nF) bypass the two SN74HC08 supplies to GND.
This sheet adds no delay or analog threshold; sequence and settling
checks are handled by the power manager and readiness circuits.

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

U330002 generates CMD_AUX25_RAW, CMD_IO33_RAW, CMD_DDR_RAW and CMD_IO18_RAW.
U330001 generates CMD_VTT_RAW, CMD_ANA5_RAW and CMD_ANA33_RAW.
Each used channel receives GLOBAL_PWR_PERMIT and its matching
EN_REQ input. The fourth U330001 gate is unused.

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

FPGA I/O / DDR / USB and converter I/O requests

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

Control logic

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

Protection and fault response

## 2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch

Raw CMD = request AND global permit; qualified on sheet 5300

## 1600_DDR_1V35.kicad_sch

Enable control

## 1600_DDR_1V35.kicad_sch

Input and enable

## 1600_DDR_1V35.kicad_sch

Buck conversion and filtering

## 1600_DDR_1V35.kicad_sch

SHEET GUIDE / DDR 1.35 V

## 1600_DDR_1V35.kicad_sch

RAW: 1.35 V nominal; shunt: 10 mV/A.
PGR_DDR: RAW status, pulled up to AON.

## 1600_DDR_1V35.kicad_sch

Output sensing

## 1600_DDR_1V35.kicad_sch

DDR memory supply, 1.35 V

## 1600_DDR_1V35.kicad_sch

Conversion and filtering

## 1600_DDR_1V35.kicad_sch

FPGA5V5 -> DDR_RAW; L150001 + C150003 filter the output.
VOS and feedback sense RAW before R150004.

## 1600_DDR_1V35.kicad_sch

R150004 (0.01 Ohm) drops 10 mV/A outside feedback. At 3 A, DDR1V35 is about
1.32 V. R150005 (10 kOhm) bleeds the output. PGR_DDR is open drain, pulled to
AON by R150006 (10 kOhm); use its RAW status only with FPGA5V5 present. The IC
supports up to 3 A, subject to thermal and shared-input limits. Current and
thermal protection are internal.

## 1600_DDR_1V35.kicad_sch

U150001 (TPS62130A) receives FPGA5V5 at AVIN and both PVIN pins. C150002 (10 uF)
and C150001 (100 nF) bypass the input. CMD_DDR drives Q150001; a high command
enables EN_DDR. R150002 (100 kOhm) pulls EN low when Q150001 is off. FPGA5V5 must
be available first.

## 1600_DDR_1V35.kicad_sch

Output and protection

## 1600_DDR_1V35.kicad_sch

L150001 (2.2 uH) and C150003 (47 uF nominal) filter the switched output. VOS
senses DDR_RAW; FSW tied to RAW selects the approximately 1.25 MHz mode as
RAW rises. Power-save operation is automatic at light load. C150004 (10 nF) on
SS/TR gives an approximately 5 ms ramp.

## 1600_DDR_1V35.kicad_sch

Output voltage setting

## 1600_DDR_1V35.kicad_sch

Purpose and role

## 1600_DDR_1V35.kicad_sch

This converter supplies MIRA's 1.35 V DDR memory domain for data buffering in
the FPGA processing path. DDR1V35 also feeds the DDR termination/reference
sheet, which derives tracking VTT and VREF supplies. Separate control and
status support coordinated startup of memory and its interfaces.

## 1600_DDR_1V35.kicad_sch

CMD_DDR drives Q150001; R150002 pulls EN low.

## 1600_DDR_1V35.kicad_sch

R150003 (11 kOhm) and R150001 (16 kOhm) set the RAW voltage:
V(DDR_RAW)=0.8 V x (1+R150003/R150001) = 1.35 V.
To change it: R150003 = R150001 x (VRAW / 0.8 V - 1). Increasing R150003 raises the
voltage. DEF is grounded; the +5% margin is disabled.

## 1600_DDR_1V35.kicad_sch

DDR 1.35 V

## 1800_DDR_VTT_REFERENCE.kicad_sch

Input and enable

## 1800_DDR_VTT_REFERENCE.kicad_sch

R150010 and R150007 (10.0 kOhm each) divide DDR1V35 into REFIN_VTT. V(VTT) and
V(DDR_VREF) approximately equal V(DDR1V35) / 2 = 0.675 V at 1.35 V. C150010
(100 nF) filters REFIN. Preserve the 1:1 ratio when changing the memory I/O
voltage.

## 1800_DDR_VTT_REFERENCE.kicad_sch

SHEET GUIDE / DDR VTT and VREF

## 1800_DDR_VTT_REFERENCE.kicad_sch

DDR1V35 / 2 sets both outputs.
VTT sources and sinks current.

## 1800_DDR_VTT_REFERENCE.kicad_sch

Two output functions

## 1800_DDR_VTT_REFERENCE.kicad_sch

Termination and reference

## 1800_DDR_VTT_REFERENCE.kicad_sch

Output and protection

## 1800_DDR_VTT_REFERENCE.kicad_sch

Enable control

## 1800_DDR_VTT_REFERENCE.kicad_sch

Output voltage setting

## 1800_DDR_VTT_REFERENCE.kicad_sch

VTT: termination bias
DDR_VREF: receiver reference

## 1800_DDR_VTT_REFERENCE.kicad_sch

This block supplies the termination bias and receiver reference for MIRA's
1.35 V DDR interface. VTT sources and sinks termination current; DDR_VREF
sets the receiver threshold. Both track half of DDR1V35 so the interface
follows its memory I/O supply.

## 1800_DDR_VTT_REFERENCE.kicad_sch

CMD_VTT is buffered on sheet 5300.
R150011 links it directly to EN_VTT.
DDR_VREF remains on with EN low.

## 1800_DDR_VTT_REFERENCE.kicad_sch

U150002 (TPS51200) uses AON for VIN and DDR1V35 for VLDOIN. The AUP
buffer on sheet 5300 drives EN_VTT through R150011 without a VGS drop.
R150008 and R340013 pull EN low when the buffer is disabled. Disabling EN
discharges VTT; DDR_VREF remains active while its input supplies are valid.

## 1800_DDR_VTT_REFERENCE.kicad_sch

DDR VTT and VREF

## 1800_DDR_VTT_REFERENCE.kicad_sch

DDR termination and reference, half of DDR1V35

## 1800_DDR_VTT_REFERENCE.kicad_sch

U150002 is a linear source/sink regulator. C150006 (10 uF) and C150011 (4.7 uF)
bypass its two inputs. C150007-C150008 provide 30 uF nominal on VTT; C150009 (100
nF) bypasses DDR_VREF. VOSNS senses the VTT net; route it separately from the
load-current path.

## 1800_DDR_VTT_REFERENCE.kicad_sch

Purpose and role

## 1800_DDR_VTT_REFERENCE.kicad_sch

Conversion and filtering

## 1800_DDR_VTT_REFERENCE.kicad_sch

PGR_VTT is open drain and is pulled to AON by R150009 (10 kOhm). U150002 includes
soft start, source/sink current limiting, UVLO and thermal shutdown. These
limits are internal; the divider does not set a current trip. Available
termination current depends on thermal design and load.

## 5700_AON_ANALOG_INPUT_ISOLATION.kicad_sch

Analog Isolation 2

## 5700_AON_ANALOG_INPUT_ISOLATION.kicad_sch

U500001: MON_V_INPUT -> MON_V_INPUT_SAFE, MON_V_IO33 -> MON_V_IO33_SAFE

## 5700_AON_ANALOG_INPUT_ISOLATION.kicad_sch

U500002: MON_V_P15 -> MON_V_P15_SAFE, MON_V_IO18 -> MON_V_IO18_SAFE

## 5700_AON_ANALOG_INPUT_ISOLATION.kicad_sch

U500003: MON_V_SYS -> MON_V_SYS_SAFE, MON_V_USB -> MON_V_USB_SAFE

## 5700_AON_ANALOG_INPUT_ISOLATION.kicad_sch

U500004: ADC_VTT -> ADC_VTT_SAFE

## 5700_AON_ANALOG_INPUT_ISOLATION.kicad_sch

All unpowered receivers have a 100 kOhm discharge path. Divider gain includes this load.
TMUX2821: +/-5.5 V beyond-supply analog range; common GND. No diode clamp to AON upstream.

## 5600_AON_ANALOG_INPUT_ISOLATION.kicad_sch

Analog Isolation 1

## 5600_AON_ANALOG_INPUT_ISOLATION.kicad_sch

U490001: MON_V_ANA33 -> MON_V_ANA33_SAFE, MON_V_ANA5 -> MON_V_ANA5_SAFE

## 5600_AON_ANALOG_INPUT_ISOLATION.kicad_sch

U490002: MON_V_ANA6 -> MON_V_ANA6_SAFE, MON_V_AUX18 -> MON_V_AUX18_SAFE

## 5600_AON_ANALOG_INPUT_ISOLATION.kicad_sch

U490003: MON_V_AUX25 -> MON_V_AUX25_SAFE, MON_V_CORE -> MON_V_CORE_SAFE

## 5600_AON_ANALOG_INPUT_ISOLATION.kicad_sch

U490004: MON_V_DDR -> MON_V_DDR_SAFE, MON_V_FPGA -> MON_V_FPGA_SAFE

## 5600_AON_ANALOG_INPUT_ISOLATION.kicad_sch

All unpowered receivers have a 100 kOhm discharge path. Divider gain includes this load.
TMUX2821: +/-5.5 V beyond-supply analog range; common GND. No diode clamp to AON upstream.

## 2200_PROGRAM_NEGATIVE.kicad_sch

Q200001 discharges through R200011 || R200009 = 340 Ohm.
U200001 disables discharge; R200004 bleeds residual charge.

## 2200_PROGRAM_NEGATIVE.kicad_sch

This path provides PROG_N15 to MIRA's bipolar stimulus circuitry for
memristor READ/SET/RESET operations. It connects N15 under hardware
authorization and disconnects the output when permission is removed.
Downstream matrix electronics define stimulus amplitude and pulse timing;
forming uses a separate branch.

## 2200_PROGRAM_NEGATIVE.kicad_sch

Without optocoupler drive, Q200003 equalizes pass G-S.
U200003 releases this clamp during authorized operation.

## 2200_PROGRAM_NEGATIVE.kicad_sch

N15 is the negative power input; AON supplies the control side. Sinking
MATRIX_OPTO_K lights U200002-U200001 through R200003, R200005 and R200002 (300 Ohm
each). U200002 raises the pass gates through R200010 (330 kOhm), U200003 releases
the OFF clamp and U200001 disables output discharge.

## 2200_PROGRAM_NEGATIVE.kicad_sch

Output voltage setting

## 2200_PROGRAM_NEGATIVE.kicad_sch

Without optocoupler drive, Q200003 equalizes the pass gates and sources. Q200001
discharges the output through R200011 || R200009 = 340 Ohm; R200004 (100 kOhm)
bleeds the remaining charge. D200003, D200002 and D200001 clamp VGS; D200004 clamps
positive output excursions. Verify actual OFF and discharge timing.

## 2200_PROGRAM_NEGATIVE.kicad_sch

PROG_N15 follows the upstream N15 voltage with MOSFET and interconnect
losses. Its voltage is set by the upstream regulator; this sheet contains no
adjustable regulator or local current-limit setting. The 10 V zeners limit
gate-source stress, rather than setting the programming amplitude.

## 2200_PROGRAM_NEGATIVE.kicad_sch

Input and enable

## 2200_PROGRAM_NEGATIVE.kicad_sch

Negative programming supply switch

## 2200_PROGRAM_NEGATIVE.kicad_sch

N15 -> PROG_N15 when enabled.
The OFF pair blocks backfeed.

## 2200_PROGRAM_NEGATIVE.kicad_sch

Q200002 and Q200004 (AO3400A) form an opposed NMOS pair with common sources and
joined gates. Their body diodes block both current directions while the pair
is off. C200003 (4.7 uF nominal) stores and filters the output. R200006 (680 Ohm)
and C200002 (47 nF) shape gate/output transitions.

## 2200_PROGRAM_NEGATIVE.kicad_sch

SHEET GUIDE / Program Negative

## 2200_PROGRAM_NEGATIVE.kicad_sch

Purpose and role

## 2200_PROGRAM_NEGATIVE.kicad_sch

Program Negative

## 2200_PROGRAM_NEGATIVE.kicad_sch

Output and protection

## 2200_PROGRAM_NEGATIVE.kicad_sch

Negative pass pair and output

## 2200_PROGRAM_NEGATIVE.kicad_sch

Output discharge

## 2200_PROGRAM_NEGATIVE.kicad_sch

Hardware OFF clamp

## 2200_PROGRAM_NEGATIVE.kicad_sch

Conversion and filtering
