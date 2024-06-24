package constelation is

  constant constelationName : string := "GlonassL1";

  constant radioFrequencyOut : integer := 1602000000;
  constant outputRate        : integer := 20000000;--15000000;

  constant RadioFrequencyIn : integer := 1602000000;
  constant InputRate        : integer := 511000;
  constant FrameSize        : integer := 10;

end package;