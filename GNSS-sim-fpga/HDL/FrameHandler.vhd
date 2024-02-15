library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.settings.all;

entity FrameHandler is
    generic(
        bits : integer := 10
    );
    port(
        reset          : in std_logic;
        pull_data      : in std_logic;
        data           : out std_logic;
        doppler_shift  : out integer;
        delay_set      : out signed(63 downto 0);
        power          : out Power_t;
        get_next_frame : out std_logic;
        next_frame     : in std_logic_vector(frameWidth-1 downto 0)
    );
end FrameHandler;

architecture behavioral of FrameHandler is
    signal current_bit : integer := 0;
begin

    data          <= next_frame(frameWidth-8-64+current_bit);
    delay_set     <= signed(next_frame(frameWidth-8-64-1 downto frameWidth-8-64-64));
    doppler_shift <= to_integer(signed(next_frame(frameWidth-8-64-64-1 downto frameWidth-8-64-64-32))); --> phase shift
    power         <= unsigned(next_frame(frameWidth-8-64-64-32-1 downto frameWidth-8-64-64-32-8));

    process (reset, pull_data)
    begin
        if reset = '1' then
            get_next_frame <= '0';
        elsif rising_edge( pull_data ) then
            if current_bit+1 < bits then
                current_bit <= current_bit+1;
            else
                current_bit <= 0;
                get_next_frame <= '1';
            end if;
        elsif falling_edge( pull_data ) then
            get_next_frame <= '0';
        end if;
    end process;
end behavioral;