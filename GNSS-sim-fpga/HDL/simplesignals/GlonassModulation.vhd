library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.settings.all;

entity GlonassModulation is
  port(
    reset      : in std_logic;
    
    clk_output : in std_logic;
	  I_output   : out IQ;
	  Q_output   : out IQ;
	
	  clk_input  : out std_logic;
	  data_input : in std_logic
  );
end GlonassModulation;

architecture glonassL1 of GlonassModulation is
  signal code_step      : integer;
  signal repeat         : integer;
  signal shift_register : std_logic_vector(9 downto 1);
  
  signal spreading_code : std_logic;
begin

  process(clk_output, reset)
    variable step : integer;
	  variable rep  : integer;
  begin
    step := code_step;
	  rep  := repeat;
    if reset = '1' then
	    clk_input <= '0';
	    step := 0;
	    rep  :=0;
	    shift_register <= "111111111";
	  elsif rising_edge( clk_output ) then
	    shift_register <= shift_register(9-1 downto 1) & (shift_register(5) xor shift_register(9));
	    step := step+1;
	    if step=511 then
		    step := 0;
		    rep  := rep+1;
		    if rep=10 then
		      rep := 0;
		      clk_input <= '1';
		    end if;
	    end if;
	  elsif falling_edge( clk_output ) then
      clk_input <= '0';
    end if;
	  code_step <= step;
	  repeat <= rep;
  end process;
  
  
  process(clk_output, data_input, shift_register)
  begin
    spreading_code <= shift_register(7);
    Q_output <= to_signed(0, 8);
    if (shift_register(7) xor data_input)='1' then
      I_output <= to_signed(100, 8);
    else
      I_output <= to_signed(-100, 8);
    end if;
  end process;
  
end glonassL1;