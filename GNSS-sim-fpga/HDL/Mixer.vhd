library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.settings.all;

entity Mixer is
    generic(
        chanel_count : integer := 4
    );
    port(
        clk:              in std_logic; 
        reset:            in std_logic; 
        I_s:              in IQList;
        Q_s:              in IQList;
        powers:           in PowerList_t;
        I:                out IQ;
        Q:                out IQ
    );
end Mixer;

architecture behavioral of Mixer is

begin -- force sum of powers to add up to a power of 2 -> 256


    process(clk, reset)
        variable total_i : signed(16 downto 0);
        variable total_q : signed(16 downto 0);
    begin
        if (reset = '1') then
            I <= (others => '0');
            Q <= (others => '0');
        elsif falling_edge(clk) then
            
            total_I := (others => '0');
            total_Q := (others => '0');
            for n in I_s'range loop
                total_I := total_I + I_s(n)*signed('0'&powers(n));
                total_Q := total_Q + Q_s(n)*signed('0'&powers(n));
            end loop;
            I <= total_i(15 downto 8);
            Q <= total_q(15 downto 8);
        end if;
    end process;

end architecture;