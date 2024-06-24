library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.GNSSsettings.all;

entity DopplerUpsample is
  generic
  (
    radioFrequencyOut : integer := 1575420000;
    radioFrequencyIn  : integer := 1575420000;
    inputRate         : integer := 511000;
    outputRate        : integer := 20000000;
    subCycles         : integer := 1
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
end DopplerUpsample;

architecture arch1 of DopplerUpsample is

  signal n           : signed(63 downto 0);
  signal itterNStep  : signed(63 downto 0);
  signal bufferNStep : signed(63 downto 0);

  signal unitPhase     : unsigned(PHASE_POWER downto 0);
  signal unitPhaseStep : signed(PHASE_POWER downto 0);

begin

  unitPhaseStep <= to_signed(doppler_shift, unitPhaseStep'length);

  process (clk, reset)
    variable tmp_n : signed(n'range);
  begin
    if reset = '1' then
      itterNStep  <= to_signed(subCycles * inputRate, itterNStep'length); -- could these 2 be made constants -> probably yes, but how?
      bufferNStep <= to_signed(subCycles * outputRate, bufferNStep'length);
      n           <= to_signed(0, n'length);
      unitPhase   <= to_unsigned(0, unitPhase'length);
      enable_modulation <= DISABLED;

      IQ_output <= (i => (others => '0'), q => (others => '0'));

    elsif rising_edge(clk) then
      if enable = ENABLED then

        -- is this order needed or can i make the calc chain shorter(1 sample more delay)
        tmp_n := n + itterNStep - delay_step; -- i am stearing on delay step, no feedback, will this work? need good external controle.
        if tmp_n >= bufferNStep then -- tmp_n -> n?
          n <= tmp_n - bufferNStep;
          enable_modulation <= ENABLED;
        else
          n <= tmp_n;
          enable_modulation <= DISABLED;
        end if;
    
        IQ_output <= rotate_IQ(IQ_input, unitPhase); -- can this be moved outside of the process, i think so -> faster responce, less waist at the start?
    
        unitPhase <= unitPhase+unsigned(unitPhaseStep); -- should overflow and go around at the correct times

      else
        enable_modulation <= DISABLED;
      end if;
    end if;

  end process;

end arch1;