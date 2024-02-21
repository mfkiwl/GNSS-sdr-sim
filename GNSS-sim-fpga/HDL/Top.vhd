library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.settings.all;

entity Top is
    port(
        clk : in std_logic;
        reset : in std_logic;
        
        store : in std_logic;

        serial_in : in std_logic;
        serial_out : out std_logic;

        debug : out std_logic_vector(7 downto 0)
    );
end Top;

architecture structural of Top is
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
          Q : out IQ;
			 debug : out std_logic_vector(7 downto 0)
        );
    end component;

    component OutputHandler
        port (
          clk : in std_logic;
          reset : in std_logic;
          serial_out : out std_logic;
          I : in IQ;
          Q : in IQ
        );
    end component;

    signal I, Q : IQ;

begin
    
	 --serial_out <= serial_in;
	 
    IN0: component InputHandler port map (clk, reset, serial_in, store, I, Q, debug);
    OUT0: component OutputHandler port map (clk, reset, serial_out, I, Q);

end structural;