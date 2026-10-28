# SPC 3000 (and [Pip-Boy OS](Software/README%20(Pip-Boy%20OS).md) )
The Survival Personal Computer 3000 is a forearm PC inspired by the *Pip-Boy* from *Fallout New Vegas*.

<img width="717" height="467" alt="image" src="https://github.com/user-attachments/assets/46e5624c-05e2-4e9f-b137-e420c69d9e3c" />


## Features
- **Radiation Monitoring:** Built-In Geiger counter to detect gamma and beta radiation so you know where you should NOT go
- **Radio:** Integrated Mini-Speaker and Radio Module to feel the Nuclear Vibes
- **Clock:** The Real Time Clock (RTC) Module will wake you up always at the right time. As they say "The early bird gets the Radroach"
- **Compatibility:** with a Usb-c port for charging, a Usb port for inputs (ex: Mouse or Keyboard), and a HDMI integrated cable for screen mirroring, you can always connect with older and newer technologies alike
## Hardware & Bill of materials
You can find the detailed cost breakdown, component list and buying links in my [BOM.md](./BOM.md) and [BOM.csv](./BOM.csv) files (shipping prices included). The wiring schematics are situated in the [Schematics Folder](Schematics/). **ATTENTION: the schematics only show the connections that need to be soldered**, that's why in the top-right area of the schematics there are 2 Isolated components (USB port and Micro USB) which are soldered so as to form a cable that connects to the Raspberry via Micro USB, that's also why there is no MiniHDMI to HDMI cable, which also connects to the Raspberry using its MiniHDMI port.

<img width="1169" height="828" alt="Schematic_Survival-PC-3000_2026-08-28" src="https://github.com/user-attachments/assets/d56d64b9-3732-40b0-b53e-235eac7d7f3e" />

## Software
The device runs a **Raspberry Pi OS (Legacy 32-bit with Desktop)** on a Raspberry Pi Zero 2W and a some custom made Python scripts (**Pip-Boy OS**) to interface with sensors, a touch screen and analog inputs (that stay true to the Pip-Boy style ). **To see the Pip-Boy OS README [click here](Software/README%20(Pip-Boy%20OS).md)**

<img width="390" height="316" alt="Screenshot 2026-07-18 170426" src="https://github.com/user-attachments/assets/3f1b723f-4dd3-4424-a425-d9b1af67f751" />

<img width="397" height="316" alt="Screenshot 2026-08-27 130842" src="https://github.com/user-attachments/assets/0c52e5ed-df51-482c-84d8-b31679faa2be" />

### PARTS NOT MINE:

-**3d Model of the casing:** I used [This 3D Pip-Boy case](https://ytec3d.com/pip-boy/) as a base and then heavily modified it to make space for the hardwware

-**Pip-Boy menu:** I used [This Pip-Boy menu on github](https://github.com/kelmes1/pipboy-pi/tree/main) as a base to develop my code (the code has suffered extreme changes, only a few files remained unchanged)

-**Icons:** they are taken from the [Iconify archive](https://icon-sets.iconify.design/ ) and all have MIT or Apache 2.0 licensing (No attribution required, commercial use is allowed)

-**Songs:** they are taken from the [Internet Archive](https://archive.org/search?query=78+rpm+records&tab=all ) and are all 78 rpm songs from 1930s/1940s that are in the public domain

-**SFXs:** inherited from the base open-source repository (I don't know the origin of those SFXs; can be removed/replaced if required)

## Important Information (For the SPC 3000, for the Pip-Boy OS [click here](Software/README%20(Pip-Boy%20OS).md))
1) **In this repo there aren't any Images and sfxs**: As I'm european and european laws are a hassle and a half, I've decided to not insert any images or sfxs that could've broken the [Bethesda Copyright Policies](https://documents.bethesda.net/en/legal-information). I know, this will cost me dearly stardust-wise, but I'd rather be a bitch about it than lose the project.
2) **There is NO FIRMWARE**: the project uses a raspberry and, because I'm not using custom PCBs, it doesn't need a firmware. The only thing near to a firmware is the [hardware_inputs](./Software/Pip-Boy%20OS/modules/hardware_input.py ) file, which links the inputs from the GPIO ports of the Raspberry to their repsective PC Button/s (example: knob == A/D key);
3) **Some parts of the project are not mine**, I took some scripts and 3D models online, in order to make my project as similar as possible to the  model that inspired it. All the elements I took online are listed in the [BOM.md](./BOM.md) file;
4) **The Solar Panel Add-on will NOT be implemented in the SPC 3000 for the stardance shipping** (because I'm lacking the time to make the 3D model for a support), **Hack Club you can remove the solar panel from the total price or you can keep it**, I don't mind, however after stardance I'll work on implementing said add-on;
5) **The analog hardware aren't completely loyal to the games**, the wheel is too small, and replacing it with a second rotary encoder occupies too much space (as an input it will work, however I'll try to replace it after stardance);  there is no knob (I'll 3D print it when I'll get a printer probably); and the buttons have a strange metal piece at the center (whereas the buttons of the Pip-Boy are completeley made of orange plastic). I couldn't find the perfect hardware pieces estetically so I had to compromise in order to get at least the inputs right, hope that you'll understand;
6) **There is NO CUSTOM PCB**: The SPC 3000 only uses electronics parts that are on the market, this is because I never designed Custom PCBs and I think that this choice adds depth to the project making it easily repairable. That's also why the Kicad files (except the sch file) are empty;
7) **If there are issues please report them in the Issues section**: This is my first Python program and My first electric diagram, so any reported issue is an occasion for me to grow, while optimizing the project.
