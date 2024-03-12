library ieee;
use ieee.std_logic_1164.all;
use work.settings.all;

entity FIFO is
    generic (
        width  : integer := 4;
        depth  : integer := 64
    );
    port(
        reset:       in std_logic;
        clk_push:    in std_logic;
        enable_push: in std_logic;
        clk_pop:     in std_logic;
        enable_pop:  in std_logic; 
        Q:           in std_logic_vector(width-1 downto 0);
        D:           out std_logic_vector(width-1 downto 0);
        D2:          out std_logic_vector(width-1 downto 0)
    );
end FIFO;

architecture behavioral of FIFO is
  type FIFO_ARRAY_TYPE is array (depth-1 downto 0) of std_logic_vector(width-1 downto 0);
  signal registers : FIFO_ARRAY_TYPE := (others => (others => '0'));

  signal top    : integer range depth-1 downto 0 := 0;
  signal bottom : integer range depth-1 downto 0 := 0;
  signal peek   : integer range depth-1 downto 0 := 0;
  
begin
  D  <= registers(bottom);
  D2 <= registers(peek);

  process (bottom)
  begin
    if (bottom /= depth-1) then
      peek <= bottom + 1;
    else
      peek <= 0;
    end if;
  end process;

	process(clk_pop, reset)
	begin
		if (reset = '1') then
			bottom <= 0;
		elsif rising_edge(clk_pop) then
			if enable_pop=ENABLED then
				if (bottom /= depth-1) then
					bottom <= bottom + 1;
				else
					bottom <= 0;
				end if;
			end if;
		end if;
	end process;

  process(clk_push, reset)
	begin
		if (reset = '1') then
			registers <= (others => (others => '0'));
			top <= 0;
		elsif rising_edge(clk_push) then
			if enable_push=ENABLED then
				registers(top) <= Q;
				if (top /= depth-1) then
					top <= top + 1;
				else
					top <= 0;
				end if;
			end if;
		end if;
	end process;
  
end behavioral;