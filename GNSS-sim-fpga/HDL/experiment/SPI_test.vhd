library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.settings.all;

entity SPI_Test is
    port(
        clk : in std_logic;
        reset : in std_logic;
        
        --store : in std_logic;

        serial_in : in std_logic;
        serial_out : out std_logic;

        debug : out std_logic_vector(7 downto 0)
    );
end entity;

architecture structural of SPI_Test is
    component SPI
        generic (
          n : integer := 8
        );
        port (
          clk : in std_logic;
          reset : in std_logic;
          serial_in : in std_logic;
          parallel_out : out std_logic_vector(n-1 downto 0)
        );
    end component;
begin

    SPI0: component SPI port map (clk, reset, serial_in, debug);

    serial_out <= serial_in;

end structural;