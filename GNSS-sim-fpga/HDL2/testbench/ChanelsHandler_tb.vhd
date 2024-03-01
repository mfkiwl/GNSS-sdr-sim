library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.settings.all;

entity ChanelsHandler_tb is
end ChanelsHandler_tb;

architecture bench1 of ChanelsHandler_tb is
  component ChanelsHandler
    port (
      clk : in std_logic;
      reset : in std_logic;
      enable : in std_logic;
      IQ : out IQ_t;
      store : in std_logic;
      frame : in Frame_t
    );
  end component;

  signal clk, reset, enable, store : std_logic;
  signal IQ : IQ_t;
  signal frame : Frame_t;
  signal frame_record : FrameRecord_t;

begin

  frame <= record_to_frame(frame_record);
  CH_0: ChanelsHandler port map (clk, reset, enable, IQ, store, frame);

  process
  begin
    clk <= '0';
    store <= '0';
    enable <= '0';

    reset <= '1';
    wait for 1 ns;
    reset <= '0';

    wait for 1 us;
    enable <= '1';
    wait for 1 us;

    frame_record.chanel <= to_unsigned(0, 8);
    frame_record.prn <= to_unsigned(0, 8);
    frame_record.bits <= (others => '0');
    frame_record.delay_step <= to_signed(0, frame_record.delay_step'length);
    frame_record.phase_step <= 100000;
    frame_record.power <= to_unsigned(250, 8);
    wait for 1 us;
    store <= '1';
    wait for 1 us;
    store <= '0';
    wait for 1 us;

    loop
      clk <= '1';
      wait for 1 us;
      clk <= '0';
      wait for 1 us;
    end loop;

  end process;

end bench1;