library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.settings.all;

--clk         : in  std_logic;
--reset       : in  std_logic;
--enable      : in  std_logic;
--enable_data : out std_logic;
--prn         : in PRN_T;
--IQ_output    : out IQ_t;
--data_input  : in  std_logic

architecture glonassL1 of Modulation is
  constant prn_len : integer := 511;
  constant repeat_count : integer := 10;

  signal code_step      : integer range 0 to prn_len-1;
  signal repeat         : integer range 0 to repeat_count-1;
  signal shift_register : std_logic_vector(9 downto 1);

begin

  process(reset, clk)
  begin
    if reset = '1' then
      enable_data <= DISABLED;
	    code_step <= 0;
	    repeat <= 0;
	    shift_register <= "111111111";
	  elsif rising_edge( clk ) then
      
      if enable=ENABLED then

        if code_step=prn_len-1 then
          shift_register <= "111111111";
        else
          shift_register <= shift_register(9-1 downto 1) & (shift_register(5) xor shift_register(9));
        end if;

        -- if we need a new data bit next time already request it
        if repeat=repeat_count-1 and code_step=prn_len-2 then
          enable_data <= ENABLED;
        else
          enable_data <= DISABLED;
        end if;
        
        -- set the code step and repeat index for the next clock cycle
        if code_step=prn_len-1 then -- loop over prn
          code_step <= 0;
          if repeat=repeat_count-1 then -- not all prn repetitions need a new bit
            repeat <= 0;
          else
            repeat <= repeat+1;
          end if;
        else
          code_step <= code_step+1;
        end if;
        

      else
        -- make shure we only request data once
        enable_data <= DISABLED;
      end if;
    end if;
  end process;
  
  -- output the for the value currently in the shift register/current spreading code
  process(data_input, shift_register)
    variable spreading_code : std_logic;
  begin
    spreading_code := shift_register(7);
    if (shift_register(7) xor data_input)='1' then
      IQ_output <= (to_signed(-121, 8), to_signed(0, 8));
    else
      IQ_output <= (to_signed(121, 8), to_signed(0, 8));
    end if;
  end process;
  
end glonassL1;