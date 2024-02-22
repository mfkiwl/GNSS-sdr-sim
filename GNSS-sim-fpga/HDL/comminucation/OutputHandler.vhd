library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.settings.all;

entity OutputHandler is
    port(
        clk : in std_logic;
        reset : in std_logic;
        
        serial_out : out std_logic;

        I : in IQ;
        Q : in IQ;
		  
		  debug : out std_logic_vector(2 downto 0)
    );
end OutputHandler;


architecture behavioral of OutputHandler is
    signal word : std_logic_vector(15 downto 0) := (others => '0');
    signal state : integer range 0 to 15;
	 
	 -- from: https://groups.google.com/d/msg/comp.lang.vhdl/eBZQXrw2Ngk/4H7oL8hdHMcJ
	 function reverse_any_vector(a: in std_logic_vector) return std_logic_vector is
		variable result: std_logic_vector(a'RANGE);
		alias aa: std_logic_vector(a'REVERSE_RANGE) is a;
	 begin
		for i in aa'RANGE loop
			result(i) := aa(i);
		end loop;
		return result;
	 end; -- function reverse_any_vector	
	 
begin

    serial_out <= word(0);
    
	 debug <= std_logic_vector(to_unsigned(state, debug'length));
	 
    process (reset, clk, I, Q)
    begin
        if reset = '1' then
            word <= std_logic_vector(I) & std_logic_vector(Q);
            state <= 0;
        elsif falling_edge( clk ) then
            if (state=15) then
                state <= 0;
                word <= std_logic_vector(I) & std_logic_vector(Q);
            else
                state <= state+1;
                word <= '0' & word(15 downto 1);
            end if;
        end if;
    end process;

end behavioral;