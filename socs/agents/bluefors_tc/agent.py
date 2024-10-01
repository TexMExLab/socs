import os
import argparse
import requests
import json

import txaio
from ocs import ocs_agent, site_config
from ocs.ocs_twisted import TimeoutLock

# For logging
txaio.use_twisted()

TIMEOUT = 30

class BlueforsTCAgent:
    def __init__(self, agent, ip):
        self.agent = agent
        self.ip = ip
        self.url = f'http://{self.ip}:5001'
        self.lock = TimeoutLock()

    @ocs_agent.param('setpoint', type=float)
    @ocs_agent.param('heater', default=4, type=int, choices=[1, 2, 3, 4])
    def set_setpoint(self, session, params):
        """set_setpoint(setpoint=None,heater='2')

        **Task** - Sets the setpoint of the heater control loop,
        after first turning ramp off. May be a limit to how high the setpoint
        can go based on your system parameters.

        Parameters:
            setpoint (float): The setpoint for the control loop. Units depend
                              on the preferred sensor units (Kelvin, Celsius,
                              or Sensor).
            heater (str, optional): Default '2'. Selects the heater for which
                                    to set the input channel.
                                    Must be '1' or '2'.
        """
        with self.lock.acquire_timeout(job='set_setpoint', timeout=3) as acquired:

            if not acquired:
                print(
                    f"Lock could not be acquired because it is held by "
                    f"{self._lock.job}")
                return False, 'Could not acquire lock'

            cmd_dict = {
                'heater_nr' : params['heater'],
                'setpoint' : params['setpoint'],
                'active' : True,
                'pid_mode' : 1
            }

            req = requests.post(f'{self.url}/heater/update', json=cmd_dict, timeout=TIMEOUT)
            if not (req.json()['status'] == 'OK' and req.json()['pid_mode'] == 1 and req.json()['active']):
                return False, f'Setting the PID setpoint failed: {req.json()}'
            else:
                return True, 'Set setpoint successfull'

def make_parser(parser=None):
    """Build the argument parser for the Agent. Allows sphinx to automatically
    build documentation based on this function.

    """
    if parser is None:
        parser = argparse.ArgumentParser()

    # Add options specific to this agent.
    pgroup = parser.add_argument_group('Agent Options')
    pgroup.add_argument('--ip-address')

    return parser

def main(args=None):
    txaio.start_logging(level=os.environ.get("LOGLEVEL", "info"))

    parser = make_parser()
    args = site_config.parse_args(agent_class='BlueforsTCAgent', parser=parser, args=args)

    #init_params= False
    #if args.auto_acquire:
    #    init_params = {'auto_acquire':True}

    agent, runner = ocs_agent.init_site_agent(args)

    tc = BlueforsTCAgent(agent, args.ip_address)

    #agent.register_task('init', tc.init)
    agent.register_task('set_setpoint', tc.set_setpoint)

    runner.run(agent, auto_reconnect=True)

if __name__ == '__main__':
    main()
