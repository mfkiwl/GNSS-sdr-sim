library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;

package settings is
    constant frameWidth: integer := 176;
    constant chanel_count: integer := 4;
    
    subtype IQ is signed(7 downto 0);
    type IQList is array (chanel_count-1 downto 0) of IQ;

    
    subtype Power_t is unsigned(7 downto 0);
    type PowerList_t is array (chanel_count-1 downto 0) of Power_t;

end package;