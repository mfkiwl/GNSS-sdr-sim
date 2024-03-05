
# PlanAhead Launch Script for Pre-Synthesis Floorplanning, created by Project Navigator

create_project -name ISE2 -dir "/home/mike/Desktop/Thesis/GNSS-sdr-sim/GNSS-sim-fpga/ISE2/planAhead_run_4" -part xc3s1200efg320-4
set_param project.pinAheadLayout yes
set srcset [get_property srcset [current_run -impl]]
set_property target_constrs_file "/home/mike/Desktop/Thesis/GNSS-sdr-sim/GNSS-sim-fpga/Top.ucf" [current_fileset -constrset]
set hdlfile [add_files [list {../HDL2/Constants.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../HDL2/Modulation.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../HDL2/ModConst.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../HDL2/FrameHandler.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../HDL2/DopplerUpsample.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../HDL2/Mixer.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../HDL2/communication/FIFO.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../HDL2/Chanel.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../HDL2/communication/SPI.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../HDL2/communication/ClockDiv16.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../HDL2/ChanelsHandler.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set hdlfile [add_files [list {../HDL2/Top.vhd}]]
set_property file_type VHDL $hdlfile
set_property library work $hdlfile
set_property top Top $srcset
add_files [list {/home/mike/Desktop/Thesis/GNSS-sdr-sim/GNSS-sim-fpga/Top.ucf}] -fileset [get_property constrset [current_run]]
open_rtl_design -part xc3s1200efg320-4
