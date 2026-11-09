# Run: vivado -mode batch -source create_io_project.tcl -tclargs /absolute/new/output
# Prepared from UG835; not executed in Vivado in this delivery.
set task_here [file dirname [file normalize [info script]]]
if {$argc != 1} { error "Provide one new output directory in -tclargs" }
set task_out [file normalize [lindex $argv 0]]
if {[file exists $task_out]} { error "Output already exists: $task_out" }
if {[llength [get_parts -quiet xc7z020clg484-1]] != 1} {
    error "Install Zynq-7000 device support for xc7z020clg484-1"
}
create_project mira_io $task_out -part xc7z020clg484-1
set_property design_mode PinPlanning [current_fileset]
open_io_design -name mira_io
create_port -direction INOUT {FX_D0}
create_port -direction INOUT {FX_D1}
create_port -direction INOUT {FX_D2}
create_port -direction INOUT {FX_D3}
create_port -direction INOUT {FX_D4}
create_port -direction OUT {FX_SLCS_N}
create_port -direction OUT {FX_PKTEND}
create_port -direction INOUT {FX_D5}
create_port -direction INOUT {FX_D6}
create_port -direction INOUT {FX_D7}
create_port -direction INOUT {FX_D8}
create_port -direction INOUT {FX_D9}
create_port -direction INOUT {FX_D10}
create_port -direction INOUT {FX_D11}
create_port -direction INOUT {FX_D12}
create_port -direction INOUT {FX_D13}
create_port -direction OUT {FX_A0}
create_port -direction OUT {FX_A1}
create_port -direction INOUT {FX_D14}
create_port -direction INOUT {FX_D15}
create_port -direction IN {FX_FLAGB}
create_port -direction OUT {FX_PCLK}
create_port -direction OUT {FX_SLWR_N}
create_port -direction OUT {FX_SLRD_N}
create_port -direction INOUT {FX_D16}
create_port -direction INOUT {FX_D17}
create_port -direction INOUT {FX_D18}
create_port -direction INOUT {FX_D19}
create_port -direction INOUT {FX_D20}
create_port -direction INOUT {FX_D21}
create_port -direction INOUT {FX_D22}
create_port -direction INOUT {FX_D23}
create_port -direction INOUT {FX_D24}
create_port -direction OUT {FX_SLOE_N}
create_port -direction IN {FX_FLAGA}
create_port -direction INOUT {FX_D25}
create_port -direction INOUT {FX_D26}
create_port -direction INOUT {FX_D27}
create_port -direction INOUT {FX_D28}
create_port -direction INOUT {FX_D29}
create_port -direction INOUT {FX_D30}
create_port -direction INOUT {FX_D31}
create_port -direction OUT {ADC_CNV}
create_port -direction OUT {ADC_SCK}
create_port -direction OUT {ADC_SDI}
create_port -direction OUT {ADC_RESET_N}
create_port -direction OUT {ADC_CS_N0}
create_port -direction IN {DAC_SDO1}
create_port -direction IN {DAC_SDO2}
create_port -direction OUT {ADC_CS_N1}
create_port -direction OUT {ADC_CS_N2}
create_port -direction OUT {ADC_CS_N3}
create_port -direction OUT {ADC_CS_N4}
create_port -direction OUT {ADC_CS_N5}
create_port -direction OUT {ADC_CS_N6}
create_port -direction OUT {ADC_CS_N7}
create_port -direction IN {ADC_SDO0}
create_port -direction IN {ADC_SDO1}
create_port -direction IN {DAC_SDO3}
create_port -direction IN {ADC_SDO2}
create_port -direction IN {ADC_SDO3}
create_port -direction IN {ADC_SDO4}
create_port -direction IN {ADC_SDO5}
create_port -direction IN {ADC_SDO6}
create_port -direction IN {ADC_SDO7}
create_port -direction OUT {DAC_SCLK}
create_port -direction OUT {DAC_LDAC_N}
create_port -direction OUT {DAC_CLR}
create_port -direction OUT {DAC_SDI0}
create_port -direction OUT {DAC_SDI1}
create_port -direction OUT {DAC_SDI2}
create_port -direction OUT {DAC_SDI3}
create_port -direction OUT {DAC_CS_N0}
create_port -direction OUT {DAC_CS_N1}
create_port -direction OUT {DAC_CS_N2}
create_port -direction OUT {DAC_CS_N3}
create_port -direction IN {DAC_SDO0}
create_port -direction OUT {WL_REQ0}
create_port -direction OUT {WL_REQ1}
create_port -direction OUT {WL_REQ2}
create_port -direction OUT {WL_REQ3}
create_port -direction OUT {WL_REQ4}
create_port -direction IN {FPGA_CS_N}
create_port -direction OUT {WL_REQ5}
create_port -direction OUT {WL_REQ6}
create_port -direction OUT {WL_REQ7}
create_port -direction OUT {WL_REQ8}
create_port -direction OUT {WL_REQ9}
create_port -direction OUT {WL_REQ10}
create_port -direction OUT {WL_REQ11}
create_port -direction OUT {WL_REQ12}
create_port -direction OUT {WL_REQ13}
create_port -direction IN {FPGA_SCK}
create_port -direction IN {FPGA_MOSI}
create_port -direction OUT {WL_REQ14}
create_port -direction OUT {WL_REQ15}
create_port -direction OUT {FPGA_MISO}
create_port -direction OUT {Z_IRQ}
create_port -direction OUT {WL_REQ16}
create_port -direction OUT {WL_REQ17}
create_port -direction OUT {WL_REQ18}
create_port -direction OUT {WL_REQ19}
create_port -direction OUT {WL_REQ20}
create_port -direction OUT {WL_REQ21}
create_port -direction OUT {WL_REQ22}
create_port -direction OUT {WL_REQ23}
create_port -direction OUT {WL_REQ24}
create_port -direction OUT {WL_REQ25}
create_port -direction OUT {WL_REQ26}
create_port -direction OUT {WL_REQ27}
create_port -direction OUT {WL_REQ28}
create_port -direction OUT {WL_REQ29}
create_port -direction OUT {WL_REQ30}
create_port -direction OUT {WL_REQ31}
create_port -direction OUT {MAT_SPI_MOSI}
create_port -direction OUT {MAT_SPI_SCK}
create_port -direction OUT {MAT_SPI_LATCH}
create_port -direction OUT {MAT_SPI_OE_N}
create_port -direction OUT {MAT_SERVICE_EN_REQ}
create_port -direction OUT {FAULT_LOAD_N}
create_port -direction OUT {GLOBAL_ARM_CLK}
create_port -direction OUT {MAT_READ_EN_REQ}
create_port -direction OUT {MAT_WRITE_EN_REQ}
create_port -direction OUT {MAT_VMM_EN_REQ}
create_port -direction OUT {MAT_POLARITY_REQ}
create_port -direction OUT {FORM_BL_A0}
create_port -direction OUT {FORM_BL_A1}
create_port -direction OUT {FORM_BL_A2}
create_port -direction OUT {FORM_BL_A3}
create_port -direction OUT {FORM_BL_A4}
create_port -direction OUT {RUN_REQ}
create_port -direction OUT {FORM_PULSE_REQ}
create_port -direction OUT {FORM_NL_A0}
create_port -direction OUT {FORM_NL_A1}
create_port -direction OUT {SERVICE_CS_N}
create_port -direction OUT {WL_ENABLE_REQ}
create_port -direction OUT {FORM_WL_A0}
create_port -direction OUT {FORM_WL_A1}
create_port -direction OUT {FORM_WL_A2}
create_port -direction OUT {FORM_WL_A3}
create_port -direction OUT {FORM_WL_A4}
create_port -direction OUT {FORM_NL_A2}
create_port -direction OUT {FORM_NL_A3}
create_port -direction OUT {FORM_NL_A4}
create_port -direction OUT {FAULT_CLEAR_REQ}
create_port -direction IN {FAULT_LATCHED}
create_port -direction IN {FAULT_MAP_SDO}
create_port -direction IN {SERVICE_READY}
read_xdc [file join $task_here pl-candidate.xdc]
report_io -file [file join $task_out io.rpt]
report_drc -file [file join $task_out io-drc.rpt]
write_xdc [file join $task_out io-exported.xdc]
write_verilog -force [file join $task_out io-top.v]
# Persist the generated port declarations for reopening this I/O planning project.
add_files [file join $task_out io-top.v]
add_files -fileset constrs_1 [file join $task_out io-exported.xdc]
puts "I/O project saved. Inspect io-drc.rpt. This is NOT MIG validation or timing closure."
close_project
