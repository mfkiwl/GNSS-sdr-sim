library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package constelation is

  constant constelationName : string := "GPSL1";

  constant radioFrequencyOut : integer := 1575420000;
  constant outputRate        : integer := 1023000;--2600000;

  constant RadioFrequencyIn : integer := 1575420000;
  constant InputRate        : integer := 1023000;
  constant FrameSize        : integer := 5;

end package;