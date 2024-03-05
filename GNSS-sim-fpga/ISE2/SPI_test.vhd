library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.settings.all;

entity SPI_test is
  port
  (
    clk   : in std_logic;
    reset : in std_logic;

    store : in std_logic;

    serial_in  : in std_logic;
    serial_out : out std_logic;

    debug  : out std_logic_vector(7 downto 0);
    debug2 : out std_logic_vector(2 downto 0)
  );
end SPI_test;

architecture Behavioral of SPI_test is
  component SPI
    generic (
      n_in  : integer := 8;
      n_out : integer := 8
    );
    port (
      clk : in std_logic;
      reset : in std_logic;
      serial_in : in std_logic;
      parallel_out : out std_logic_vector(n_out-1 downto 0);
      parallel_in : in std_logic_vector(n_in-1 downto 0);
      serial_out : out std_logic--;
		--debug : out std_logic_vector(7 downto 0)
    );
  end component;
  
  signal paralell : std_logic_vector(7 downto 0);
  
  
begin
	
	-- debug <= paralell;
	
	debug2(0) <= store;
	debug2(1) <= clk;
	debug2(2) <= '0';
	
	debug <= paralell;
	
	
	SPI0: SPI port map (clk, reset, serial_in, paralell, x"a5", serial_out);

end Behavioral;

