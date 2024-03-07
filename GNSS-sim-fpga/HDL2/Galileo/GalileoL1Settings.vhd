library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package constelation is

  constant constelationName : string := "GalileoL1";

  constant radioFrequencyOut : integer := 1575420000;
  constant outputRate        : integer := 15000000;

  constant RadioFrequencyIn : integer := 1575420000;
  constant InputRate        : integer := 12276000;
  constant FrameSize        : integer := 25;

end package;