library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.GNSSsettings.all;

entity ChanelsHandler is
  port
  (
    clk    : in std_logic;
    reset  : in std_logic;

    enable : in std_logic;
    IQ : out IQ_t;

    store  : in std_logic;
    frame : in Frame_t;

    debug  : out std_logic_vector(7 downto 0);
    debug2 : out std_logic_vector(2 downto 0)
  );
end ChanelsHandler;

architecture structural of ChanelsHandler is
  component FIFO
    generic (
      width : integer := frameWidth;
      depth : integer := frameBufferDepth
    );
    port (
      reset : in std_logic;
      clk_push : in std_logic;
      enable_push : in std_logic;
      clk_pop : in std_logic;
      enable_pop : in std_logic;
      Q : in std_logic_vector(width-1 downto 0);
      D : out std_logic_vector(width-1 downto 0);
      D2 : out std_logic_vector(width-1 downto 0)
    );
  end component;

  component Chanel
    port (
      clk : in std_logic;
      reset : in std_logic;
      enable : in std_logic;
      enable_next_frame : out std_logic;
      next_frame : in Frame_t;
      peek_frame : in Frame_t;
      IQ : out IQ_t;
      power : out Power_t
    );
  end component;

  component Mixer
    generic (
      chanel_count : integer := chanel_count
    );
    port (
      clk : in std_logic;
      reset : in std_logic;
      IQ_s : in IQList;
      powers : in PowerList_t;
      IQ : out IQ_t
    );
  end component;



  signal IQ_s : IQList;

  signal power_s : PowerList_t;

  signal push : std_logic_vector(chanel_count-1 downto 0);-- := (others => '0');
  signal pop  : std_logic_vector(chanel_count-1 downto 0) := (others => '0');

  signal frame_record : FrameRecord_t;
  signal frames : FrameList_t;
  signal peek_frames : FrameList_t;

  signal chanel_select : integer;
  
  --constant g : integer := 1;
  
  signal IQ_tmp : IQ_t;
  
begin

  frame_record <= frame_to_record(frame);
  chanel_select <= to_integer(frame_record.chanel);
  
  IQ <= IQ_tmp;
  
  debug2 <= (others => '0');
  debug <= std_logic_vector(IQ_tmp.i);
  
  
  GEN_CHANEL:
  for g in 0 to chanel_count-1 generate
    FIFO_X: FIFO port map (reset, store, push(g), clk, pop(g), frame, frames(g), peek_frames(g));
    CHANEL_X: Chanel port map (clk, reset, enable, pop(g), frames(g), peek_frames(g), IQ_s(g), power_s(g));
    push(g) <= To_Std_Logic( chanel_select=g );
  end generate GEN_CHANEL;

  RESULT: Mixer port map(clk, reset, IQ_s, power_s, IQ_tmp);

end structural;

library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.GNSSsettings.all;

entity ChanelsHandlerWrapper is
  port
  (
    clk    : in std_logic;
    reset  : in std_logic;

    enable : in std_logic;
    I : out std_logic_vector(15 downto 0);
    Q : out std_logic_vector(15 downto 0);

    store  : in std_logic;
    frame : in std_logic_vector(frameWidth - 1 downto 0)
  );
end ChanelsHandlerWrapper;

architecture structural of ChanelsHandlerWrapper is

    -- Declare attributes for clocks and resets
    ATTRIBUTE X_INTERFACE_INFO : STRING; 
    ATTRIBUTE X_INTERFACE_INFO of clk: SIGNAL is "xilinx.com:signal:clock:1.0 clk CLK";
    ATTRIBUTE X_INTERFACE_INFO of reset : SIGNAL is "xilinx.com:signal:reset:1.0 reset RST";
    ATTRIBUTE X_INTERFACE_PARAMETER : STRING;
    --ATTRIBUTE X_INTERFACE_PARAMETER of clk : SIGNAL is "ASSOCIATED_RESET reset, FREQ_HZ 20000000";
    ATTRIBUTE X_INTERFACE_PARAMETER of reset : SIGNAL is "POLARITY ACTIVE_HIGH";

    component ChanelsHandler
    port (
    clk    : in std_logic;
    reset  : in std_logic;

    enable : in std_logic;
    IQ : out IQ_t;

    store  : in std_logic;
    frame : in Frame_t;

    debug  : out std_logic_vector(7 downto 0);
    debug2 : out std_logic_vector(2 downto 0)
    );
    end component;
    signal debug : std_logic_vector(7 downto 0);
    signal debug2 : std_logic_vector(2 downto 0);
    signal IQ : IQ_t;
    signal IQ_buffer : IQ_t;
begin

  process (clk, reset)
  begin
    if reset = '1' then
      IQ_buffer.i <= "00000000";
      IQ_buffer.q <= "00000000";

    elsif rising_edge(clk) then
      if enable = ENABLED then
        IQ_buffer <= IQ;
      else
        IQ_buffer.i <= "00000000";
        IQ_buffer.q <= "00000000";
      end if;
    end if;
  end process;

I <= std_logic_vector(IQ_buffer.i) & "00000000";
Q <= std_logic_vector(IQ_buffer.q) & "00000000";
CH: ChanelsHandler port map (clk, reset, enable, IQ, store, frame, debug, debug2);
end structural;