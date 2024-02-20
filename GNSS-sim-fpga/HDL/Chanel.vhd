library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.settings.all;

entity Chanel is
  port
  (
    clk   : in std_logic;
    reset : in std_logic;

    get_next_frame : out std_logic;
    next_frame     : in std_logic_vector(frameWidth - 1 downto 0);

    I : out IQ;
    Q : out IQ;

    power: out Power_t
  );
end Chanel;

architecture behavioral of Chanel is

  component FrameHandler
    generic
    (
      bits : integer
    );
    port
    (
      reset          : in std_logic;
      pull_data      : in std_logic;
      data           : out std_logic;
      doppler_shift  : out integer;
      delay_set      : out signed(63 downto 0);
      power          : out Power_t;
      get_next_frame : out std_logic := '0';
      next_frame     : in std_logic_vector(frameWidth - 1 downto 0)
    );
  end component;

  component GlonassModulation
    port
    (
      reset      : in std_logic;
      clk_output : in std_logic;
      I_output   : out IQ;
      Q_output   : out IQ;
      clk_input  : out std_logic;
      data_input : in std_logic
    );
  end component;

  component DopplerUpsample
    generic
    (
      radioFrequencyOut : integer;
      radioFrequencyIn  : integer;
      inputRate         : integer;
      outputRate        : integer;
      subCycles         : integer
    );
    port
    (
      reset         : in std_logic;
      clk_output    : in std_logic;
      I_output      : out IQ;
      Q_output      : out IQ;
      clk_input     : out std_logic;
      I_input       : in IQ;
      Q_input       : in IQ;
      doppler_shift : in integer;
      delay_set     : in signed(63 downto 0);
      delay_step    : in signed(63 downto 0);
      delay_current : out signed(63 downto 0)
    );
  end component;
  signal pull_upsample, pull_source, pull_data : std_logic;
  signal I_source, Q_source                    : IQ;

  signal delay_set     : signed(63 downto 0);
  signal delay_step    : signed(63 downto 0);
  signal delay_current : signed(63 downto 0);
  signal doppler_shift : integer;
  signal data          : std_logic;

begin

  --data0: component DataSource port map (reset=>reset, 
  --    clk_output=>clk_data, data_out=>data, 
  --    doppler_shift_out=>doppler_shift, delay_out=>delay);

  data0 : component FrameHandler generic map (bits => 10)
  port map
  (
    reset => reset,
    pull_data => pull_data, data => data, doppler_shift => doppler_shift, delay_set => delay_set, power=>power,
    get_next_frame => get_next_frame, next_frame => next_frame
  );

  mod0 : component GlonassModulation port map (
    reset => reset,
    clk_output => pull_source, I_output => I_source, Q_output => Q_source,
    clk_input => pull_data, data_input => data
  );

  delay_step    <= to_signed(0, delay_step'length);
  delay_current <= to_signed(0, delay_current'length);
  
  upsample : component DopplerUpsample generic map (
    radioFrequencyOut => 1602000000,
    radioFrequencyIn  => 1602000000, -- set this diffrently for diffrent prn
    inputRate         =>  511000,
    outputRate        => outputRate,
    subCycles         => 100
  )
  port map (
    reset => reset,
    clk_output => clk, I_output => I, Q_output => Q,
    clk_input => pull_source, I_input => I_source, Q_input => Q_source,
    doppler_shift => doppler_shift, delay_set => delay_set, delay_step => delay_step, delay_current => delay_current
  );

end architecture;