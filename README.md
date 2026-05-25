# Some Notices

1. Multi-tasking is not available even with '''runloop''' class

2. async / await function needs to be call with the runloop.run in order to run stably. One can try to run the function directly without using async/await, and it will still compile and run. Just that the delay is now instable(From observation sometime it does work, which is weird. 

3. From observation, it roughly takes 
```
theta = 0.35 * 360
```
to make a 90 $degree$ turn with the default small robot with big wheels

4. In distance_sensor class, both get_pixel and set_pixel methods have outdated api docs. The light matrix on the distance sensor has components only range from {0,1} instead {0~3}

# Reverse Engineering
From [Chrome for developer](https://developer.chrome.com/blog/lego-education-spike-web-bluetooth-web-serial?hl=zh-tw). I see it's using BluetoothDevice or SerialPort

in index.js:

```js
            connect(e) {
                    return M(this, null, function*() {
                        try {
                            const n = yield navigator.serial.requestPort({
                                filters: [{
                                    usbVendorId: A.SerialVendorId.LEGO
                                }]
                            });
                            yield n.open({
                                baudRate: 115200
                            }),
                            this.keepReading = !0,
                            this.receive(n),
                            this.port = n;
                            const o = this.getProductId(n);
                            return this.device = {
                                id: o.toString(),
                                serial: {
                                    productId: o,
                                    vendorId: A.SerialVendorId.LEGO
                                },
                                type: _e.USB,
                                name: o.toString()
                            },
                            navigator.serial.addEventListener("disconnect", i => {
                                const a = this.getProductId(i.target);
                                a === o && this.onSerialDisconnected(a.toString())
                            }
                            ),
                            this.device
                        } catch (n) {
                            return null
                        }
                    })
                }
```

Also in line 11182: 
```js
k5 = JSON.parse('{"Q":{"/typeshed/stdlib/_ast.pyi":"import sys\\nfrom typing import Any,    ...
```
We can find the supported library. This line is too lone to show but you can use the "find" tool to ensure its inside the modified micropython
We can only use a subset of asyncio

# procedures (according to gemini)

1. putty into the BL serial, ctrl+c. This will enter the REPL

2. ctrl+E to enter the paste mode

3. paste the code

4. ctrl+d   

5. control the car. it should be listening to bluetooth via call_back


# About Final:
## motivation:
Lego spike is definitely running RTOS. You can run you custom program, but nomatter what there's a daemon-like program updating sensor data

However, they don't expose the RTOS cntrol to you. They forbid the use "asyncio" api, also the "runloop" api doesn't realy support multi-tasking. So to achieve multi-tasking we implement a software-level corperate scheduler.
## flowchart
main

## implementation:
Every task will need to inherit the dummy parent class "Task", and override the __init__(), and run() in child.
The main loop run the corresponding task if the current_time - i.last_time >= i.period.

1. balence task(5ms): the balance car can stay balance and turn to the given yaw goal
2. song task({custom}ms): this part sing "Never Gonna Give You Up"
3. A* visualization task(500ms): this part visulize the a star path finding algorithm.