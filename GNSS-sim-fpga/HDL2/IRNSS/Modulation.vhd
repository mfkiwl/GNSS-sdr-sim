library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.GNSSsettings.all;

--clk         : in  std_logic;
--reset       : in  std_logic;
--enable      : in  std_logic;
--enable_data : out std_logic;
--prn         : in PRN_T;
--IQ_output    : out IQ_t;
--data_input  : in  std_logic

architecture irnssL5 of Modulation is
  constant prn_len : integer := 1023;
  constant repeat_count : integer := 20;

  signal code_step      : integer range 0 to prn_len-1;
  signal repeat         : integer range 0 to repeat_count-1;


  subtype Register_t is std_logic_vector(10 downto 1);

  signal regG1 : Register_t;
  signal regG2 : Register_t;

  type Resets_t is array(0 to 14) of Register_t;
  constant G2_resets : Resets_t := ("0000000000", "1110100111", "0000100110", "1000110100", "0101110010", "1110110000", "0001101011", "0000010100", "0100110000", "0010011000", "1101100100", "0001001100", "1101111100", "1011010010", "0111101010" );

  signal G2_reset : Register_t := G2_resets(0);

begin

  process(prn)
  begin
    G2_reset <= G2_resets(to_integer(unsigned(prn)));
  end process;

  process(reset, clk)
  begin
    if reset = '1' then
      enable_data <= DISABLED;
	    code_step <= 0;
	    repeat <= 0;
	    regG1 <= "1111111111";
	    regG2 <= G2_reset;
	  elsif rising_edge( clk ) then
      
      if enable=ENABLED then

        if code_step=prn_len-1 then
          regG1 <= "1111111111";
          regG2 <= G2_reset;
        elsif code_step=0 then
          regG1 <= regG1(10-1 downto 1) & (regG1(3) xor regG1(10));
          regG2 <= G2_reset(10-1 downto 1) & (G2_reset(2) xor G2_reset(3) xor G2_reset(6) xor G2_reset(8) xor G2_reset(9) xor G2_reset(10));
        else
          regG1 <= regG1(10-1 downto 1) & (regG1(3) xor regG1(10));
          regG2 <= regG2(10-1 downto 1) & (regG2(2) xor regG2(3) xor regG2(6) xor regG2(8) xor regG2(9) xor regG2(10));
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
  process(data_input, regG1, regG2)
    variable spreading_code : std_logic;
  begin
    spreading_code := regG1(10) xor regG2(10);
    if (spreading_code xor data_input)='1' then
      IQ_output <= (to_signed(121, 8), to_signed(0, 8));
    else
      IQ_output <= (to_signed(-121, 8), to_signed(0, 8));
    end if;
  end process;
  
end irnssL5;