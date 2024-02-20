library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.settings.all;

entity OutputHandler is
    port(
        clk : in std_logic;
        reset : in std_logic;
        
        serial_out : out std_logic;

        I : in IQ;
        Q : in IQ
    );
end OutputHandler;

architecture behavioral of OutputHandler is
    signal word : std_logic_vector(15 downto 0) := (others => '0');
    signal state : integer range 0 to 15;
begin

    serial_out <= word(0);

    process (reset, clk, I, Q)
    begin
        if reset = '1' then
            word <= std_logic_vector(I) & std_logic_vector(Q);
        elsif falling_edge( clk ) then
            if (state=15) then
                state <= 0;
                word <= std_logic_vector(I) & std_logic_vector(Q);
            else
                state <= state+1;
                word <= '0' & word(15 downto 1);
            end if;
        end if;
    end process;

end behavioral;