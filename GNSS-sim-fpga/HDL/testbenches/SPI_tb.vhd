library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity SPI_tb is
end;

architecture bench of SPI_tb is
    constant n : integer := 4;
    

    component SPI_helper
        generic (
          n : integer := n;
          clk_period : time := 1 us
        );
        port (
          word : in std_logic_vector(n-1 downto 0);
          done : out std_logic;
          clk : out std_logic;
          serial_out : out std_logic
        );
    end component;
    component SPI
        generic (
          n : integer := n
        );
        port (
          clk : in std_logic;
          reset : in std_logic;
          serial_in : in std_logic;
          parallel_out : out std_logic_vector(n-1 downto 0)
        );
    end component;

    signal clk       : std_logic := '0';
    signal reset     : std_logic := '0';
    signal send_done : std_logic := '0';
    signal serial    : std_logic := '0';

    signal result    : std_logic_vector(n-1 downto 0);

    signal word    : std_logic_vector(n-1 downto 0);

begin

    SPI0: SPI port map (clk, reset, serial, result);
    SPI_HELPER0: SPI_helper port map (word, send_done, clk, serial);

    reset <= '1', '0' after 1 ns;

    process
    begin
        wait for 1 us;
        word <= "0011";
        wait until rising_edge(send_done);
        wait for 10 us;
        word <= "1100";
        wait until rising_edge(send_done);
        wait for 10 us;
        word <= "0101";
        wait until rising_edge(send_done);
        wait for 10 us;
        word <= "1010";
        wait until rising_edge(send_done);
        wait for 10 us;
    end process;

end;
