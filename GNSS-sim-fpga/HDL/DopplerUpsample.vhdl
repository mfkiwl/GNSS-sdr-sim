library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity DopplerUpsample is
  generic(
    radioFrequencyOut : integer := 1575420000;
    radioFrequencyIn  : integer := 1575420000;
    inputRate         : integer := 511000;
    outputRate        : integer := 20000000;
    subCycles         : integer := 1
  ); 
  port (
    reset      : in std_logic;
    
    clk_output : in  std_logic;
    I_output   : out integer;
    Q_output   : out integer;

    clk_input  : out std_logic;
    I_input    : in integer;
    Q_input    : in integer;

    doppler_shift : in integer;
    delay         : in integer
  );
end DopplerUpsample;

architecture arch1 of DopplerUpsample is

  constant PHASE_POWER : integer := 30;
  constant PHASE_RANGE : integer := 2**PHASE_POWER; -- 2^30
  constant TABLE_POWER : integer := 8;
  constant TABLE_SIZE  : integer := 2**TABLE_POWER;
  
  type trigTable is array(0 to TABLE_SIZE-1) of unsigned(7 downto 0);
  constant SIN_TABLE : trigTable := (
X"00", X"01", X"03", X"04", X"06", X"07", X"09", X"0a", X"0c", X"0e", X"0f", X"11", X"12", X"14", X"15", X"17",
X"18", X"1a", X"1c", X"1d", X"1f", X"20", X"22", X"23", X"25", X"26", X"28", X"2a", X"2b", X"2d", X"2e", X"30",
X"31", X"33", X"34", X"36", X"37", X"39", X"3a", X"3c", X"3d", X"3f", X"40", X"42", X"44", X"45", X"47", X"48",
X"4a", X"4b", X"4d", X"4e", X"4f", X"51", X"52", X"54", X"55", X"57", X"58", X"5a", X"5b", X"5d", X"5e", X"60",
X"61", X"63", X"64", X"65", X"67", X"68", X"6a", X"6b", X"6d", X"6e", X"6f", X"71", X"72", X"74", X"75", X"76",
X"78", X"79", X"7a", X"7c", X"7d", X"7f", X"80", X"81", X"83", X"84", X"85", X"87", X"88", X"89", X"8b", X"8c",
X"8d", X"8e", X"90", X"91", X"92", X"94", X"95", X"96", X"97", X"99", X"9a", X"9b", X"9c", X"9e", X"9f", X"a0",
X"a1", X"a2", X"a4", X"a5", X"a6", X"a7", X"a8", X"aa", X"ab", X"ac", X"ad", X"ae", X"af", X"b0", X"b2", X"b3",
X"b4", X"b5", X"b6", X"b7", X"b8", X"b9", X"ba", X"bb", X"bc", X"bd", X"bf", X"c0", X"c1", X"c2", X"c3", X"c4",
X"c5", X"c6", X"c7", X"c8", X"c9", X"c9", X"ca", X"cb", X"cc", X"cd", X"ce", X"cf", X"d0", X"d1", X"d2", X"d3",
X"d4", X"d4", X"d5", X"d6", X"d7", X"d8", X"d9", X"d9", X"da", X"db", X"dc", X"dd", X"dd", X"de", X"df", X"e0",
X"e0", X"e1", X"e2", X"e3", X"e3", X"e4", X"e5", X"e5", X"e6", X"e7", X"e7", X"e8", X"e9", X"e9", X"ea", X"ea",
X"eb", X"ec", X"ec", X"ed", X"ed", X"ee", X"ef", X"ef", X"f0", X"f0", X"f1", X"f1", X"f2", X"f2", X"f3", X"f3",
X"f4", X"f4", X"f4", X"f5", X"f5", X"f6", X"f6", X"f6", X"f7", X"f7", X"f8", X"f8", X"f8", X"f9", X"f9", X"f9",
X"fa", X"fa", X"fa", X"fa", X"fb", X"fb", X"fb", X"fc", X"fc", X"fc", X"fc", X"fc", X"fd", X"fd", X"fd", X"fd",
X"fd", X"fd", X"fe", X"fe", X"fe", X"fe", X"fe", X"fe", X"fe", X"fe", X"fe", X"fe", X"fe", X"fe", X"fe", X"fe"
   );
  
  signal n : integer;
  signal itterNStep : integer;
  signal bufferNStep : integer;

  signal unitPhase : integer;
  signal unitPhaseStep : integer;

  signal lastDelay : integer;
  signal lastDoppler : integer;
  
  signal tableIndex : std_logic_vector(7 downto 0);
  signal tableOp : std_logic_vector(1 downto 0);
  signal sinPhase : integer :=0;
  signal cosPhase : integer :=0;
  
