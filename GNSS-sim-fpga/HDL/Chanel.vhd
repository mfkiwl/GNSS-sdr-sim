library ieee;
use ieee.std_logic_1164.all;
use work.settings.all;

entity Chanel is
    port(
        clk: in std_logic;
        reset: in std_logic;
        
        get_next_frame: out std_logic;
        next_frame: in std_logic_vector(frameWidth-1 downto 0);

        I: out std_logic_vector(7 downto 0);
        Q: out std_logic_vector(7 downto 0)
    );
end Chanel;

architecture behavioral of Chanel is

    component DopplerUpsample
        generic (
          radioFrequencyOut : integer;
          radioFrequencyIn : integer;
          inputRate : integer;
          outputRate : integer;
          subCycles : integer
        );
        port (
          reset : in std_logic;
          clk_output : in std_logic;
          I_output : out integer;
          Q_output : out integer;
          clk_input : out std_logic;
          I_input : in integer;
          Q_input : in integer;
          doppler_shift : in integer;
          delay : in integer
        );
      end component;


    signal pull_upsample, pull_source, pull_data: std_logic;
    signal I_source, Q_source: std_logic_vector(7 downto 0);

    signal delay: integer;
    signal delay_step: integer;
    signal doppler_shift: integer;
    signal data: std_logic;
    signal power: integer;

begin

    get_next_frame <= '0';
    
    --data0: component DataSource port map (reset=>reset, 
    --    clk_output=>clk_data, data_out=>data, 
    --    doppler_shift_out=>doppler_shift, delay_out=>delay);

    mod0: component GlonassModulation port map (reset=>reset, 
        clk_output=>pull_source, I_output=>I_source, Q_output=>Q_source,
        clk_input=>pull_data, data_input=>data);

    upsample: component DopplerUpsample port map (reset=>reset, 
        clk_output=>clk_output, I_output=>Q, Q_output=>Q,
        clk_input =>clk_input , I_input =>I_source , Q_input =>Q_source ,
        doppler_shift=>doppler_shift, delay=>delay, delay_step=>delay_step);


end architecture;