# MIRA

**MIRA is a research platform under development for experiments with memristor arrays and neuromorphic computing.**

The project aims to bring array control, an analog front end, digital processing, and software tools into a single system. It is intended for studying memristor readout and programming, vector–matrix multiplication (VMM), and spiking neuron models.

## Current status

**RevA** is currently in development. The repository contains two independent KiCad projects: the power schematics and an empty control project with local libraries.

Power development is focused on connection review, protection, sequencing, and monitoring. The control project is the starting point for drawing the MCU, FPGA, communications, and matrix circuits.

Schematics in this repository do not imply that the corresponding circuits have been built or validated in hardware.

## Repository contents

| Project | Current contents | Open in KiCad |
| --- | --- | --- |
| [MIRA_Power](hardware/MIRA_Power) | Power schematics, hierarchy, and local libraries | `hardware/MIRA_Power/MIRA_Power.kicad_pro` |
| [MIRA_Control](hardware/MIRA_Control) | One empty A4 schematic, an empty PCB, and local symbol, footprint, and STEP libraries | `hardware/MIRA_Control/MIRA_Control.kicad_pro` |

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

3. In `MIRA_Power`, use the schematic hierarchy to navigate between blocks. In `MIRA_Control`, start with the empty A4 sheet and add circuits as development progresses.

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

- Verify electrical connections and coordinate protection thresholds with load requirements.
- Draw and review the control and matrix circuits in `MIRA_Control`.
- Complete consistent schematic formatting and descriptions.
- Review component suitability and availability.
- Prepare component placement and PCB routing.