begin

  process( clk_output, reset, doppler_shift, delay )
    variable next_n : integer;
	variable phase : integer;
	variable phase_vector : std_logic_vector(31 downto 0);
  begin
    next_n := n;
	phase := unitPhase;
    if reset = '1' then
      itterNStep <= subCycles * inputRate;
      bufferNStep <= subCycles * outputRate;
      next_n := 0;
      phase  := 0;
      unitPhaseStep <= (radioFrequencyIn + doppler_shift - radioFrequencyOut) * (PHASE_RANGE/outputRate);
      lastDelay <= delay;
      next_n := next_n-delay;
      clk_input <= '0';
      
    elsif rising_edge( clk_output ) then
	  
	  phase_vector := std_logic_vector(to_signed(phase, 32));
	  tableIndex <= phase_vector(PHASE_POWER-3 downto PHASE_POWER-TABLE_POWER-2);
	  tableOp    <= phase_vector(PHASE_POWER-1 downto PHASE_POWER-2);
	  
	  case tableOp is
	    when "00" =>
		  sinPhase <= to_integer(SIN_TABLE(to_integer(unsigned(tableIndex))));
		  cosPhase <= to_integer(SIN_TABLE(to_integer(TABLE_SIZE-1-unsigned(tableIndex))));
		when "01" =>
		  sinPhase <= to_integer(SIN_TABLE(to_integer(TABLE_SIZE-1-unsigned(tableIndex))));
		  cosPhase <= -to_integer(SIN_TABLE(to_integer(unsigned(tableIndex))));
		when "10" =>
		  sinPhase <= -to_integer(SIN_TABLE(to_integer(unsigned(tableIndex))));
		  cosPhase <= -to_integer(SIN_TABLE(to_integer(TABLE_SIZE-1-unsigned(tableIndex))));
		when "11" =>
		  sinPhase <= -to_integer(SIN_TABLE(to_integer(TABLE_SIZE-1-unsigned(tableIndex))));
		  cosPhase <= to_integer(SIN_TABLE(to_integer(unsigned(tableIndex))));
		when others =>
		  sinPhase <= 0;
	  end case;
	  
      I_output <= (cosPhase*I_input + sinPhase*Q_input)/256;
      Q_output <= (sinPhase*I_input + cosPhase*Q_input)/256;

      next_n := next_n + itterNStep;
      phase := phase+unitPhaseStep;
	  if (phase >= PHASE_RANGE) then
			phase := phase - PHASE_RANGE;
	  elsif (unitPhase < 0) then
			phase := phase + PHASE_RANGE;
	  end if;
	  
      if (next_n >= bufferNStep) then
        clk_input <= '1';
        next_n := next_n - bufferNStep;
      end if;

    elsif falling_edge( clk_output ) then
      clk_input <= '0';
    
    elsif lastDelay /= delay then
      next_n := next_n + lastDelay - delay;
      lastDelay <= delay;
    
    elsif lastDoppler /= doppler_shift then
      unitPhaseStep <= (radioFrequencyIn + doppler_shift - radioFrequencyOut) * (PHASE_RANGE/outputRate);
    
    end if;
    n <= next_n;
	unitPhase <= phase;
  end process;

end arch1;