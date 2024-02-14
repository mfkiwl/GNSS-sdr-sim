library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity FIFO_tb is
end;

architecture bench of FIFO_tb is
  -- Generics
  constant width : integer := 4;
  constant depth : integer := 4;
  -- Ports
  signal push : std_logic;
  signal pop : std_logic;
  signal reset : std_logic;
  signal Q : std_logic_vector(width-1 downto 0);
  signal D : std_logic_vector(width-1 downto 0);
begin

  FIFO_inst : entity work.FIFO
  generic map (
    width => width,
    depth => depth
  )
  port map (
    push => push,
    pop => pop,
    reset => reset,
    Q => Q,
    D => D
  );

  reset <= '1', '0' after 1 ns;

  push <= '0', '1' after 2 us, '0' after 3 us, '1' after 5 us;
  pop  <= '0', '1' after 6 us, '0' after 7 us, '1' after 8 us, '0' after 9 us;
  Q <= "0000", "0101" after 1 us, "1100" after 4 us;

end;