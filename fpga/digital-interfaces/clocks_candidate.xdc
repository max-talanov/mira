# MIRA.04 pin assignment candidate. Derived from native KiCad netlist.
# NOT generated or validated by MIG; not a complete timing constraint set.
# Do not use as a substitute for the MIG-generated PHY constraints.
# Planning clocks only. Full I/O min/max delays require RTL and PCB timing.
create_clock -name sys_clk -period 5.000 [get_ports sys_clk_p]
create_clock -name ft_clk -period 10.000 [get_ports FT_CLK]
create_clock -name rgmii_rxc -period 8.000 [get_ports PHY_RXC]
create_clock -name mcu_spi_sck -period 40.000 [get_ports MCU_FPGA_SCK_F]
# No false paths or CLOCK_DEDICATED_ROUTE overrides are supplied.
# RGMII TX clock and DDR CK are generated clocks: let the implementation define them.
