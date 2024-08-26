# Introduction to the Bluesky Queueserver

Last edit 03-25-2024 by VC

work-in-progress: *very* basic notes for now

- [Introduction to the Bluesky Queueserver](#introduction-to-the-bluesky-queueserver)
  - [Run the queueerver](#run-the-queueerver)
    - [operations (edited by parkjs per email from jemian 2024-04-04)](#operations-edited-by-parkjs-per-email-from-jemian-2024-04-04)
    - [diagnostics and testing](#diagnostics-and-testing)
  - [graphical user interface](#graphical-user-interface)

**IMPORTANT**:  When the queueserver starts, it **must** find only one `/.py` file in this directory and it must find `instrument/` in the same directory.  Attempts to place the qserver files in a sub directory result in `'instrument/' directory not found` as queueserver starts.

To run queueserver, **must** first activate a bluesky environment. Can use `conda deactivate` followed by a `conda activate [ENVIRONMENT]` command, or can simply use alias `become_bluesky` to do it all in one. 
Current bluesky environment is `bluesky_2024_1`.

## Run the queueerver
### operations (edited by parkjs per email from jemian 2024-04-04)
To start the queueserver daemon: 
login to workstation: haydn.xray.aps.anl.gov
with account: s1idtest
commands:
- bash
- cd ~/bluesky
- ./qserver.sh restart

Stop queueserver with
- `./qserver.sh stop`

Verify if the dameon is running with this command:
- ./qserver.sh status

(base) s1idtest@kurtag ~/bluesky $ ./qserver.sh
Usage: qserver.sh {start|stop|restart|status|checkup|console|run} [NAME]

    COMMANDS
        console   attach to process console if process is running in screen
        checkup   check that process is running, restart if not
        restart   restart process
        run       run process in console (not screen)
        start     start process
        status    report if process is running
        stop      stop process

    OPTIONAL TERMS
        NAME      name of process (default: bluesky_queueserver-1id_hexm)
(base) s1idtest@kurtag ~/bluesky $ ./qserver.sh




Run in a background screen session.
`./qserver.sh start`

### diagnostics and testing
`./qserver.sh run`

## graphical user interface
`queue-monitor &`
- connect to the server
- open the environment
- add tasks to the queue
- run the queue
