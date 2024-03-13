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

architecture beidouL1 of Modulation is
  constant prn_len : integer := 2046;
  constant repeat_count : integer := 20;

  signal code_step      : integer range 0 to prn_len-1;
  signal repeat         : integer range 0 to repeat_count-1;

  signal regG1 : std_logic_vector(11 downto 1);
  signal regG2 : std_logic_vector(11 downto 1);

  type Taps_t is array(0 to 37) of integer range 1 to 11;
  --                          x  1  2 ...
  constant taps1 : Taps_t := (1, 1, 1, 1, 1, 1, 1,  1,  1, 2, 3, 3, 3, 3, 3,  3,  3, 4, 4, 4, 4, 4,  4,  5, 5, 5, 5,  5,  6, 6, 6,  6,  8, 8,  8,  9,  9,  10);
  constant taps2 : Taps_t := (1, 3, 4, 5, 6, 8, 9, 10, 11, 7, 4, 5, 6, 8, 9, 10, 11, 5, 6, 8, 9, 10, 11, 6, 8, 9, 10, 11, 8, 9, 10, 11, 9, 10, 11, 10, 11, 11);

  signal tap1 : integer := 1;
  signal tap2 : integer := 1;


  constant NH_code : std_logic_vector(0 to 19) := "00000100110101001110";

begin

  process(prn)
  begin
    tap1 <= taps1(to_integer(prn));
    tap2 <= taps2(to_integer(prn));
  end process;

  process(reset, clk)
  begin
    if reset = '1' then
      enable_data <= DISABLED;
	    code_step <= 0;
	    repeat <= 0;
	    regG1 <= "01010101010";
	    regG2 <= "01010101010";
	  elsif rising_edge( clk ) then
      
      if enable=ENABLED then

        if code_step=prn_len-1 then
          regG1 <= "01010101010";
          regG2 <= "01010101010";
        else
          regG1 <= regG1(11-1 downto 1) & (regG1(1) xor regG1(7) xor regG1(8) xor regG1(9) xor regG1(10) xor regG1(11));
          regG2 <= regG2(11-1 downto 1) & (regG2(1) xor regG2(2) xor regG2(3) xor regG2(4) xor regG2(5) xor regG2(8) xor regG2(9) xor regG2(11));
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
  -- todo: add NH code
  process(data_input, regG1, regG2, repeat, tap1, tap2)
  begin
    if (regG1(11) xor regG2(tap1) xor regG2(tap2) xor NH_code(repeat) xor data_input)='1' then
      IQ_output <= (to_signed(121, 8), to_signed(0, 8));
    else
      IQ_output <= (to_signed(-121, 8), to_signed(0, 8));
    end if;
  end process;
  
end beidouL1;