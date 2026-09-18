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
The device runs a **Raspberry Pi OS (Legacy 32-bit with Desktop)** on a Raspberry Pi Zero 2W and it uses some custom python scripts to interface with sensors, a touch screen and analog inputs (that stay true to the Pip-Boy style ). The python scripts are built so as to emulate the Pip-Boy Operating Systems from the games Fallout 4 and Fallout New Vegas; the Pip-Boy OS that you can find in the repo can also be personalized using the [configure.py](Software/Pip-Boy%20OS/configure.py) file. To start the code you need to run [main.py](./Software/Pip-Boy%20OS/modules/main.py) in Python, all the requirements are listed in the [requirements file](./Software/Pip-Boy%20OS/requirements.txt). The Pip-Boy OS can run on PC and it uses for input:
- **Left Arrow**: to move to the menu to the left
- **Right Arrow**: to move to the menu to the right
- **Up Arrow**: to change between the CND/EFF/RAD tabs in the *Fallout: New Vegas* UI or to move upwards on the lists in the tabs or to zoom in in the MAP tab/menu
- **Down Arrow**:  to change between the CND/EFF/RAD tabs in the *Fallout: New Vegas* UI or to move downwards on the lists in the tabs or to zoom out in the MAP tab/menu
- **A**: to change to the tab to the left
- **D**: to change to the tab to the right
- **I**: to move up in the MAP tab/menu
- **K**: to move down in the MAP tab/menu
- **J**: to move left in the MAP tab/menu
- **L**: to move right in the MAP tab/menu

<img width="390" height="316" alt="Screenshot 2026-07-18 170426" src="https://github.com/user-attachments/assets/3f1b723f-4dd3-4424-a425-d9b1af67f751" />

<img width="397" height="316" alt="Screenshot 2026-08-27 130842" src="https://github.com/user-attachments/assets/0c52e5ed-df51-482c-84d8-b31679faa2be" />

## Important Information
1) **Some parts of the project are not mine**, I took some scripts and 3D models online, in order to make my project as similar as possible to the  model that inspired it. All the elements I took online are listed in the [BOM.md](./BOM.md) file;
2) **The Pip-Boy OS in the repo is still a WIP**, **the code works perfectly ON PC**, however the Fallout New Vegas UI is not complete yet: I still need to add to the code the DATA tabs of Fallout 4 and Fallout New Vegas, the Fallout New Vegas Radio Stations and everything that needs the hardware to work (Geiger counter that changes in real time, a Clock Tab, a way to connect the Pip-Boy OS to the Raspberry Pi OS, a Connection to IRL Radio Stations );
3) **The Solar Panel Add-on will NOT be implemented in the SPC 3000 for the stardance shipping** (because I'm lacking the time to make the 3D model for a support), **Hack Club you can remove the solar panel from the total price or you can keep it**, I don't mind, however after stardance I'll work on implementing said add-on;
4) **The analog input is not completely loyal to the games**, the wheel is too small, and replacing it with a second rotary encoder occupies too much space (as an input it will work, however I'll try to replace it after stardance);  there is no knob (I'll 3D print it when I'll get a printer probably); and the buttons have a strange metal piece at the center (whereas the buttons of the Pip-Boy are completeley made of orange plastic). I couldn't find the perfect hardware pieces so I had to compromise, hope that you'll understand.
