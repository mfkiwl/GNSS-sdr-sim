library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.std_logic_textio.all;
library std;
use STD.textio.all;
use work.settings.all;
use work.input.all;
use work.constelation.all;

entity Modulation_tb is
end Modulation_tb;

architecture bench of Modulation_tb is
  component Modulation
    port (
      clk : in std_logic;
      reset : in std_logic;
      enable : in std_logic;
      enable_data : out std_logic;
      prn : in PRN_T;
      IQ_output : out IQ_t;
      data_input : in std_logic
    );
  end component;

  signal clk, reset, enable : std_logic;

  signal prn : PRN_t;
  signal IQ_output : IQ_t;

  signal enable_data : std_logic;
  signal data_input : std_logic;

  FOR MOD0: Modulation USE ENTITY WORK.Modulation(gpsL1);

begin

  MOD0: Modulation port map (clk, reset, enable, enable_data, prn, IQ_output, data_input);

  process
    file prn_file      : text open write_mode is "prn_code.txt";
    variable prnLine   : line;
  begin
    clk <= '0';
    enable <= '0';

    prn <= to_unsigned(1, 8);
    data_input <= '0';

    reset <= '1';
    wait for 1 ns;
    reset <= '0';

    wait for 1 us;
    enable <= '1';
    wait for 1 us;

    
    write(prnLine, (to_integer(IQ_output.q)+100)/200);
    writeline(prn_file, prnLine);

    for k in 0 to 1023 loop
      clk <= '1';
      wait for 0.5 us;
      clk <= '0';
      write(prnLine, (to_integer(IQ_output.q)+100)/200);
      writeline(prn_file, prnLine);
      wait for 0.5 us;
    end loop;

    --file_close(prn_file);
    wait for 20 us;

    for k in 0 to 1023 loop
      clk <= '1';
      wait for 0.5 us;
      clk <= '0';
      write(prnLine, (to_integer(IQ_output.q)+100)/200);
      writeline(prn_file, prnLine);
      wait for 0.5 us;
    end loop;
  end process;
end bench;