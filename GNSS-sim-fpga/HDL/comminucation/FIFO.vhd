library ieee;
use ieee.std_logic_1164.all;

entity FIFO is
    generic (
        width  : integer := 4;
        depth  : integer := 64
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

  signal top : integer range depth-1 downto 0 := 0;
  signal bottom : integer range depth-1 downto 0 := 0;
  
begin
    D <= registers(bottom);

    process (pop, reset)
	  begin
      if (reset = '1') then
        bottom <= 0;
      elsif rising_edge(pop) then
        if (bottom /= depth-1) then
          bottom <= bottom + 1;
        else
          bottom <= 0;
        end if;
      end if;
	  end process;
	 
	 process (push, reset)
	 begin
		if (reset = '1') then
        registers <= (others => (others => '0'));
        top <= 0;
      elsif rising_edge(push) then
		  registers(top) <= Q;
		  if (top /= depth-1) then
		    top <= top + 1;
		  else
		    top <= 0;
		  end if;
		end if;
	 end process;
	 
    --process (push, pop, reset)
    --begin
    --    if (reset = '1') then
    --        registers <= (others => (others => '0'));   
    --    elsif rising_edge(push) then
    --        if (size /= depth-1) then
    --            size <= size+1;
    --            registers(size) <= Q;
    --        end if;
    --    elsif rising_edge(pop) then
    --        if(size /= 1) then
    --            size <= size-1;
    --        end if;
    --        registers(depth-2 downto 0) <= registers(depth-1 downto 1);
    --    end if;
    --end process;
end behavioral;