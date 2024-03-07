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

architecture galileoL1 of Modulation is
  constant step_count : integer := 12;
  constant prn_len : integer := 4092;
  constant repeat_count : integer := 1;

  signal sc_step        : integer range 0 to step_count-1;
  signal code_step      : integer range 0 to prn_len-1;
  signal repeat         : integer range 0 to repeat_count-1;
  signal sec_bit        : integer range 0 to 25-1;

  type SubCarrier_t is array(0 to step_count) of signed(7 downto 0);
  constant SubCarrier_data  : SubCarrier_t := (251, 130, 251, 130, 251, 130, -130, -151, -130, -151, -130, -151);
  constant SubCarrier_pilot : SubCarrier_t := (130, 251, 130, 251, 130, 251, -251, -130, -251, -130, -251, -130);

  type MemCodes_t is array(0 to 37) of std_logic_vector(prn_len-1 downto 0);
  constant MemoryCodes_data  : MemCodes_t := ();
  constant MemoryCodes_pilot : MemCodes_t := ();

  constant SecondaryCode : std_logic_vector(24 downto 0);

begin

  process(reset, clk)
  begin
    if reset = '1' then
      enable_data <= DISABLED;
      sc_step   <= 0;
	    code_step <= 0;
	    repeat    <= 0;
	  elsif rising_edge( clk ) then
      
      if enable=ENABLED then

        --if code_step=prn_len-1 then
          -- reset
        --else
          -- next
        --end if;

        -- if we need a new data bit next time already request it
        if repeat=repeat_count-1 and code_step=prn_len-1 then
          enable_data <= ENABLED;
        else
          enable_data <= DISABLED;
        end if;
        
        if sc_step=step_count-1 then
          sc_step <= 0;
          -- set the code step and repeat index for the next clock cycle
          if code_step=prn_len-1 then -- loop over prn
            code_step <= 0;
            if repeat=repeat_count-1 then -- not all prn repetitions need a new bit
              repeat <= 0;
              if sec_bit=SecondaryCode'length-1 then
                sec_bit <= 0;
              else
                sec_bit <= sec_bit+1;
              end if;
            else
              repeat <= repeat+1;
            end if;
          else
            code_step <= code_step+1;
          end if;
        else
          sc_step <= sc_step+1;
        end if;

      else
        -- make shure we only request data once
        enable_data <= DISABLED;
      end if;
    end if;
  end process;
  
  -- output the for the value currently in the shift register/current spreading code
  process(data_input, sc_step, code_step, repeat, prn)
    variable data : signed(7 downto 0);
    variable pilot : signed(7 downto 0);
  begin
    if (MemoryCodes_data(prn)(code_step) xor SecondaryCode(sec_bit) xor data_input)='1' then
      data := (SubCarrier_data(sc_step), to_signed(0, 8));
    else
      data := (-SubCarrier_data(sc_step), to_signed(0, 8));
    end if;

    if (MemoryCodes_pilot(prn)(code_step))='1' then
      data := (SubCarrier_pilot(sc_step), to_signed(0, 8));
    else
      data := (-SubCarrier_pilot(sc_step), to_signed(0, 8));
    end if;

    IQ_output <= (data+pilot)/2;
  end process;
  
end gpsL1;