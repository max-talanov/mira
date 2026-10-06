# MIRA

**MIRA is a research platform under development for experiments with memristor arrays and neuromorphic computing.**

The project aims to bring array control, an analog front end, digital processing, and software tools into a single system. It is intended for studying memristor readout and programming, vector–matrix multiplication (VMM), and spiking neuron models.

## Current status

**RevA** is currently in development. Work is focused on the power schematics: reviewing connections, protection circuits, control, and monitoring, and preparing the design for PCB layout.

Schematics in this repository do not imply that the corresponding circuits have been built or validated in hardware.

## Repository contents

The KiCad project is located in [hardware/MIRA](hardware/MIRA).

| File or directory | Purpose |
| --- | --- |
| `MIRA.kicad_pro` | KiCad project file |
| `MIRA.kicad_sch` | Top-level schematic and hierarchy navigation |
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

## Opening the project

1. Clone the repository:

   ```bash
   git clone https://github.com/max-talanov/mira.git
   ```

2. Open `hardware/MIRA/MIRA.kicad_pro` in KiCad.
3. Open the top-level schematic, `MIRA.kicad_sch`, and use the sheet hierarchy to navigate to the required block.

Keep the directory structure intact. The `sym-lib-table` and `fp-lib-table` files are stored alongside the project and reference its local libraries.

## Versioning

**RevA** identifies the hardware revision. Git tags such as `v0.1.0` mark development milestones in the repository history.

See the [commit history](https://github.com/max-talanov/mira/commits/main) for changes and the [tag list](https://github.com/max-talanov/mira/tags) for tagged versions.

## Next steps

- Verify electrical connections and coordinate protection thresholds with load requirements.
- Complete consistent schematic formatting and descriptions.
- Review component suitability and availability.
- Prepare component placement and PCB routing.
