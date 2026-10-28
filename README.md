# MIRA

**MIRA is a research platform under development for experiments with memristor arrays and neuromorphic computing.**

The project aims to bring array control, an analog front end, digital processing, and software tools into a single system. It is intended for studying memristor readout and programming, vector–matrix multiplication (VMM), and spiking neuron models.

## Current status

**RevA** is currently in development. The repository contains two independent KiCad projects with local libraries: **MIRA_Control (30 active schematic pages)** and **MIRA_Power (49 active schematic pages)**.

Control includes MCU, FPGA, communications, matrix, analog, and protection circuits. Both projects are undergoing review before PCB placement and routing.

The [high-load schematic candidate](docs/pcb-preparation/high-load/README.md) dated **2026-10-28** adds a supplemental CORE connector and positive remote sense, replaces N15 with a TEN 30-2413WIN module, and coordinates N15 overcurrent and input overvoltage thresholds. The candidate input range is **18–30 V DC**, nominal 24 V. The provisional targets are CORE 5.2 A and N15 0.468 A; hardware capacity has not been validated.

KiCad CLI 10.0.7 reports **Power: 0 errors / 0 warnings; Control: 0 errors / 2 active warnings / 32 excluded warnings**, with the existing ignored checks retained. Twenty-one netlist/value assertions pass. Connector selection, PCB layout, feedback stability, startup, thermal performance and analog noise remain open. The [original inter-board review](docs/pcb-preparation/README.md), [original ERC reports](docs/pcb-preparation/erc/README.md) and [earlier correction candidate](docs/pcb-preparation/fixes/README.md) are preserved as history.

Schematics in this repository do not imply that the corresponding circuits have been built or validated in hardware.

## Repository contents

| Project | Current contents | Open in KiCad |
| --- | --- | --- |
| [MIRA_Power](hardware/MIRA_Power) | Power schematics, hierarchy, and local libraries | `hardware/MIRA_Power/MIRA_Power.kicad_pro` |
| [MIRA_Control](hardware/MIRA_Control) | 30-page schematic hierarchy, an empty PCB, and local symbol, footprint, and STEP libraries | `hardware/MIRA_Control/MIRA_Control.kicad_pro` |

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
- Select and qualify the physical inter-board connectors, power/return paths and mechanical stack.
- Validate CORE remote-sense stability, N15 startup/protection/noise and input surge response.
- Complete the remaining domain sequencing, reset/STOP, VTT/DDR_VREF and ERC-exclusion reviews listed in the [candidate report](docs/pcb-preparation/high-load/README.md).
- Prepare and review component placement and PCB routing before hardware validation.
