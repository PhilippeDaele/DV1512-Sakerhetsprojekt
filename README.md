
# DV1512 Security project in group, focus on system development
In today's digital landscape, security is paramount for any software development project, especially when it involves web applications. This project will delve into a software development project with a primary focus on security. The project aims to create a website that simulates surveillance cameras and provides users the ability to switch them on and off at will. However, the unique aspect of this project lies in its emphasis on identifying and mitigating potential security vulnerabilities through attack simulations.

## Features
- Login page
- As Admin you are able to
   * Ability to add and delete cameras (Add cameras with rightclick)
   * Reboot cameras if they are down
   * See log for changes
   * Change status for each camera
   * See the camera feed
- As a normal user you are able to
   * See status for each camera
- Functional database
- Responsive website
- Google Maps
    * Shows camera(s)
    * Fullscreen mode




## Installation

Download/clone the project and run in terminal

```bash
  make
```
To turn off and clean up the running processes
```
make clean
```
## Attack scenarios
Since this is a simulation of IP Surveillance systems we have implemented 3 attack scenarios that are likley to happen in the wild.
1. SQL Injection on the login page
2. (D)DoS Attack against Cameras
3. Be able to switch them on and off as a none admin user
The last 2 attacks were implemented in a bash script that can be run in the console. This script is called SpyCam.sh and this can be run as followed.

* chmod +x SpyCam.sh
* ./SpyCam.sh
But you can also run it in the browser if you move into the folder called pyxtermjs or check out this github https://github.com/cs01/pyxtermjs.
If you clone the project from his repository you need to change the port it starts to from port 5000 to something like 7000. (This is done already in the folder provided in our repository)
The script will explain each step you have to take to run a successfull attack against the simulation.

## High-level overview
The project is mainly written with python3, JS, HTML and CSS with google maps used for the map seen on the front page overview.
The cameras and frontend is run with python flask. Since we cant simulate real cameras we had to create a framework that acted as the cameras. 
This made the simulation almost entirely work with the http-request as the communication protocol. 

![bild](https://github.com/PhilippeDaele/DV1512-Sakerhetsprojekt/assets/99668019/0b9295e4-19f4-4c7e-8d66-4e15f4c4eb51)
This is what the user sees when the login page is accessed, we have created 2 users.
1. User with the highest access, with the credentials admin:admin. This user can change the status for the camera, add and delete cameras and also reboots them with a push of a button.
2. A normal level user with the credentials user:user that is used mainly for checking the live feed from the cameras. This is what the attacker will use for the entry point.
![bild](https://github.com/PhilippeDaele/DV1512-Sakerhetsprojekt/assets/99668019/3712f287-9f48-4495-bda9-5bfd8e4f8a83)
This is what is seen when the user have logged in as admin. Here the user that move around the map, check the status and live feed for each camera, add and delete cameras. The user can also check the log file in the log tab to see if anything fishy have happend to the site.

    
## Acknowledgements

- [Blekinge Institute of Technology](www.bth.se)
- [Oleksandr Adamov](https://www.bth.se/?s=Oleksandr%20Adamov&searchtype=employee)
- [Nina Dzamashvili Fogelström](https://www.bth.se/?s=Oleksandr+Adamov&searchtype=employee&employee-filter=&s=Nina+Dzamashvili+Fogelstr%C3%B6m+)


## Authors

- [Philippe Van Daele](https://www.github.com/PhilippeDaele)
- [Marcus Björnbäck](https://github.com/maRkyB0019)
- [Xiao Zhu](https://github.com/imsanqian)
- [Le Hoang Long Bui](https://github.com/LeHoangLong2610)
- [Al Ghaith Ahmad](https://github.com/ghaithahmad)

