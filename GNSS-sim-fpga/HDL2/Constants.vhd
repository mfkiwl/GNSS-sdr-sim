library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package settings is

  --constant radioFrequencyOut : integer := 1602000000;
  --constant outputRate        : integer := 15000000;

  --constant glonassRadioFrequencyIn : integer := 1602000000;
  --constant glonassInputRate        : integer := 511000;
  --constant glonassFrameSize        : integer := 10;
  
  constant subCycles        : integer := 100;
  constant frameWidth       : integer := 176;
  constant frameBufferDepth : integer := 6;
  constant chanel_count     : integer := 1;
  constant itterNStepWidth  : integer := 64 - 8;

  subtype IQ_s_t is signed(7 downto 0);
  type IQ_t is record
    i : IQ_s_t;
    q : IQ_s_t;
  end record IQ_t;
  constant IQ_ZERO : IQ_t := (i => (others => '0'), q => (others => '0'));
  type IQList is array (chanel_count - 1 downto 0) of IQ_t;
  subtype IQ_v_t is std_logic_vector(15 downto 0);
  function IQ_to_vector(IQ: IQ_t) return IQ_v_t;
  function vector_to_IQ(vector: IQ_v_t) return IQ_t;

  subtype Power_t is unsigned(7 downto 0);
  type PowerList_t is array (chanel_count - 1 downto 0) of Power_t;
  subtype Doppler_t is integer;
  subtype PRN_t is unsigned(7 downto 0);
  subtype DelayStep_t is signed(itterNStepWidth - 1 downto 0);
  subtype Frame_t is std_logic_vector(frameWidth - 1 downto 0);
  type FrameList_t is array(chanel_count-1 downto 0) of Frame_t;

  type FrameRecord_t is record
    chanel : unsigned(7 downto 0);
    prn    : PRN_t;
    bits   : std_logic_vector(63 downto 0);
    delay_step: DelayStep_t; -- chainge in delay per sample
    phase_step: Doppler_t; -- unsigned(31 downto 0)
    power  : Power_t;
  end record FrameRecord_t;

  function frame_to_record(frame: Frame_t) return FrameRecord_t;
  function record_to_frame(frame_record: FrameRecord_t) return Frame_t;

  constant ENABLED  : std_logic := '1';
  constant DISABLED : std_logic := '0';

  constant glonassChipPeriod : time := 1.95694716243 us;

  --constant outputRate : integer := 1000000;
  --constant samplePeriode : time := 1 us;

  constant samplePeriode : time := 0.0666666667 us;

  constant PHASE_POWER      : integer := 30;
  constant PHASE_RANGE      : integer := 2 ** PHASE_POWER; -- 2^30
  constant TRIG_TABLE_POWER : integer := 8;
  constant TRIG_TABLE_SIZE  : integer := 2 ** TRIG_TABLE_POWER;

  type trigTable is array(0 to TRIG_TABLE_SIZE - 1) of unsigned(7 downto 0);
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

  function rotate_IQ(
    IQ : in IQ_t;
    phase : in unsigned(PHASE_POWER downto 0)
  ) return IQ_t;

  function To_Std_Logic(L: BOOLEAN) return std_ulogic;

end package;

