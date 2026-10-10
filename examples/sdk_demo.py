"""Offline SDK integration: synthetic firmware, frame and passive-report decoding."""
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from k2up.demo import DemoTransport, demo_firmware
from k2up.protocol import Protocol, build_frame, parse_frame
from k2up.updater import Updater
from k2up.telemetry import decode_report
from k2up.emark import sample_bank, validate_bank


def main():
    firmware = demo_firmware()
    assert firmware.summary()['version'] == '5.8'
    frame = build_frame(11, struct.pack('<IH', 0x08003800, 16), tick=0)
    assert parse_frame(frame).payload.hex() == '003800081000'
    identity = Updater(Protocol(DemoTransport())).probe()
    assert identity.confirmed_k2
    updater = Updater(Protocol(DemoTransport()))
    updater.flash(firmware)  # Memory simulation, never a real transport.
    assert updater.stage == 'complete'
    payload = bytearray(52)
    struct.pack_into('<2f', payload, 4, 0.25, 3.0)
    struct.pack_into('<2I', payload, 12, 10, 20)
    struct.pack_into('<6f', payload, 20, 0.5, 0.6, 25.0, 0.0, 5.0, -1.0)
    sample = decode_report(build_frame(0x1A, bytes(payload), tick=0), 1.5)
    assert (sample.voltage, sample.current, sample.power, sample.signed_power) == (5, -1, 5, -5)
    assert validate_bank(sample_bank())[5] == 1
    print('Offline SDK: firmware, frames, identity, simulated upgrade, telemetry and E-Mark passed.')


if __name__ == '__main__':
    main()
