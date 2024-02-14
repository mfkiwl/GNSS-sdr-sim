library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.settings.all;

entity InputHandler is
    generic(
        chanel_count : integer := 4
    );
    port(
        clk : in std_logic;
        reset : in std_logic;
        
        serial_in : in std_logic;
        store : in std_logic;

        I : out std_logic_vector(7 downto 0);
        Q : out std_logic_vector(7 downto 0)
    );
end InputHandler;

architecture behavioral of InputHandler is

    --constant frameWidth: integer := 176;

    component FIFO
        generic (
          width : integer := frameWidth;
          depth : integer := 4
        );
        port (
          push : in std_logic;
          pop : in std_logic;
          reset : in std_logic;
          Q : in std_logic_vector(frameWidth-1 downto 0);
          D : out std_logic_vector(frameWidth-1 downto 0)
        );
    end component;

    component Chanel
        port (
          clk : in std_logic;
          reset : in std_logic;
          get_next_frame : out std_logic;
          next_frame : in std_logic_vector(frameWidth-1 downto 0);
          I : out std_logic_vector(7 downto 0);
          Q : out std_logic_vector(7 downto 0)
        );
    end component;

    component SPI
        generic (
          n : integer := frameWidth
        );
        port (
          clk : in std_logic;
          reset : in std_logic;
          serial_in : in std_logic;
          parallel_out : out std_logic_vector(n-1 downto 0)
        );
    end component;

    component Mixer
        generic (
          chanel_count : integer := chanel_count
        );
        port (
          clk : in std_logic;
          reset : in std_logic;
          I_s : in IQList;
          Q_s : in IQList;
          I : out std_logic_vector(7 downto 0);
          Q : out std_logic_vector(7 downto 0)
        );
    end component;

    function To_Std_Logic(L: BOOLEAN) return std_ulogic is
    begin
        if L then
            return('1');
        else
            return('0');
        end if;
    end function To_Std_Logic;
    
    
    signal I_s : IQList;
    signal Q_s : IQList;

    type ChanelSelect is array(chanel_count-1 downto 0) of std_logic;
    signal push : ChanelSelect;
    signal pop  : ChanelSelect;

    signal newData : std_logic_vector(frameWidth-1 downto 0);
    type Frames_t is array(chanel_count-1 downto 0) of std_logic_vector(frameWidth-1 downto 0);
    signal frames : Frames_t;

    signal chanel_select : integer;
    signal chanel_select_v : std_logic_vector(7 downto 0);


begin

    chanel_select <= to_integer(unsigned(newData(frameWidth-1 downto frameWidth-8)));
    chanel_select_v <= newData(frameWidth-1 downto frameWidth-8);

    SPI_IN: SPI port map (clk, reset, serial_in, newData);

    GEN_CHANEL:
    for i in 0 to chanel_count-1 generate
        FIFO_X: FIFO port map (push(i), pop(i), reset, newData, frames(i));
        CHANEL_X: Chanel port map (clk, reset, pop(i), frames(i), I_s(i), Q_s(i));
        push(i) <= To_Std_Logic( (store='1') and (chanel_select=i) );
    end generate GEN_CHANEL;

    RESULT: Mixer port map(clk, reset, I_s, Q_s, I, Q);

end architecture;