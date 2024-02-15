library ieee;
use ieee.std_logic_1164.all;

entity FIFO is
    generic (
        width  : integer := 4;
        depth  : integer := 4
    );
    port(
        push:             in std_logic; 
        pop:              in std_logic;
        reset:            in std_logic; 
        Q:                in std_logic_vector(width-1 downto 0);
        D:                out std_logic_vector(width-1 downto 0)
    );
end FIFO;

architecture behavioral of FIFO is
  type FIFO_ARRAY_TYPE is array (depth-1 downto 0) of std_logic_vector(width-1 downto 0);
  signal registers : FIFO_ARRAY_TYPE := (others => (others => '0'));
  
  signal size : integer range depth-1 downto 0 := 0;

begin
    D <= registers(0);

    process (push, pop, reset)
    begin
        if (reset = '1') then
            registers <= (others => (others => '0'));   
        elsif rising_edge(push) then
            if (size /= depth-1) then
                size <= size+1;
                registers(size) <= Q;
            end if;
        elsif rising_edge(pop) then
            size <= size-1;
            registers(depth-2 downto 0) <= registers(depth-1 downto 1);
        end if;
    end process;
end behavioral;