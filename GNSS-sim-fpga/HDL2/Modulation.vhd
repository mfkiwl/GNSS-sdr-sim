library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.settings.all;

entity Modulation is
  port(
    clk         : in  std_logic;
    reset       : in  std_logic;
    enable      : in  std_logic;
    enable_data : out std_logic;

    prn         : in PRN_T;

    IQ_output    : out IQ_t;
    data_input  : in  std_logic
  );
end Modulation;
