library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package constelation is

  constant constelationName : string := "BeiDouL1c";

  constant radioFrequencyOut : integer := 1561098000;
  constant outputRate        : integer := 2046000;--2600000;

  constant RadioFrequencyIn : integer := 1561098000;
  constant InputRate        : integer := 2046000;
  constant FrameSize        : integer := 5; -- only D1 (prn>=6)

end package;