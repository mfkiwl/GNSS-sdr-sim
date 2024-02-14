library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity SPI_helper is
    generic (
        n  : integer := 4;
        clk_period : time := 1 us
    );
    port(
        word: in std_logic_vector(n-1 downto 0);
        done: out std_logic := '0';

        clk: out std_logic;
        serial_out: out std_logic
    );
end entity;

architecture behavioral of SPI_helper is
begin

    process
    begin
        loop
            wait on word;
            done <= '0';

            for i in 0 to n-1 loop
                clk <= '0';
                serial_out <= word(i);
                wait for clk_period;
                clk <= '1';
                wait for clk_period;
            end loop;
            
            done <= '1';
        end loop;

    end process;

end behavioral;
