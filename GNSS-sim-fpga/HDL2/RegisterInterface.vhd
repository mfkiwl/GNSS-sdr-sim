library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.settings.all;

entity RegInterface is
  port
  (
    reg0 : in std_logic_vector(31 downto 0);
    reg1 : in std_logic_vector(31 downto 0);
    reg2 : in std_logic_vector(31 downto 0);
    reg3 : in std_logic_vector(31 downto 0);
    reg4 : in std_logic_vector(31 downto 0);
    reg5 : in std_logic_vector(31 downto 0);
    reg6 : in std_logic_vector(31 downto 0);
    reg7 : in std_logic_vector(31 downto 0);
	
	frame       : out std_logic_vector(175 downto 0);
	clock_reset : out std_logic;
	gnss_reset  : out std_logic;
	gnss_enable : out std_logic;
	gnss_store  : out std_logic
  );
end RegInterface;

architecture structural of RegInterface is
	
	signal frame_record : FrameRecord_t;

begin

	frame_record.chanel <= reg0( 7 downto  0);
    frame_record.prn    <= reg0(15 downto  8);
	frame_record.power  <= reg0(23 downto 16);
	
    bits(31 downto  0)  <= reg1;
	bits(63 downto 32)  <= reg2;
	
	delay_step(31 downto  0)   <= reg3;
	delay_step(63-8 downto 32) <= reg4(31-8 downto 0);
	
    phase_step  <= reg5;
	
	gnss_store  <= reg6(0);
	
	clock_reset <= reg7(0);
	gnss_reset  <= reg7(1);
	gnss_enable <= reg7(2);
	
	frame <= record_to_frame(frame_record);
	
end structural;