library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.std_logic_textio.all;
library std;
use STD.textio.all;

entity GlonassUpsample_tb is
end GlonassUpsample_tb;

architecture Stim1 of GlonassUpsample_tb is
  component DopplerUpsample
    generic(
      radioFrequencyOut : integer := 1602000000;
      radioFrequencyIn  : integer := 1602000000;
      inputRate         : integer := 511000;
      outputRate        : integer := 20000000;
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
  
  component GlonassModulation is
  port(
    reset      : in std_logic;
    
    clk_output : in std_logic;
	I_output   : out integer;
	Q_output   : out integer;
	
	clk_input  : out std_logic;
	data_input : in std_logic
  );
  end component GlonassModulation;
  
  component DataSource is
  port(
    reset             : in std_logic;
    clk_output        : in std_logic;
    data_out          : out std_logic;
    doppler_shift_out : out integer;
    delay_out         : out integer
  );
  end component DataSource;
  
  file IQ_file : text;
  
  signal reset      : std_logic;
      
  signal clk_output : std_logic := '0';
  signal I_output   : integer;
  signal Q_output   : integer;
  
  signal clk_mod  : std_logic;
  signal I_mod    : integer;
  signal Q_mod    : integer;
  
  signal clk_data : std_logic;
  signal data     : std_logic;
  
  signal doppler_shift : integer := 0;
  signal delay         : integer := 0;

  signal simend : boolean := false;
begin
  
  reset <= '1', '0' after 1 ns;
  --clk_output <= not clk_output after 25 ns;
  
  process
  begin
	wait for 6001 ms;
	simend <= true;
  end process;
	
  process
    variable iqLine     : line;
  begin
    file_open(IQ_file, "output_results.txt", write_mode);
    wait for 25 ns;
    while simend=false loop
      clk_output <= '1';
	  wait for 25 ns;
      clk_output <= '0';
	  write(iqLine, I_output);
	  write(iqLine, string'(", "));
	  write(iqLine, Q_output);
	  writeline(IQ_file, iqLine);
	  wait for 25 ns;
    end loop;
	file_close(IQ_file);
	report "done";
	wait;
  end process;
	
  --src0: component ExampleInput port map (reset => reset, clk=>clk_input, I=>I_input, Q=>Q_input);
  
  data0: component DataSource port map (reset=>reset, 
                                     clk_output=>clk_data, data_out=>data, 
									 doppler_shift_out=>doppler_shift, delay_out=>delay);
  
  mod0: component GlonassModulation port map (reset=>reset, 
                                     clk_output=>clk_mod, I_output=>I_mod, Q_output=>Q_mod,
									 clk_input=>clk_data, data_input=>data);
  
  chanel0: component DopplerUpsample port map (reset=>reset, 
                                     clk_output=>clk_output, I_output=>I_output, Q_output=>Q_output,
                                     clk_input =>clk_mod , I_input =>I_mod , Q_input =>Q_mod ,
                                     doppler_shift=>doppler_shift, delay=>delay);

  
end Stim1;
