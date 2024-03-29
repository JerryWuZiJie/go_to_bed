# go_to_bed
This project is intend for CE DP2

## Description
We know from the Internet (forums) and in our daily lives that most people, especially young people, find it difficult to control themselves from going to bed early at night. 
After an investigation on the Internet, it was found that there is no device on the market that can truly satisfy users to solve this problem, as a result, we decide to build an alarm clock that tries to make people sleep early.

## How It Works
The alarm clock will monitor your phone status and environment lights. Once your light is off and your phone is not in use, the clock will consider you are asleep and record your sleep time. This sleep time will compare to others, reward the winner, and produce peer pressure by displaying what percentage of other users have gone to bed on time so far to push everyone to sleep on time.

The clock also has two modes: Normal mode and Supervision mode, which allows it to adapt to more different user groups. 

## Implementation
We will build the hardware device using raspberry pi zero w, and implement software using mainly Python.

## Contact
Member #1: 
Yingzhuo Yang.
Email: yy3826@nyu.edu

Member #2: 
Zijie Wu.
Email: zw1711@nyu.edu

## File Structure
- ### docs
    Documents such as datasheet \
    Also contains pictures used in markdown files
- ### sound
    Sound file used by speaker module
- ### utils.py
    Contains all low level functions and classes that can be used directly
- ### demo.py
    A demo on how to use the functions and classes in utils.py

## Common Errors
- ```AttributeError: module 'pygame.mixer_music' has no attribute 'unload'``` \
    update pygame to latest version
- ```NotImplementedError: mixer module not available``` \
    install libsdl2-mixer-2.0-0 by running ```sudo apt install```
- ```OSError: libespeak.so.1: cannot open shared object file: No such file or directory``` \
    Install espeak by running ```sudo apt install espeak```

