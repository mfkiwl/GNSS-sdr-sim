library ieee;
use ieee.std_logic_1164.all;
USE ieee.std_logic_arith.ALL;
use ieee.numeric_std.all;
use work.settings.all;


entity InputHandler_tb is
end;

architecture bench of InputHandler_tb is
    
    constant frameWidth: integer := 176;
    constant chanel_count : integer := 4;

    component SPI_helper
        generic (
          n : integer := frameWidth;
          clk_period : time := 1 us
        );
        port (
          word : in std_logic_vector(frameWidth-1 downto 0);
          done : out std_logic;
          clk : out std_logic;
          serial_out : out std_logic
        );
    end component;
    
    component InputHandler
        generic (
          chanel_count : integer := chanel_count
        );
        port (
          clk : in std_logic;
          reset : in std_logic;
          serial_in : in std_logic;
          store : in std_logic;
          I : out std_logic_vector(7 downto 0);
          Q : out std_logic_vector(7 downto 0)
        );
    end component;

    signal clk       : std_logic := '0';
    signal reset     : std_logic := '0';
    signal send_done : std_logic := '0';
    signal serial    : std_logic := '0';
    signal store     : std_logic := '0';

    signal I, Q : std_logic_vector(7 downto 0);

    signal word    : std_logic_vector(frameWidth-1 downto 0);

begin

    InputHandler0: InputHandler port map (clk, reset, serial, store, I, Q);
    SPI_HELPER0: SPI_helper port map (word, send_done, clk, serial);

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
    begin
        wait for 1 us;
        send(x"00333333333333333333333333333333333333333333");
        wait for 10 us;
        send(x"01aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
        wait for 10 us;
        send(x"02555555555555555555555555555555555555555555");
        wait for 10 us;
        send(x"03999999999999999999999999999999999999999999");
        wait for 10 us;
    end process;

end;
