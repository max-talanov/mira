# Run in full Vivado: vivado -mode gui -source create_mig_workspace.tcl -tclargs /absolute/new/output
# Creates an unconfigured IP. Read README.md and mig-settings.json before customization.
set task_here [file dirname [file normalize [info script]]]
if {$argc != 1} { error "Provide one new output directory in -tclargs" }
set task_out [file normalize [lindex $argv 0]]
if {[file exists $task_out]} { error "Output already exists: $task_out" }
create_project mira_ddr3l $task_out -part xc7a200tfbg484-2
set_property target_language Verilog [current_project]
set task_ips [get_ipdefs -all -quiet xilinx.com:ip:mig_7series:*]
if {[llength $task_ips] == 0} { error "7-series MIG IP is unavailable in this installation" }
create_ip -vlnv [lindex [lsort -dictionary $task_ips] end] -module_name mira_ddr3l
puts "Unconfigured MIG workspace created. Customize mira_ddr3l using mig-settings.json and the pin-map CSV."
puts "Do not generate an unchanged default IP: it has NOT been configured for this board."
