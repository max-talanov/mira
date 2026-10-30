# MIRA

**MIRA.06, 30 октября 2026:** [компоненты, разъёмы и сборка](docs/pcb-preparation/components-assembly/README.md). Уточнены 112 записей компонентов; исправлены SMT-footprint J100 и отверстия J600. BOM: 2148 обозначений / 322 группы; закупочные статусы и условия монтажа BGA/0201 записаны. Схемные соединения сохранены. Чертёж и открывание сокета, полный OPN входного клеммника, закупка, допуски и нагрузка разъёмов, подтверждение сборщика остаются открытыми; разрешения на производство нет.

**MIRA.05, 30 октября 2026:** [требования аналоговой части и исправления схемы](docs/pcb-preparation/analog-requirements/README.md). U2109 заменён на INA149AIDR с новой распиновкой; потолок команды снижен до 10,05 В, порог готовности P15 повышен до 13,22 В. Сохранены исправления пары CV 100/101 кОм и восьми записей BOM из промежуточного обновления; итоговая дельта — 12 компонентов. Заданы предварительные диапазоны READ/SET/RESET/FORMING, ток, нагрузка, одновременность и время; свойства реальной матрицы оставлены неизвестными. ERC 0 ошибок / 0 предупреждений на обеих платах. Пиковый ток, устойчивость, точность и время импульсов требуют отдельной проверки; прошивка и PCB не изменены.

**Решение от 30.10.2026: проверка MIG/Vivado отложена по согласованию с пользователем. Вернуться к ней перед трассировкой FPGA ↔ DDR3L на плате Control и до окончательной фиксации распиновки FPGA. По решению пользователя текущая карточка MIRA.04 закрывается как завершённый схемный этап; проверка MIG остаётся незавершённым условием перед трассировкой. Остальные проверки схемы, проектирование Power и независимые участки Control можно продолжать.**

**MIRA.04, 30 октября 2026:** [проверка цифровых интерфейсов](docs/pcb-preparation/digital-interfaces/README.md). SPI SCK перенесён AB12 → Y11; FMC/AF и 164 FPGA-порта сверены, ERC 0/0. MIG/Vivado ещё не запускались; кандидатные XDC и процедура запуска находятся в `fpga/digital-interfaces/`. Закрытие текущей карточки не означает выполнения проверки MIG; её нужно завершить до трассировки DDR3L.

**Предыдущий этап v6, 30 октября 2026:** [исправления сигналов при отключённом питании](docs/pcb-preparation/signal-remediation/README.md). Power — 61 лист / Control — 43; ERC 0/0. Закрытие — по схеме в указанных условиях; испытания платы и PCB открыты. AON: суммарный добавочный резерв 112 mA и 2.8 µF к бюджету 28 октября. Данные прежних этапов ниже сохранены как история.

**MIRA is a research platform under development for experiments with memristor arrays and neuromorphic computing.**

The project aims to bring array control, an analog front end, digital processing, and software tools into a single system. It is intended for studying memristor readout and programming, vector–matrix multiplication (VMM), and spiking neuron models.

## Current status

The current **MIRA.05 analog requirements** revision defines a provisional operating envelope and repairs the anti-windup amplifier, command ceiling and P15 qualifier. See the [analog report](docs/pcb-preparation/analog-requirements/README.md). Native ERC and historical regressions pass; matrix-specific limits, loop stability and transient peak-current qualification remain open.

The previous **2026-10-30 v6 signal remediation** adds hardware protection for PM, DAC, ADC/FDA and comparator inputs; replaces 33 analog switch ICs with fail-safe-input parts; isolates 10 VIN-relative enable paths; and qualifies USB and FPGA AUX/IO supplies. See the [current review and operating conditions](docs/pcb-preparation/signal-remediation/README.md). There are 271 new components and 40 changed legacy values. Native KiCad ERC reports zero errors and warnings. The checklist can be closed as a schematic review within those conditions. PCB, firmware and prototype qualification remain open. The [v5 receiver-only report](docs/pcb-preparation/unpowered-signals/README.md) is historical.

The preceding [fault hardware repair](docs/pcb-preparation/fault-review/README.md) adds a 170–230 ms application heartbeat watchdog, first-edge readiness and direct host reset on watchdog expiry. LINK_READY_H feeds the matrix interlock and PM PC15. The 14 added components are checked by native netlist and ideal timing/latch tests; firmware and prototype validation remain open.

The **2026-10-29** update adds [AON startup gating and full-swing VTT enable](docs/pcb-preparation/startup/README.md), plus [PM clear feedback and the 15-rail sequencing contract](docs/pcb-preparation/sequencing/README.md). The PM firmware must read GLOBAL_CLEAR_N on PC14 before arming, then confirm GLOBAL_PWR_PERMIT. Firmware implementation and prototype fault/ramp tests remain open.

**RevA** is currently in development. The repository contains two independent KiCad projects with local libraries: **MIRA_Control (43 active schematic pages)** and **MIRA_Power (61 active schematic pages)**.

Control includes MCU, FPGA, communications, matrix, analog, and protection circuits. Both projects are undergoing review before PCB placement and routing.

The [high-load schematic candidate](docs/pcb-preparation/high-load/README.md) dated **2026-10-28** adds a supplemental CORE connector and positive remote sense, replaces N15 with a TEN 30-2413WIN module, and coordinates N15 overcurrent and input overvoltage thresholds. The candidate input range is **18–30 V DC**, nominal 24 V. The provisional targets are CORE 5.2 A and N15 0.468 A; hardware capacity has not been validated.

