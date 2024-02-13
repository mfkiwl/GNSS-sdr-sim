library ieee;
use ieee.std_logic_1164.all;

entity SPI is
    generic (
        n  : integer := 4 
    );
    port(
        clk:              in std_logic; 
        reset:            in std_logic; 
        serial_in:        in std_logic;
        parallel_out:     out std_logic_vector(n-1 downto 0)
    );
end SPI;

architecture behavioral of SPI is
  signal reg: std_logic_vector(n-1 downto 0) := (Others => '0');
begin
    parallel_out <= reg;

    process (clk,reset)
    begin
        if (reset = '1') then
            reg <= (others => '0');   
        elsif (clk'event and clk='1') then
            reg <= serial_in & reg(n-1 downto 1);
        end if;
    end process;
end behavioral;