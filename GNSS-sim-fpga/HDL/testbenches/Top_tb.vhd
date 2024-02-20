library ieee;
use ieee.std_logic_1164.all;
USE ieee.std_logic_arith.ALL;
use ieee.numeric_std.all;
use ieee.std_logic_textio.all;
library std;
use STD.textio.all;
use work.settings.all;


entity top_tb is
end;

architecture bench of top_tb is
    
    --constant frameWidth: integer := 176;
    --constant chanel_count : integer := 4;

    component SPI_helper
        generic (
          n : integer := frameWidth;
          clk_period : time := samplePeriode
        );
        port (
          word : in std_logic_vector(frameWidth-1 downto 0);
          done : out std_logic;
          clk : out std_logic;
          serial_out : out std_logic
        );
    end component;

    component Top
        port (
          clk : in std_logic;
          reset : in std_logic;
          store : in std_logic;
          serial_in : in std_logic;
          serial_out : out std_logic
        );
    end component;


    signal clk       : std_logic := '0';
    signal reset     : std_logic := '0';
    signal store     : std_logic := '0';

    signal MOSI : std_logic;
    signal MISO : std_logic;

    signal word    : std_logic_vector(frameWidth-1 downto 0);
    signal send_done : std_logic;

begin

    SPI0: component SPI_helper port map (word, send_done, clk, MOSI);
    TOP0: component Top port map (clk, reset, store, MOSI, MISO);

    reset <= '1', '0' after 1 ns;

    process
        procedure send(value: in std_logic_vector(frameWidth-1 downto 0)) is
        begin
            word <= value;
            wait until rising_edge(send_done);
            store <= '1';
            wait for 0.5 us;
            store <= '0';
            wait for 0.5 us;
        end procedure;

        procedure send(
          satNum:     in integer range 0 to 255;
          bits:       in std_logic_vector(63 downto 0);
          delay:      in std_logic_vector(63 downto 0);
          phase_step: in integer;
          power:      in integer range 0 to 255
        ) is
        begin
            send(
              std_logic_vector(to_unsigned(satNum, 8)) & 
              bits & 
              delay & 
              std_logic_vector(to_signed(phase_step, 32)) & 
              std_logic_vector(to_unsigned(power, 8))
            );
        end procedure;

        procedure send(
          satNum:     in integer range 0 to 255;
          bits:       in std_logic_vector(63 downto 0);
          delay:      in integer;
          phase_step: in integer;
          power:      in integer range 0 to 255
        ) is
        begin
            send(
              satNum, bits,
              std_logic_vector(to_signed(delay, 64)),
              phase_step, power
            );
        end procedure;

    begin
        wait for 1 us;

        send(0, x"00000000000001aa", x"00002d0fe08c7ccf", 40297315, 62);
        send(0, x"0000000000000295", x"00002d0fdf463844", 40297315, 62);
        send(0, x"000000000000015a", x"00002d0fddffffb2", 40297244, 62);
        send(0, x"0000000000000155", x"00002d0fdcb9d01b", 40297244, 62);
        send(0, x"00000000000001a9", x"00002d0fdb73af7d", 40297244, 62);
        send(0, x"00000000000002a6", x"00002d0fda2d94dc", 40297244, 62);
        send(0, x"000000000000016a", x"00002d0fd8e78635", 40297244, 62);
        send(0, x"00000000000001a9", x"00002d0fd7a18388", 40297244, 62);

        loop
            word <= (others => '0');
            wait until rising_edge(send_done);
            word <= (others => '1');
            wait until rising_edge(send_done);
        end loop;
    end process;

end bench;