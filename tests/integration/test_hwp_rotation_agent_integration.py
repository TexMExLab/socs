import pytest

import ocs
from ocs.base import OpCode

from ocs.testing import (
    create_agent_runner_fixture,
    create_client_fixture,
)

from integration.util import (
    create_crossbar_fixture
)

from socs.testing.device_emulator import create_device_emulator

pytest_plugins = ("docker_compose")

wait_for_crossbar = create_crossbar_fixture()
run_agent = create_agent_runner_fixture(
    '../agents/hwp_rotation/rotation_agent.py', 'hwp_rotation_agent', args=['--log-dir', './logs/'])
client = create_client_fixture('rotator')
kikusui_emu = create_device_emulator(
    {'SYST:REM': ''}, relay_type='tcp', port=2000)
pid_emu = create_device_emulator(
    {'*W02400000': 'W02\r'}, relay_type='tcp', port=2001)


@pytest.mark.integtest
def test_testing(wait_for_crossbar):
    """Just a quick test to make sure we can bring up crossbar."""
    assert True


@pytest.mark.integtest
def test_hwp_rotation_get_direction(wait_for_crossbar, kikusui_emu, pid_emu, run_agent, client):
    responses = {'*R02': 'R02400000\r'}
    pid_emu.define_responses(responses)
    resp = client.get_direction()
    print(resp)
    assert resp.status == ocs.OK
    print(resp.session)
    assert resp.session['op_code'] == OpCode.SUCCEEDED.value

    # Test when in reverse
    responses = {'*W02401388': 'W02\r',
                 '*R02': 'R02401388\r'}
    pid_emu.define_responses(responses)

    client.set_direction(direction='1')
    resp = client.get_direction()
    print(resp)
    assert resp.status == ocs.OK
    print(resp.session)
    assert resp.session['op_code'] == OpCode.SUCCEEDED.value


@pytest.mark.integtest
def test_hwp_rotation_set_direction(wait_for_crossbar, kikusui_emu, pid_emu, run_agent, client):
    responses = {'*W02400000': 'W02\r',
                 '*W02401388': 'W02\r'}

    pid_emu.define_responses(responses)
    resp = client.set_direction(direction='0')
    print(resp)
    assert resp.status == ocs.OK
    print(resp.session)
    assert resp.session['op_code'] == OpCode.SUCCEEDED.value

    resp = client.set_direction(direction='1')
    print(resp)
    assert resp.status == ocs.OK
    print(resp.session)
    assert resp.session['op_code'] == OpCode.SUCCEEDED.value


@pytest.mark.integtest
def test_hwp_rotation_set_pid(wait_for_crossbar, kikusui_emu, pid_emu, run_agent, client):
    responses = {'*W1700C8': 'W17\r',
                 '*W18003F': 'W18\r',
                 '*W190000': 'W19\r',
                 '*Z02': 'Z02\r'}

    pid_emu.define_responses(responses)
    resp = client.set_pid(p_param=0.2, i_param=63, d_param=0)
    print(resp)
    assert resp.status == ocs.OK
    print(resp.session)
    assert resp.session['op_code'] == OpCode.SUCCEEDED.value


@pytest.mark.integtest
def test_hwp_rotation_tune_stop(wait_for_crossbar, kikusui_emu, pid_emu, run_agent, client):
    responses = {'*W0C83': 'W0C\r',
                 '*W01400000': 'W01\r',
                 '*R01': 'R01400000\r',
                 '*Z02': 'Z02\r',
                 '*W1700C8': 'W17\r',
                 '*W180000': 'W18\r',
                 '*W190000': 'W19\r'}

    pid_emu.define_responses(responses)
    resp = client.tune_stop()
    print(resp)
    assert resp.status == ocs.OK
    print(resp.session)
    assert resp.session['op_code'] == OpCode.SUCCEEDED.value


@pytest.mark.integtest
def test_hwp_rotation_get_freq(wait_for_crossbar, kikusui_emu, pid_emu, run_agent, client):
    responses = {'*X01': 'X010.000\r'}
    pid_emu.define_responses(responses)

    resp = client.get_freq()
    print(resp)
    assert resp.status == ocs.OK
    print(resp.session)
    assert resp.session['op_code'] == OpCode.SUCCEEDED.value


@pytest.mark.integtest
def test_hwp_rotation_set_scale(wait_for_crossbar, kikusui_emu, pid_emu, run_agent, client):
    responses = {'*W14102710': 'W14\r',
                 '*W03302710': 'W03\r',
                 '*Z02': 'Z02\r'}
    pid_emu.define_responses(responses)

    resp = client.set_scale()
    print(resp)
    assert resp.status == ocs.OK
    print(resp.session)
    assert resp.session['op_code'] == OpCode.SUCCEEDED.value


@pytest.mark.integtest
def test_hwp_rotation_declare_freq(wait_for_crossbar, kikusui_emu, pid_emu, run_agent, client):
    resp = client.declare_freq(freq=0)
    print(resp)
    assert resp.status == ocs.OK
    print(resp.session)
    assert resp.session['op_code'] == OpCode.SUCCEEDED.value


@pytest.mark.integtest
def test_hwp_rotation_tune_freq(wait_for_crossbar, kikusui_emu, pid_emu, run_agent, client):
    responses = {'*W0C81': 'W0C\r',
                 '*W01400000': 'W01\r',
                 '*R01': 'R01400000\r',
                 '*Z02': 'Z02\r',
                 '*W1700C8': 'W17\r',
                 '*W18003F': 'W18\r',
                 '*W190000': 'W19\r'}
    pid_emu.define_responses(responses)

    resp = client.tune_freq()
    print(resp)
    assert resp.status == ocs.OK
    print(resp.session)
    assert resp.session['op_code'] == OpCode.SUCCEEDED.value


# @pytest.mark.integtest
# def test_ls425_start_acq(wait_for_crossbar, emulator, run_agent, client):
#     responses = {'*IDN?': 'LSCI,MODEL425,LSA425T,1.3',
#                  'RDGFIELD?': '+1.0E-01'}
#     emulator.define_responses(responses)
#
#     resp = client.acq.start(sampling_frequency=1.0)
#     assert resp.status == ocs.OK
#     assert resp.session['op_code'] == OpCode.STARTING.value
#
#     # We stopped the process with run_once=True, but that will leave us in the
#     # RUNNING state
#     resp = client.acq.status()
#     assert resp.session['op_code'] == OpCode.RUNNING.value
#
#     # Now we request a formal stop, which should put us in STOPPING
#     client.acq.stop()
#     # this is so we get through the acq loop and actually get a stop command in
#     # TODO: get sleep_time in the acq process to be small for testing
#     time.sleep(3)
#     resp = client.acq.status()
#     print(resp)
#     print(resp.session)
#     assert resp.session['op_code'] in [OpCode.STOPPING.value, OpCode.SUCCEEDED.value]
