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
          I : out IQ;
          Q : out IQ
        );
    end component;

    signal clk       : std_logic := '0';
    signal reset     : std_logic := '0';
    signal send_done : std_logic := '0';
    signal serial    : std_logic := '0';
    signal store     : std_logic := '0';

    signal I, Q : IQ;

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

        procedure send(
          satNum:     in integer range 0 to 255;
          bits:       in std_logic_vector(63 downto 0);
          delay:      in integer;
          phase_step: in integer;
          power:      in integer range 0 to 255
        ) is
        begin
            send(
              std_logic_vector(to_unsigned(satNum, 8)) & 
              bits & 
              std_logic_vector(to_signed(delay, 64)) & 
              std_logic_vector(to_signed(phase_step, 32)) & 
              std_logic_vector(to_unsigned(power, 8))
            );
        end procedure;

    begin
        wait for 1 us;
        --send(x"00333333333333333333333333333333333333333333");
        send(0, x"3333333333333333", 0, 10, 255);
        wait for 10 us;
        --send(x"01aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
        send(1, x"aaaaaaaaaaaaaaaa", 0, 20, 0);
        wait for 10 us;
        --send(x"02555555555555555555555555555555555555555555");
        send(2, x"5555555555555555", 0, 0, 0);
        wait for 10 us;
        --send(x"03999999999999999999999999999999999999999999");
        send(3, x"9999999999999999", 0, 0, 0);
        wait for 10 us;
    end process;

end;
