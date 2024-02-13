library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

architecture Stim1 of DopplerUpsample_tb is
  component DopplerUpsample
    generic(
      radioFrequencyOut : integer := 1575420000;
      radioFrequencyIn  : integer := 1575420000;
      inputRate         : integer := 10000000;
      outputRate        : integer := 25000000;
      subCycles         : integer := 1
    ); 
    port (
      reset      : in std_logic;
      
      clk_output : in  std_logic;
      I_output   : out integer;
      Q_output   : out integer;
  
      clk_input  : out std_logic;
      I_input    : in integer;
      Q_input    : in integer;
  
      doppler_shift : in integer;
      delay         : in integer
    );
  end component DopplerUpsample;

  component ExampleInput
  port(
    reset : in std_logic;
    clk   : in  std_logic;
    I     : out integer;
    Q     : out integer
  );
  end component ExampleInput;

  signal reset      : std_logic;
      
  signal clk_output : std_logic := '0';
  signal I_output   : integer;
  signal Q_output   : integer;
  
  signal clk_input  : std_logic;
  signal I_input    : integer;
  signal Q_input    : integer;
  
  signal doppler_shift : integer := 0;
  signal delay         : integer := 0;

begin
  
  reset <= '1', '0' after 1 ns;
  clk_output <= not clk_output after 10 ns;

  src0: component ExampleInput port map (reset => reset, clk=>clk_input, I=>I_input, Q=>Q_input);

  chanel0: component DopplerUpsample port map (reset=>reset, 
                                     clk_output=>clk_output, I_output=>I_output, Q_output=>Q_output,
                                     clk_input =>clk_input , I_input =>I_input , Q_input =>Q_input ,
                                     doppler_shift=>doppler_shift, delay=>delay);
  
end Stim1;