import pygame
import threading
import settings

try:
    from gpiozero import Button, RotaryEncoder, DigitalInputDevice
    import smbus2 as smbus
    GPIO_AVAILABLE = True
except (ImportError, NotImplementedError):
    GPIO_AVAILABLE = False

class TEA5767Radio:
    def __init__(self, bus_number=1, address=0x60):
        self.address = address
        self.bus_number = bus_number
        self.bus = None
        if GPIO_AVAILABLE:
            try:
                self.bus = smbus.SMBus(self.bus_number)
            except Exception as e:
                print(f"[Hardware Error] Reading of I2C for FM Radio module failed: {e}")

    def set_frequency(self, frequency_mhz):
        if not self.bus:
            return
        try:
            frequency = int((frequency_mhz + 0.225) * 4 / 0.032768)
            buffer = [
                (frequency >> 8) & 0x3F,
                frequency & 0xFF,
                0xB0,
                0x10,
                0x00
            ]
            self.bus.write_i2c_block_data(self.address, buffer[0], buffer[1:])
        except Exception as e:
            print(f"[FM Radio Error] Syncronization error: {e}")


class HardwareInputManager:
    def __init__(self, tab_manager=None):
        self.tab_manager = tab_manager
        self.active_rot1_position = 0
        self.fm_radio = TEA5767Radio()
        
        ui_style = str(getattr(settings, 'UI_STYLE', 'fallout_4')).lower()
        self.is_nv = ui_style in ('fallout_nv', 'fallout_new_vegas')

        if not getattr(settings, 'RASPI', False) or not GPIO_AVAILABLE:
            print("[Hardware] Raspberry not detected/GPIO deactivated\nSimulated Inputs: ON")
            return

        try:
            # 1. THE 3 MAIN BUTTONS
            self.btn_s1 = Button(17, pull_up=True, bounce_time=0.05)
            self.btn_s2 = Button(27, pull_up=True, bounce_time=0.05)
            self.btn_s3 = Button(22, pull_up=True, bounce_time=0.05)

            if self.is_nv:
                # New Vegas UI: S1 = STATS (0), S3 = ITEMS/INV (1), S2 = DATA (2)
                self.btn_s1.when_pressed = lambda: self._handle_nv_button(0)
                self.btn_s3.when_pressed = lambda: self._handle_nv_button(1)
                self.btn_s2.when_pressed = lambda: self._handle_nv_button(2)
            else:
                # Fallout 4: S1 = LEFT KEY, S3 = RETURN, S2 = RIGHT KEY
                self.btn_s1.when_pressed = lambda: self._inject_key(pygame.K_LEFT)
                self.btn_s2.when_pressed = lambda: self._inject_key(pygame.K_RIGHT)
                self.btn_s3.when_pressed = lambda: self._inject_key(pygame.K_RETURN)

            # 2. SCROLL WHEEL (ROTARY SWITCH) -> UP/DOWN KEY
            self.encoder = RotaryEncoder(a=5, b=6, wrap=False, max_steps=100)
            self.wheel_btn = Button(13, pull_up=True, bounce_time=0.05)
            self.wheel_btn.when_pressed = lambda: self._inject_key(pygame.K_x)
            
            self.last_encoder_steps = self.encoder.steps
            self.running_wheel = True
            threading.Thread(target=self._monitor_encoder, daemon=True).start()

            # 3. KNOB 1P5T (ROT1) -> CHANGE SUB-TAB
            self.rot1_pins = [19, 26, 20, 21, 16]
            self.rot1_devices = [DigitalInputDevice(pin, pull_up=True) for pin in self.rot1_pins]
            
            for index, device in enumerate(self.rot1_devices):
                device.when_activated = lambda idx=index: self._handle_rot1_change(idx)

            # 4. CONTATORE GEIGER (U4)
            self.geiger_sensor = Button(4, pull_up=True, bounce_time=0.01)
            self.geiger_sensor.when_pressed = self._handle_geiger_pulse

            # 5. MODULO RTC (DS3231)
            self._verify_rtc_sync()

            print("[Hardware] Input configuration complete.")
        except Exception as e:
            print(f"[Hardware Error] Error in GPIO inizialization: {e}")

    def _handle_nv_button(self, target_tab_index):
        """In NV UI, pressing / holding the button of the open Menu will be interpreted as RETURN / X"""
        if not self.tab_manager:
            return

        current_index = getattr(self.tab_manager, 'current_tab_index', 0)
        
        if current_index == target_tab_index:
            # If we are in the related tab use RETURN
            self._inject_key(pygame.K_RETURN)
        else:
            # If we aren't in the related menu, change menu
            if hasattr(self.tab_manager, 'navigate'):
                self.tab_manager.navigate(target_tab_index)
            else:
                diff = target_tab_index - current_index
                key = pygame.K_RIGHT if diff > 0 else pygame.K_LEFT
                for _ in range(abs(diff)):
                    self._inject_key(key)

    def _inject_key(self, key):
        event = pygame.event.Event(pygame.KEYDOWN, key=key)
        pygame.event.post(event)

    def _monitor_encoder(self):
        while self.running_wheel:
            current_steps = self.encoder.steps
            if current_steps > self.last_encoder_steps:
                self._inject_key(pygame.K_DOWN)
                self.last_encoder_steps = current_steps
            elif current_steps < self.last_encoder_steps:
                self._inject_key(pygame.K_UP)
                self.last_encoder_steps = current_steps
            pygame.time.wait(20)

    def _handle_rot1_change(self, position_index):
        self.active_rot1_position = position_index
        if position_index > getattr(self, '_last_pos', 0):
            self._inject_key(pygame.K_d)
        else:
            self._inject_key(pygame.K_a)
        self._last_pos = position_index

    def _handle_geiger_pulse(self):
        if hasattr(settings, 'RADIATION_VALUE'):
            settings.RADIATION_VALUE += 5
            settings.RADIATION_CURRENT = min(100, settings.RADIATION_VALUE // 10)

    def _verify_rtc_sync(self):
        try:
            bus = smbus.SMBus(1)
            bus.read_byte(0x68)
        except Exception:
            pass