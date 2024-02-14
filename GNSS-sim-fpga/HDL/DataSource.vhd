library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity DataSource is
  generic(
    metaDataRate : integer := 10 -- symbol per (delay, dopler) 
  );
  port(
    reset             : in std_logic;
    clk_output        : in std_logic;
    data_out          : out std_logic;
    doppler_shift_out : out integer;
    delay_out         : out integer
  );
end DataSource;

architecture dummy1 of DataSource is
  
  constant data : std_logic_vector(0 to 199) := "01010101101010100101010101010101010101010110011001010110011001101010101001101010011010011010100101101001011010101010010101100110010101100101101001011001100101011001100101111110001101110101000010010110";
   
  signal data_output : std_logic;
  signal data_count : integer := 0;
begin
  process(clk_output, reset)
  begin
    if reset = '1' then
	  data_output <= '0';
	  delay_out <= 0;
	  data_count <= 0;
	  doppler_shift_out <= 0;
	elsif rising_edge( clk_output ) then
	  data_output <= not data_output;
	  if data_count=199 then
		data_count <= 0;
	  else
		data_count <= data_count+1;
	  end if;
	end if;
  end process;
  
  --data_out <= data_output;
  
  process(data_count)
  begin
    data_out <= data(data_count);
  end process;
end dummy1;