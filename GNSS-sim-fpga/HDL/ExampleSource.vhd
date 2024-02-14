library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity ExampleInput is
  port(reset : in std_logic;
       clk   : in  std_logic;
       I     : out integer;
       Q     : out integer
  );
end ExampleInput;

architecture halfhertz of ExampleInput is
  signal v : integer;
begin
  I <= v;
  Q <= 0;
  process (clk, reset)
  begin
    if reset = '1' then
      v <= 1;
    elsif rising_edge( clk ) then
      v <= v * (-1);
    end if;
  end process;
end halfhertz;

entity DopplerUpsample_tb is
end entity;