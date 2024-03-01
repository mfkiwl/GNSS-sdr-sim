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
        IQ_s:             in IQList;
        powers:           in PowerList_t;
        IQ:               out IQ_t
    );
end Mixer;

architecture behavioral of Mixer is

begin -- force sum of powers to add up to a power of 2 -> 256


    process(clk, reset)
        variable total_i : signed(16 downto 0);
        variable total_q : signed(16 downto 0);
    begin
        if (reset = '1') then
            IQ <= (i => (others => '0'), q => (others => '0'));
        elsif rising_edge(clk) then
            
            total_I := (others => '0');
            total_Q := (others => '0');
            for n in IQ_s'range loop
                total_I := total_I + IQ_s(n).i*signed('0'&powers(n));
                total_Q := total_Q + IQ_s(n).q*signed('0'&powers(n));
            end loop;
            IQ <= (i => total_i(15 downto 8), q => total_q(15 downto 8));
        end if;
    end process;

end architecture;