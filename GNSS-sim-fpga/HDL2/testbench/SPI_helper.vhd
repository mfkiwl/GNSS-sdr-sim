library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity SPI_helper is
  generic
  (
    w_out      : integer := 4;
    w_in       : integer := 4;
    clk_period : time    := 1 us
  );
  port
  (
    clk : out std_logic;

    word_out   : in std_logic_vector(w_out - 1 downto 0);
    done_out   : out std_logic := '0';
    serial_out : out std_logic;

    word_in   : out std_logic_vector(w_in - 1 downto 0);
    done_in   : out std_logic;
    serial_in : in std_logic;

    clk_override : in std_logic
  );
end entity;

architecture behavioral of SPI_helper is
  component SPI
    generic
    (
      n_in  : integer := w_out;
      n_out : integer := w_in
    );
    port
    (
      clk          : in std_logic;
      reset        : in std_logic;
      serial_in    : in std_logic;
      parallel_out : out std_logic_vector(n_out - 1 downto 0);
      parallel_in  : in std_logic_vector(n_in - 1 downto 0);
      serial_out   : out std_logic
    );
  end component;

  signal reset : std_logic;
  signal myclk : std_logic;

begin

  clk <= myclk;

  SPI_T : SPI port map
    (myclk, reset, serial_in, word_in, word_out, serial_out);

  process
    variable c_in : integer := 0;
  begin
    myclk      <= '0';
    reset      <= '0';
    done_in    <= '0';
    done_out   <= '0';
    wait for 1 ns;
    reset <= '1';
    wait for 1 ns;
    reset <= '0';
    loop
      if (not (clk_override='1')) then
        wait on word_out, clk_override;
        wait for 1 ns;
        reset <= '1';
        wait for 1 ns;
        reset <= '0';
      end if;
      done_out <= '0';

      for i in 1 to w_out loop
        myclk <= '0';
        wait for clk_period/2;
        myclk   <= '1';
        done_in <= '0';
        c_in := c_in + 1;
        wait for clk_period/2;
        if (c_in = w_in) then
          c_in := 0;
          done_in <= '1';
        end if;
      end loop;

      done_out <= '1';
    end loop;

  end process;

end behavioral;