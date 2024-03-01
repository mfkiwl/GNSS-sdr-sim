library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.settings.all;

entity FrameHandler is
  generic
  (
    bits : integer := 10
  );
  port
  (
    clk               : in std_logic;
    reset             : in std_logic;
    enable            : in std_logic;
    data              : out std_logic;
    doppler_shift     : out Doppler_t;
    delay_step        : out DelayStep_t;
    power             : out Power_t;
    prn               : out PRN_T;
    enable_next_frame : out std_logic := '0';
    next_frame        : in Frame_t
  );
end FrameHandler;

architecture behavioral of FrameHandler is
  constant current_bit_high : integer := bits-1;

  signal current_bit : integer range 0 to current_bit_high := 0;
  signal frame_record : FrameRecord_t;
begin

  frame_record <= frame_to_record(next_frame);

  -- check if assignments are correct
  prn           <= frame_record.prn;
  data          <= frame_record.bits(current_bit);
  delay_step    <= frame_record.delay_step;
  doppler_shift <= frame_record.phase_step;
  power         <= frame_record.power;

  process (clk, reset)
  begin
    if reset = '1' then
      enable_next_frame <= '0';
    elsif rising_edge(clk) then
      if enable=ENABLED then
        if current_bit=current_bit_high then
          current_bit <= 0;
          enable_next_frame <= ENABLED;
        else
          current_bit <= current_bit+1;
          enable_next_frame <= DISABLED;
        end if;
      else
        enable_next_frame <= DISABLED;
      end if;
    end if;
  end process;
end behavioral;