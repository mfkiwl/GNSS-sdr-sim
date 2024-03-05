library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.settings.all;

entity Top_tb is
end Top_tb;

architecture bench1 of Top_tb is
  component Top
    port (
      clk : in std_logic;
      reset : in std_logic;
      store : in std_logic;
      serial_in : in std_logic;
      serial_out : out std_logic;
      debug : out std_logic_vector(7 downto 0);
      debug2 : out std_logic_vector(2 downto 0)
    );
  end component;
  component SPI_helper
    generic (
      w_out : integer := frameWidth;
      w_in : integer := 16;
      clk_period : time := samplePeriode/2
    );
    port (
      clk : out std_logic;
      word_out : in std_logic_vector(w_out-1 downto 0);
      done_out : out std_logic;
      serial_out : out std_logic;
      word_in : out std_logic_vector(w_in-1 downto 0);
      done_in : out std_logic;
      serial_in : in std_logic;
      clk_override : in std_logic
    );
  end component;

  signal clk, reset, store, serial_in, serial_out : std_logic;
  signal debug : std_logic_vector(7 downto 0);
  signal debug2 : std_logic_vector(2 downto 0);

  signal frame : Frame_t;

  signal iq_vector : std_logic_vector(15 downto 0);
  signal IQ : IQ_t := IQ_ZERO;

  signal frame_done, iq_done, clk_override : std_logic;

begin

  TOP0: Top port map (clk, reset, store, serial_in, Serial_out, debug, debug2);
  SPIH0 : SPI_helper port map (clk, frame, frame_done, serial_in, iq_vector, iq_done, serial_out, clk_override);

  process
    variable frame_record : FrameRecord_t;
  begin
    reset <='0';
    store <= '0';
    clk_override <= '0';
    wait for 1 ns;
    reset <='1';
    wait for 1 ns;
    reset <='0';

    frame_record.chanel     := to_unsigned(1, 8);
    frame_record.prn        := to_unsigned(0, 8);
    frame_record.bits       := (others => '0');
    frame_record.delay_step := to_signed(0, frame_record.delay_step'length);
    frame_record.phase_step := 100000;
    frame_record.power      := to_unsigned(250, 8);

    frame <= record_to_frame(frame_record);

    wait until rising_edge(frame_done);
    wait for 1 ns;
    store <= '1';
    wait for 1 ns;
    store <= '0';

    clk_override <= '1';
    frame <= (others => '0');

    wait for 200 ms;

  end process;

  process (iq_done)
  begin
    if rising_edge(iq_done) then
      iq <= vector_to_iq(iq_vector);
    end if;
  end process;

end bench1;