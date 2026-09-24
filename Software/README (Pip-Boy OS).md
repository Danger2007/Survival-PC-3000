# Pip-Boy OS

The Pip-Boy OS (or Pip-Boy Operating System) is the 'soul' of the SPC 3000. 
This is my first ever Python code, so I used a [half made base]() that I found online; I also used Gemini as a support in the making of the code, so as to understand Python faster and to speed up the programming process, however that doesn't mean that the code is AI slop, I came up with the logic and the AI just transcribed the logic in Python.

![Prenentation NV Gif](./Pip-Boy%20OS/documentation/screenshots/Record.gif)

## First Run Preparations And Requirements
All the software requirements are listed in the [requirements file](./Software/Pip-Boy%20OS/requirements.txt)
Before running the Pip-Boy OS for the first time you'll need to run the file **init** (init.bash if you are using windows; init.sh if you're using linux) these files create various vital files and folders in the Pip-Boy OS (it generates the '**cache**' folder and the '**settings_secret**' file). **In case init doesn't compile/run**: you have to manually add the cache folder with inside 2 folders named '**map**' and '**places**' and you have to add a Python file inside **modules** called '**settings_secret**' with these lines of code.

        REAL_LOCATION = 'YOUR_LOCATION'
        LONGITUDE = 00.0000
        LATITUDE = 00.000
        GEOAPIFY_KEY = 'YOUR_GEOAPIFY_KEY'
 
REMEMBER: if you want to see the IRL Map you need to insert in the code above your information (doesn't need to be true) and Create/Insert your Geoapify API Key (at https://www.geoapify.com/get-started-with-maps-api/ in the "Project and API Keys" section); DO NOT insert the URL (it doesn't work).
## How To Run
To start the code you need to run [main.py](./Software/Pip-Boy%20OS/modules/main.py), running other codes inside the software will not work. The code works perfectly on PC, give it a try!
![alt text](./Pip-Boy%20OS/documentation/screenshots/image-1.png)

## Customization
The Pip-Boy OS that you can find in the repo can also be personalized using the [configure.py](Software/Pip-Boy%20OS/configure.py) file. To start the code you need to run [main.py](./Software/Pip-Boy%20OS/modules/main.py) in Python, all the requirements are listed in the [requirements file](./Software/Pip-Boy%20OS/requirements.txt). To move in the configure.py UI you use as inputs:
- **Numpad 2**: to move down
- **Numpad 8**: to move up
- **ENTER**: To change/select an option

(Always make sure that the Numlock is **ON**)
![alt text](./Pip-Boy%20OS/documentation/screenshots/image.png)
## Inputs
The Pip-Boy OS uses for input:
- **Left Arrow**: to move to the menu to the left
- **Right Arrow**: to move to the menu to the right
- **Up Arrow**: to change between the CND/EFF/RAD tabs in the *Fallout: New Vegas* UI, to move upwards on the lists in the tabs or to zoom in in the MAP tab/menu
- **Down Arrow**:  to change between the CND/EFF/RAD tabs in the *Fallout: New Vegas* UI, to move downwards on the lists in the tabs or to zoom out in the MAP tab/menu
- **A**: to change to the tab to the left
- **D**: to change to the tab to the right
- **I**: to move up in the MAP tab/menu
- **K**: to move down in the MAP tab/menu
- **J**: to move left in the MAP tab/menu
- **L**: to move right in the MAP tab/menu
- **X**: to change the area that you are scrolling in Quests and Notes/Misc Tabs in the DATA Menu
- **ENTER**: To equip/unequip weapons/armor, to activate/disactivate quests, to chenge between the Reputation and General tabs in the Fallout: New Vegas STATS Menu

## Important information
- **This version might not work on the SPC 3000**: As I don't currently have the hardware I cannot check;
- **The Code can change**: If you see this README, it means that I shipped a DEMO of the software, a WIP with all UI elements working;
- **Not everything from the games is in the code**: I don't have enough time to insert all missions/notes/weaons etc... so for the Stardance event I'll just leave some elements from the games and some fallback Images to ease future additions.