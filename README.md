# Some Notices

1. Multi-tasking is not available even with '''runloop''' class

2. async / await function needs to be call with the runloop.run in order to run stably. One can try to run the function directly without using async/await, and it will still compile and run. Just that the delay is now instable(From observation sometime it does work, which is weird. 

3. From observation, it roughly takes 
```
theta = 0.35 * 360
```
to make a 90 $degree$ turn with the default small robot with big wheels

4. In distance_sensor class, both get_pixel and set_pixel methods have outdated api docs. The light matrix on the distance sensor has components only range from {0,1} instead {0~3}

