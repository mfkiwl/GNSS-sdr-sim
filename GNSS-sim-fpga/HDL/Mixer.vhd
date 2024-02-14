library ieee;
use ieee.std_logic_1164.all;
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
        I:                out std_logic_vector(7 downto 0);
        Q:                out std_logic_vector(7 downto 0)
    );
end Mixer;

architecture behavioral of Mixer is

begin

    I <= I_s(0);
    Q <= Q_s(0);

end architecture;