package body settings is
 
  function rotate_IQ(
    IQ : in IQ_t;
    phase : in unsigned(PHASE_POWER downto 0)
  ) return IQ_t is
    variable phase_vector : std_logic_vector(phase'range);
    variable I_mult, Q_mult : signed(16 downto 0);
    variable IQ_output    : IQ_t;
    variable tableIndex   : std_logic_vector(7 downto 0);
    variable tableOp      : std_logic_vector(1 downto 0);
    variable sinPhase     : signed(8 downto 0);
    variable cosPhase     : signed(8 downto 0);
  begin
    phase_vector := std_logic_vector(phase);
    tableIndex := phase_vector(PHASE_POWER - 3 downto PHASE_POWER - TRIG_TABLE_POWER - 2);
    tableOp    := phase_vector(PHASE_POWER - 1 downto PHASE_POWER - 2);

    case tableOp is
      when "00" =>
        sinPhase :=   signed('0' & SIN_TABLE(to_integer(unsigned(tableIndex))));
        cosPhase :=   signed('0' & SIN_TABLE(to_integer(TRIG_TABLE_SIZE - 1 - unsigned(tableIndex))));
      when "01" =>
        sinPhase :=   signed('0' & SIN_TABLE(to_integer(TRIG_TABLE_SIZE - 1 - unsigned(tableIndex))));
        cosPhase := - signed('0' & SIN_TABLE(to_integer(unsigned(tableIndex))));
      when "10" =>
        sinPhase := - signed('0' & SIN_TABLE(to_integer(unsigned(tableIndex))));
        cosPhase := - signed('0' & SIN_TABLE(to_integer(TRIG_TABLE_SIZE - 1 - unsigned(tableIndex))));
      when "11" =>
        sinPhase := - signed('0' & SIN_TABLE(to_integer(TRIG_TABLE_SIZE - 1 - unsigned(tableIndex))));
        cosPhase :=   signed('0' & SIN_TABLE(to_integer(unsigned(tableIndex))));
      when others =>
        sinPhase := to_signed(0, 9);
        cosPhase := to_signed(255, 9);
    end case;

    I_mult := (cosPhase * IQ.i + sinPhase * IQ.q);
    Q_mult := (sinPhase * IQ.i + cosPhase * IQ.q);
      
    IQ_output := (i => I_mult(15 downto 8), q => Q_mult(15 downto 8));
		return IQ_output;
  end;

  function frame_to_record(frame: Frame_t) return FrameRecord_t is
    variable res: FrameRecord_t;
  begin
    res.chanel     :=            unsigned( frame(frame'HIGH                           downto frame'HIGH-8                           +1 ));
    res.prn        :=            unsigned( frame(frame'HIGH-8                         downto frame'HIGH-8-8                         +1 ));
    res.bits       :=                      frame(frame'HIGH-8-8                       downto frame'HIGH-8-8-64                      +1  );
    res.delay_step :=              signed( frame(frame'HIGH-8-8-64                    downto frame'HIGH-8-8-64-itterNStepWidth      +1 ));
    res.phase_step := to_integer(  signed( frame(frame'HIGH-8-8-64-itterNStepWidth    downto frame'HIGH-8-8-64-itterNStepWidth-32   +1)));
    res.power      :=            unsigned( frame(frame'HIGH-8-8-64-itterNStepWidth-32 downto frame'HIGH-8-8-64-itterNStepWidth-32-8 +1 ));
    return res;
  end;

  function record_to_frame(frame_record: FrameRecord_t) return Frame_t is
    variable res: Frame_t;
  begin
    res := std_logic_vector(           frame_record.chanel     )
         & std_logic_vector(           frame_record.prn        )
         &                 (           frame_record.bits       )
         & std_logic_vector(           frame_record.delay_step )
         & std_logic_vector(to_signed( frame_record.phase_step , 32))
         & std_logic_vector(           frame_record.power      );
    return res;
  end;
  
  function IQ_to_vector(IQ: IQ_t) return IQ_v_t is
    variable res: std_logic_vector(15 downto 0);
  begin
    res := std_logic_vector(IQ.i) & std_logic_vector(IQ.q);
    return res;
  end;
  function vector_to_IQ(vector: IQ_v_t) return IQ_t is
    variable res: IQ_t;
  begin
    res.i := signed(vector(15 downto 8));
    res.q := signed(vector(7 downto 0));
    return res;
  end;

  function To_Std_Logic(L: BOOLEAN) return std_ulogic is
  begin
      if L then
          return('1');
      else
          return('0');
      end if;
  end function To_Std_Logic;

end package body settings;