library ieee;
use ieee.std_logic_1164.all;

package settings is
    constant frameWidth: integer := 176;
    constant chanel_count: integer := 4;

    type IQList is array (chanel_count-1 downto 0) of std_logic_vector(7 downto 0);
end package;