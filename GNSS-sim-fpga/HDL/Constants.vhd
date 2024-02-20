library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;

package settings is
    constant frameWidth: integer := 176;
    constant chanel_count: integer := 1;
    
    subtype IQ is signed(7 downto 0);
    type IQList is array (chanel_count-1 downto 0) of IQ;

    
    subtype Power_t is unsigned(7 downto 0);
    type PowerList_t is array (chanel_count-1 downto 0) of Power_t;

    constant glonassChipPeriod : time := 1.95694716243 us;

    --constant outputRate : integer := 1000000;
    --constant samplePeriode : time := 1 us;
    
    constant outputRate : integer := 15000000;
    constant samplePeriode : time := 0.0666666667 us;

end package;