The [distributed power interface](docs/pcb-preparation/distributed-power/README.md) replaces the central 64-contact connector with **seven local power entries and one separate supervision interface**. The zones are FPGA, DDR, MCU, USB, Ethernet, DAC/matrix and ADC/AFE. Eight Samtec SSW/HTSW pairs have assigned parts, local footprints and nominal 3D envelope models. The proposed stack has Power below Control and a 12 mm facing-surface gap; final placement coordinates and routing remain to be defined.

All 118 mating contacts were checked. The 6686-entry connector regression baseline from `c72edb2` remains matched after explicitly mapping back the documented startup, PC14 feedback, fault hardware the three v5 receive-path changes, and the explicit v6 signal-remediation delta; unrelated source/load circuits and positive CORE sense are preserved. The new pinout requires updating both projects together. The [earlier connector/ERC report](docs/pcb-preparation/connectors-erc/README.md) is retained as history.

KiCad CLI 10.0.8 reports **0 errors / 0 warnings / 0 exclusions for both projects**. Negative analog supply pins are now named VSS_NEG, with their power-input types and nets preserved; 32 old exclusions were removed. Two existing style checks remain ignored (`four_way_junction`, `single_global_label`); footprint-filter and simulation-model checks were re-enabled. PCB layout, mechanical and thermal qualification, feedback stability, startup and analog noise remain open. The [task 1/2 status and remaining questions](docs/pcb-preparation/README.md), [current ERC review](docs/pcb-preparation/erc/README.md) and [updated power budget](docs/pcb-preparation/power-budget/README.md) describe the current candidate. Original reports and calculations remain available as history. The budget applies a 30% margin to provisional peak loads and explicitly leaves N15 startup and shared-rail current distribution unresolved.

Schematics in this repository do not imply that the corresponding circuits have been built or validated in hardware.

## Repository contents

| Project | Current contents | Open in KiCad |
| --- | --- | --- |
| [MIRA_Power](hardware/MIRA_Power) | Power schematics, hierarchy, and local libraries | `hardware/MIRA_Power/MIRA_Power.kicad_pro` |
| [MIRA_Control](hardware/MIRA_Control) | 43-page schematic hierarchy, an empty PCB, and local symbol, footprint, and 3D libraries | `hardware/MIRA_Control/MIRA_Control.kicad_pro` |

Each project has its own library tables and project-relative library paths. Keep its complete folder together.

The power project includes:

| File or directory | Purpose |
| --- | --- |
| `MIRA_Power.kicad_pro` | KiCad project file |
| `MIRA_Power.kicad_sch` | Top-level schematic and hierarchy navigation |
| `POWER_SYSTEM.kicad_sch` | Power system overview |
| `POWER_INPUT.kicad_sch` | Power input and primary protection |
| `PRIMARY_POWER.kicad_sch` | Primary power converters |
| `SECONDARY_POWER.kicad_sch` | Secondary power converters |
| `PROGRAM_SWITCHES.kicad_sch` | Programming voltage switching |
| `POWER_CONTROL.kicad_sch` | Power control and protection interlocks |
| `POWER_MONITOR.kicad_sch` | Voltage and current monitoring |
| `libraries/` | Local symbol, footprint, and 3D model libraries |

The power system is designed around an external **24 V DC supply**. It provides digital and analog power rails, controlled startup, rail monitoring, and fault shutdown.

## Planned architecture

- **Memristor array and analog front end:** readout, programming, and VMM operations.
- **FPGA:** array timing control and high-speed data transfer.
- **STM32:** neuron model computation and control tasks.
- **USB 3.0 and Ethernet:** communication with a host computer.
- **Mira Studio:** a desktop application for configuring experiments, controlling the device, visualizing data, and saving results.

These blocks describe the planned development direction. Their implementation status is reflected in the current project files.

## Opening the projects

1. Clone the repository:

   ```bash
   git clone https://github.com/max-talanov/mira.git
   ```

2. Open the required `.kicad_pro` file from the table above. On Linux:

   ```bash
   cd mira
   kicad hardware/MIRA_Power/MIRA_Power.kicad_pro
   # Or open the control project:
   kicad hardware/MIRA_Control/MIRA_Control.kicad_pro
   ```

3. In both projects, use the schematic hierarchy to navigate between blocks. Open the root schematic through the project manager so the project-relative libraries are available.

Keep the directory structure intact. The `sym-lib-table` and `fp-lib-table` files are stored alongside the project and reference its local libraries.

## Versioning

**RevA** identifies the hardware revision. Git tags such as `v0.1.0` mark development milestones in the repository history.

| Tag | Milestone |
| --- | --- |
| `v0.1.0` | Initial KiCad project and local library import |
| `v0.2.0` | Separate Power and empty Control projects, with updated repository documentation |

Use commits for routine edits and annotated tags for milestones. Keep published tags on their original commits. A new repository tag does not change the hardware revision or indicate completed hardware validation.

See [CHANGELOG.md](CHANGELOG.md), the [commit history](https://github.com/max-talanov/mira/commits/main), and the [tag list](https://github.com/max-talanov/mira/tags).

## Licenses and attribution

See [LICENSE](LICENSE) and the third-party library and model notices included under each project's `libraries/` directory. Keep those notices with the corresponding assets.

## Next steps

- Establish the FPGA/matrix maximum operating scenario and recalculate the full power budget for the new N15 module.
- Co-design both PCB floorplans around the eight connector pairs; place regulators and local returns near their assigned load zones and qualify the proposed 12 mm mechanical stack.
- Validate CORE remote-sense stability, N15 startup/protection/noise and input surge response.
- Complete the remaining domain sequencing, reset/STOP and VTT/DDR_VREF reviews listed in the [candidate report](docs/pcb-preparation/high-load/README.md). The VSS ERC-exclusion review is resolved in the connector/ERC update.
- Prepare and review component placement and PCB routing before hardware validation.
