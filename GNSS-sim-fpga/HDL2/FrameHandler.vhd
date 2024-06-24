library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.GNSSsettings.all;

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
    next_frame        : in Frame_t;
    peek_frame        : in Frame_t
  );
end FrameHandler;

architecture behavioral of FrameHandler is

  signal current_bit : integer range 0 to bits+1 := 0;
  signal frame_record : FrameRecord_t;
  signal peek_frame_record : FrameRecord_t;

  signal peek_bit : std_logic;
begin

  frame_record <= frame_to_record(next_frame);
  peek_frame_record <= frame_to_record(peek_frame);

  -- check if assignments are correct
  prn           <= frame_record.prn;
  --data          <= frame_record.bits(current_bit);
  delay_step    <= frame_record.delay_step;
  doppler_shift <= frame_record.phase_step;
  power         <= frame_record.power;

  process(current_bit, frame_record, peek_frame_record)
  begin
    if current_bit=bits or current_bit=bits+1 then
      data <= peek_bit;--peek_frame_record.bits(0);
    else
      data <= frame_record.bits(current_bit);
    end if;
  end process;

  --enable_next_frame <= To_Std_Logic((enable=ENABLED) and (current_bit=current_bit_high-1));

  process (clk, reset)
  begin
    if reset = '1' then
      enable_next_frame <= '0';
    elsif rising_edge(clk) then
      if enable=ENABLED then
        if current_bit=bits-1 then
          enable_next_frame <= ENABLED;
          peek_bit <= peek_frame_record.bits(0);
        else
          enable_next_frame <= DISABLED;
        end if;
        if current_bit=bits or current_bit=bits+1 then
          current_bit <= 1;
        else 
          current_bit <= current_bit+1;
        end if;
      else
        enable_next_frame <= DISABLED;
        if current_bit=bits then
          current_bit <= current_bit+1;
        elsif current_bit=bits+1 then
          current_bit <= 0;
        end if;
      end if;
    end if;
  end process;
end behavioral;