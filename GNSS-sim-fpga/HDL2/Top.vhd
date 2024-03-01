library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.settings.all;

entity Top is
  port
  (
    clk   : in std_logic;
    reset : in std_logic;

    store : in std_logic;

    serial_in  : in std_logic;
    serial_out : out std_logic;

    debug  : out std_logic_vector(7 downto 0);
    debug2 : out std_logic_vector(2 downto 0)
  );
end Top;

architecture structural of Top is
  component ClockDiv16
    port (
      clk : in std_logic;
      clkdiv : out std_logic
    );
  end component;
  component SPI
    generic (
      n_in  : integer := frameWidth;
      n_out : integer := 16
    );
    port (
      clk : in std_logic;
      reset : in std_logic;
      serial_in : in std_logic;
      parallel_out : out std_logic_vector(n_out-1 downto 0);
      parallel_in : in std_logic_vector(n_in-1 downto 0);
      serial_out : out std_logic
    );
  end component;
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

  signal IQ_vector : std_logic_vector(15 downto 0);
  signal IQ : IQ_t;

  signal frame : Frame_t;
  
  signal clk16 : std_logic;

begin

  IQ_vector <= std_logic_vector(IQ.i) & std_logic_vector(IQ.q);

  CLK_DIV: ClockDiv16 port map (clk, clk16);
  SPI_0  : SPI port map (clk, reset, serial_in, frame, IQ_vector, serial_out);
  CHNS_0 : ChanelsHandler port map (clk, reset, '1', IQ, store, frame);

  debug <= std_logic_vector(IQ.i);
  debug2(0) <= serial_in;
  debug2(1) <= clk16;
  debug2(2) <= frame(frame'HIGH-8);

end structural;