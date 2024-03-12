library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.std_logic_textio.all;
library std;
use STD.textio.all;
use work.settings.all;
use work.input.all;
use work.constelation.all;

entity ChanelsHandler_tb is
end ChanelsHandler_tb;

architecture bench2 of ChanelsHandler_tb is
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



  subtype byte is std_ulogic_vector(7 downto 0);

  function to_byte(c : character) return byte is
  begin
    return byte(to_unsigned(character'pos(c), 8));
  end function;

  function to_character(b: byte) return character is
  begin
    return character'val(to_integer(unsigned(b)));
  end function;



  signal clk, reset, enable, store : std_logic;
  signal IQ : IQ_t;
  signal frame : Frame_t;
  signal frame_record : FrameRecord_t;

  signal frames_send : integer := 0;
  signal step : integer := 0;

begin

  CH_0: ChanelsHandler port map (clk, reset, enable, IQ, store, frame);

  process
    file IQ_file      : text open write_mode is "signal.txt";
    variable iqLine          : line;

    procedure storeFrame(new_frame : in Frame_t) is
    begin
        frame <= new_frame;
        wait for 1 ns;
        store <= '1';
        wait for 1 ns;
        store <= '0';
        wait for 1 ns;
    end procedure;

    procedure storeSatsFrames(n: in Integer) is
    begin
      for sat in 1 to inputFrameSatCount loop
        storeFrame(inputSeq(frames_send+sat-1));
      end loop;
      frames_send <= frames_send+inputFrameSatCount;
      if n>1 then
        storeSatsFrames(n-1);
      end if;
    end procedure;

    procedure run10th_sec(n: in Integer) is
    begin
      for sat in 1 to outputRate/10 loop
        step <= sat;
        clk <= '1';
        wait for (1000 ms)/outputRate/2;
        clk <= '0';
        wait for (1000 ms)/outputRate/2;

        write(iqLine, to_integer(IQ.i));
        write(iqLine, string'(","));
        write(iqLine, to_integer(IQ.q));
        writeline(IQ_file, iqLine);
      end loop;
      if n>1 then
        run10th_sec(n-1);
      end if;
    end procedure;
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


    storeSatsFrames(1);
    wait for 1 ns;
    storeSatsFrames(1);
    wait for 1 ns;
    loop
      report "loop started";
      if frames_send<inputTable'length then
        storeSatsFrames(1);
        report "uploaded";
      else
        report "end reached";
      end if;
      run10th_sec(1);
    end loop;

  end process;

end bench2;