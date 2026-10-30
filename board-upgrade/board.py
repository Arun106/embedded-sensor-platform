"""Simulation only: updates a JSON fixture; never communicates with hardware."""
import argparse
import json
from pathlib import Path


def plan(config, state):
    if config.get('simulation') is not True or state.get('simulation') is not True:
        raise ValueError('Simulation markers required; real hardware is unsupported')
    if state['board_revision'] != config['board_revision']:
        raise ValueError('Unsupported board revision')
    if state['bootloader'] != config['required_bootloader']:
        raise ValueError('Unsupported bootloader')
    if state['firmware'] not in config['upgrade_paths']:
        raise ValueError('Unknown starting firmware; stop for review')
    steps = config['upgrade_paths'][state['firmware']]
    if (steps and steps[-1] != config['target']) or (not steps and state['firmware'] != config['target']):
        raise ValueError('Upgrade path does not reach target')
    for index, version in enumerate(steps):
        if config['upgrade_paths'].get(version) != steps[index + 1:]:
            raise ValueError('Inconsistent intermediate upgrade path')
    return steps


def flash(config, state, version):
    steps = plan(config, state)
    if not steps or version != steps[0]:
        raise ValueError('Requested update skips the approved next step')
    result = dict(state)
    result['history'] = state.get('history', []) + [version]
    result['firmware'] = version
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['read', 'plan', 'flash'])
    parser.add_argument('--state', default='/work/board.json')
    parser.add_argument('--config', default='/work/config/release.json')
    parser.add_argument('--version')
    args = parser.parse_args()
    state_path = Path(args.state)
    state = json.loads(state_path.read_text())
    config = json.loads(Path(args.config).read_text())
    steps = plan(config, state)
    if args.action == 'flash':
        state = flash(config, state, args.version)
        temporary = state_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(state, indent=2) + '\n')
        temporary.replace(state_path)
    print(json.dumps(steps if args.action == 'plan' else state))


if __name__ == '__main__':
    main()
