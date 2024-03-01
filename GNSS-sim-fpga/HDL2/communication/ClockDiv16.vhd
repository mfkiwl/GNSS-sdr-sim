library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.settings.all;

entity ClockDiv16 is
    port(
        clk : in std_logic;
        clkdiv : out std_logic
    );
end entity;

architecture behavioral of ClockDiv16 is
    signal clk2, clk4, clk8, clk16 : std_logic := '0';
begin
    clkdiv <= clk16;

    process (clk)
    begin
        if(rising_edge(clk)) then
            clk2 <= not clk2;
        end if;
    end process;

    process (clk2)
    begin
        if(rising_edge(clk2)) then
            clk4 <= not clk4;
        end if;
    end process;

    process (clk4)
    begin
        if(rising_edge(clk4)) then
            clk8 <= not clk8;
        end if;
    end process;

    process (clk8)
    begin
        if(rising_edge(clk8)) then
            clk16 <= not clk16;
        end if;
    end process;

end behavioral;