library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.settings.all;

entity SPI_tb is
end SPI_tb;

architecture bench1 of SPI_tb is
  component SPI
    generic (
      n_in : integer := 8;
      n_out : integer := 8
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
  component SPI_helper
    generic (
      w_out : integer := 8;
      w_in : integer := 8;
      clk_period : time := 0.5 us
    );
    port (
      clk : out std_logic;
      word_out : in std_logic_vector(w_out - 1 downto 0);
      done_out : out std_logic;
      serial_out : out std_logic;
      word_in : out std_logic_vector(w_in - 1 downto 0);
      done_in : out std_logic;
      serial_in : in std_logic;
      clk_override : in std_logic
    );
  end component;

  signal reset, clk, clk_override : std_logic;
  signal send_done, recieve_done, serial_in, serial_out : std_logic;

  signal word_in, word_out, parallel_in, parallel_out, word_recieved : std_logic_vector(7 downto 0);

begin

  SPIH0: SPI_helper port map (clk, word_out, send_done, serial_in, word_in, recieve_done, serial_out, clk_override);
  SPI0: SPI port map (clk, reset, serial_in, parallel_out, parallel_in, serial_out);

  process
    variable frame_record : FrameRecord_t;
  begin
    reset <='0';
    clk_override <= '0';
    wait for 1 ns;
    reset <='1';
    wait for 1 ns;
    reset <='0';

    parallel_in <= x"55";
    word_out<=x"aa";

    wait until rising_edge(send_done);
    
    parallel_in <= parallel_out;

    word_out <= (others => '0');

    wait until rising_edge(send_done);
    clk_override <= '1';
    parallel_in <= parallel_out;

    wait for 200 ms;

  end process;

  process (recieve_done)
  begin
    if rising_edge(recieve_done) then
      word_recieved <= word_in;
    end if;
  end process;


end bench1;