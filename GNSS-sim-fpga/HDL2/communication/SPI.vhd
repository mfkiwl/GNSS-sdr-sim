library ieee;
use ieee.std_logic_1164.all;

entity SPI is
    generic (
        n_in  : integer := 4;
        n_out : integer := 4
    );
    port(
        clk:              in std_logic;
        reset:            in std_logic;

        serial_in:        in std_logic;
        parallel_out:     out std_logic_vector(n_out-1 downto 0);

        parallel_in:      in std_logic_vector(n_in-1 downto 0);
        serial_out:       out std_logic
    );
end SPI;

architecture behavioral of SPI is
  signal reg: std_logic_vector(n_out-1 downto 0) := (others => '0');
  signal reg_send: std_logic_vector(n_in-1 downto 0) := (others => '0');
  signal index: integer range n_in-1 downto 0;
begin
    parallel_out <= reg;
    serial_out <= reg_send(n_in-1-index);

    process (clk,reset,parallel_in)
    begin
        if (reset = '1') then
            reg <= (others => '0');
            reg_send <= parallel_in; -- or 0?
            index <= 0;
        elsif falling_edge(clk) then
            
            if (index=n_in-1) then
              index <= 0;
              reg_send <= parallel_in;
            else
              index <= index+1;
            end if;
        elsif rising_edge(clk) then
          reg <=  reg(n_out-2 downto 0) & serial_in;
        end if;
    end process;
end behavioral;