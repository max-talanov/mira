# Run: vivado -mode batch -source create_io_project.tcl -tclargs /absolute/new/output
# Prepared from UG835; not executed in Vivado in this delivery.
set task_here [file dirname [file normalize [info script]]]
if {$argc != 1} { error "Provide one new output directory in -tclargs" }
set task_out [file normalize [lindex $argv 0]]
if {[file exists $task_out]} { error "Output already exists: $task_out" }
if {[llength [get_parts -quiet xc7a200tfbg484-2]] != 1} {
    error "Install Artix-7 device support for xc7a200tfbg484-2"
}
create_project mira_io $task_out -part xc7a200tfbg484-2
set_property design_mode PinPlanning [current_fileset]
open_io_design -name mira_io
source [file join $task_here ports.tcl]
read_xdc [file join $task_here mira_pinout_candidate.xdc]
report_io -file [file join $task_out io.rpt]
report_drc -file [file join $task_out io-drc.rpt]
write_xdc [file join $task_out io-exported.xdc]
write_verilog -force [file join $task_out io-top.v]
# Persist the generated port declarations for reopening this I/O planning project.
add_files [file join $task_out io-top.v]
add_files -fileset constrs_1 [file join $task_out io-exported.xdc]
puts "I/O project saved. Inspect io-drc.rpt. This is NOT MIG validation or timing closure."
close_project
