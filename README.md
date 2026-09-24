# SPC 3000 
The Survival Personal Computer 3000 is an open-source post-apocalyptic forearm PC inspired by the *Pip-Boy* from *Fallout New Vegas*.

<img width="717" height="467" alt="image" src="https://github.com/user-attachments/assets/46e5624c-05e2-4e9f-b137-e420c69d9e3c" />


## Features
- **Radiation Monitoring:** Built-In Geiger counter to detect gamma and beta radiation so you know where you should NOT go
- **Radio:** Integrated Mini-Speaker and Radio Module to feel the Nuclear Vibes
- **Clock:** The Real Time Clock (RTC) Module will wake you up always at the right time. As they say "The early bird gets the Radroach"
- **Reinforced structure:** M2 and M3 screws with some glue and neodimium magnets will make this Pip-Boy indestructible
- **Compatibility:** with a Usb-c port for charging, a Usb port for inputs (ex: Mouse or Keyboard), and a HDMI integrated cable for screen mirroring, you can always connect with older and newer technologies alike
## Hardware & Bill of materials
You can find the detailed cost breakdown, component list and buying links in my [BOM.md](./BOM.md) and [BOM.csv](./BOM.csv) files (shipping prices included). The wiring schematics are situated in the [Schematics Folder](Schematics/). **ATTENTION: the schematics only show the connections that need to be soldered**, that's why in the top-right area of the schematics there are 2 Isolated components (USB port and Micro USB) which are soldered so as to form a cable that connects to the Raspberry via Micro USB, that's also why there is no MiniHDMI to HDMI cable, which also connects to the Raspberry using its MiniHDMI port.

<img width="1169" height="828" alt="Schematic_Survival-PC-3000_2026-08-28" src="https://github.com/user-attachments/assets/d56d64b9-3732-40b0-b53e-235eac7d7f3e" />

## Software
The device runs a **Raspberry Pi OS (Legacy 32-bit with Desktop)** on a Raspberry Pi Zero 2W and a some custom made Python scripts (**Pip-Boy OS**) to interface with sensors, a touch screen and analog inputs (that stay true to the Pip-Boy style ). **To see the Pip-Boy OS README [click here](Software/README%20(Pip-Boy%20OS).md)**

<img width="390" height="316" alt="Screenshot 2026-07-18 170426" src="https://github.com/user-attachments/assets/3f1b723f-4dd3-4424-a425-d9b1af67f751" />

<img width="397" height="316" alt="Screenshot 2026-08-27 130842" src="https://github.com/user-attachments/assets/0c52e5ed-df51-482c-84d8-b31679faa2be" />

## Important Information (For the SPC 3000, for the Pip-Boy OS [click here](Software/README%20(Pip-Boy%20OS).md))
1) **Some parts of the project are not mine**, I took some scripts and 3D models online, in order to make my project as similar as possible to the  model that inspired it. All the elements I took online are listed in the [BOM.md](./BOM.md) file;
2) **The Solar Panel Add-on will NOT be implemented in the SPC 3000 for the stardance shipping** (because I'm lacking the time to make the 3D model for a support), **Hack Club you can remove the solar panel from the total price or you can keep it**, I don't mind, however after stardance I'll work on implementing said add-on;
3) **The analog input is not completely loyal to the games**, the wheel is too small, and replacing it with a second rotary encoder occupies too much space (as an input it will work, however I'll try to replace it after stardance);  there is no knob (I'll 3D print it when I'll get a printer probably); and the buttons have a strange metal piece at the center (whereas the buttons of the Pip-Boy are completeley made of orange plastic). I couldn't find the perfect hardware pieces so I had to compromise, hope that you'll understand.
