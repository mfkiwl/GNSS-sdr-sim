library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity SPI is
    generic (
        n_in  : integer := 4;
        n_out : integer := 4
    );
    port(
        clk:              in std_logic;
        reset:            in std_logic;

        serial_in:        in std_logic;
        parallel_out:     out std_logic_vector(n_out-1 downto 0);

        parallel_in:      in std_logic_vector(n_in-1 downto 0);
        serial_out:       out std_logic--;
		  
		  --debug: out std_logic_vector(7 downto 0)
    );
end SPI;

architecture behavioral of SPI is
  signal reg: std_logic_vector(n_out-1 downto 0) := (others => '0');
  signal reg_send: std_logic_vector(n_in-1 downto 0) := (others => '0');
  signal index: integer range n_in-1 downto 0;
  signal test : std_logic := '0';
begin
    parallel_out <= reg;
    serial_out <= reg_send(n_in-1-index);
    
	 --debug(0) <= clk;
	 --debug(1) <= reset;
	 --debug(2) <= test;
	 --debug(3) <= not (clk or (not test) or reset);
	 --debug(7 downto 4) <= (others => '0');
    --debug <= parallel_out;


    process (clk)
    begin
        
        if falling_edge(clk) then
				if (reset = '1') then
					reg_send <= parallel_in; -- or 0?
					index <= 0;
					test <= '1';
				else
					test <= not test;
					if (index=n_in-1) then
					  index <= 0;
					  reg_send <= parallel_in;
					else
					  index <= index+1;
					end if;
				end if;
        end if;
    end process;
	 
	 process (clk)
    begin
      if rising_edge(clk) then
        if (reset = '1') then
          reg <= (others => '0');
		  else
          reg <= reg(n_out-2 downto 0) & serial_in;
		  end if;
      end if;
    end process;
end behavioral;