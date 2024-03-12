library ieee;
use ieee.std_logic_1164.all;
USE ieee.numeric_std.ALL;
use work.settings.all;
use work.constelation.all;

entity Chanel is
  port
  (
    clk    : in std_logic;
    reset  : in std_logic;
    enable : in std_logic;

    enable_next_frame : out std_logic;
    next_frame     : in Frame_t;
    peek_frame     : in Frame_t;

    IQ : out IQ_t;

    power: out Power_t
  );
end Chanel;

architecture structural of Chanel is

  component FrameHandler
    generic
    (
      bits : integer
    );
    port
    (
      clk            : in std_logic;
      reset          : in std_logic;
      enable         : in std_logic;
      data           : out std_logic;
      doppler_shift  : out Doppler_t;
      delay_step     : out DelayStep_t;
      power          : out Power_t;
      prn            : out PRN_T;
      enable_next_frame : out std_logic := '0';
      next_frame     : in Frame_t;
      peek_frame     : in Frame_t
    );
  end component;

  component Modulation
    port
    (
      clk         : in  std_logic;
      reset       : in  std_logic;
      enable      : in  std_logic;
      enable_data : out std_logic;

      prn         : in PRN_T;

      IQ_output    : out IQ_t;
      data_input  : in  std_logic
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
      clk           : in std_logic;
      reset         : in std_logic;
      enable        : in std_logic;
      enable_modulation : out std_logic;

      IQ_output      : out IQ_t;
      IQ_input       : in IQ_t;

      doppler_shift : in Doppler_t;
      delay_step    : in DelayStep_t
    );
  end component;

  signal enable_upsample, enable_modulation, enable_data : std_logic;
  
  signal data : std_logic;
  signal doppler_shift : Doppler_t;
  signal delay_step : DelayStep_t;
  signal prn : PRN_t;

  signal IQ_upsampled, IQ_modulated : IQ_t;
  
  
  FOR mod0: Modulation USE ENTITY WORK.Modulation(galileoL1);
  
begin

  IQ <= IQ_upsampled;
  enable_upsample <= enable;

  data0 : component FrameHandler generic map (bits => FrameSize)
  port map (
    clk => clk, reset => reset,
    enable => enable_data, data => data, doppler_shift => doppler_shift, delay_step => delay_step, power => power, prn => prn,
    enable_next_frame => enable_next_frame, next_frame => next_frame, peek_frame => peek_frame
  );

  mod0 : component Modulation port map (
    clk => clk, reset => reset,
    enable => enable_modulation,
    enable_data => enable_data,
    prn => prn,
    IQ_output => IQ_modulated,
    data_input => data
  );

  
  upsample : component DopplerUpsample generic map (
    radioFrequencyOut => radioFrequencyOut,
    radioFrequencyIn  => RadioFrequencyIn, -- set this diffrently for diffrent prn
    inputRate         => InputRate,
    outputRate        => outputRate,
    subCycles         => subCycles
  )
  port map (
    clk => clk, reset => reset,
    enable => enable_upsample,
    enable_modulation => enable_modulation,

    IQ_output => IQ_upsampled,
    IQ_input => IQ_modulated,

    doppler_shift => doppler_shift,
    delay_step => delay_step
  );

end architecture;