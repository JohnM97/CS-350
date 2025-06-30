# CS-350
Project Reflection

Over the semester, I took a vanilla Raspberry Pi from fresh OS install through a series of hands-on labs—SSH setup, GPIO button and LED control, I²C sensor readings, state-machine design, threading, and finally a full thermostat system. Each module built on the last: we learned to connect and configure hardware, write clean Python drivers, manage concurrent tasks, and model behavior as states. By the end, I had an embedded application that maintained a target temperature automatically.
What did you do particularly well?

I kept each lab’s code modular—separating hardware interface, control logic, and user I/O—so I could reuse GPIO and sensor classes in later assignments. My state-machine implementations clearly mapped out transitions, and I used threading smartly to poll sensors without blocking the main loop. I documented every step, from Pi network configuration to Python dependencies, making setup repeatable.
Where could you improve?

I didn’t introduce automated testing early enough; I relied on the actual hardware for almost every change. Next time I’d mock GPIO and sensor inputs so I could catch logic bugs on my laptop. I also learned that extracting all pin mappings and thresholds into a single config file sooner would have saved time when lab requirements changed.
What tools and resources are now in my support network?

I regularly reference the Raspberry Pi official docs, the gpiozero library reference, and community Q&A on Raspberry Pi Stack Exchange. I’ve bookmarked Python’s unittest.mock and pytest guides for hardware simulation, and I use GitHub Actions to run linting and tests on every commit.
Which skills from this course are most transferable?

Designing and documenting finite-state machines, writing hardware-abstraction layers, and managing concurrent tasks all apply to robotics, IoT, and backend systems with background workers. Learning to configure Linux headlessly over SSH and automate deployments is also vital for any devops or cloud-infrastructure work.
How did I make the work maintainable, readable, and adaptable?

– Modular code structure: hardware drivers, control logic, and user interfaces live in separate modules.
– Single source of truth: all pin numbers, I²C addresses, and temperature thresholds in one config file.
– Clear documentation: README setup steps, inline comments, and class-docstrings guide future contributors through wiring and code usage.
– Version control: small, focused commits for each lab ensure a clear history and easy rollback.
