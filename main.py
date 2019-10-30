from pathlib import Path

import xmltodict

BASE = '/mnt/ssd-1/lineage-16.0'
DEVICE_PATHS = [
    'device/sony/nile-common/overlay',
    'device/sony/nile-common/overlay-lineage',
    'device/sony/discovery/overlay',
    'device/sony/discovery/overlay-lineage',
    'device/sony/pioneer/overlay',
    'device/sony/pioneer/overlay-lineage',
]


def parse(v):
    res = {}

    if 'resources' in v:
        for _, resource_values in v['resources'].items():
            if '#text' in resource_values:
                res[resource_values['@name']] = resource_values['#text']
            elif 'item' in resource_values:
                res[resource_values['@name']] = resource_values['item']
            elif '@name' in resource_values:
                res[resource_values['@name']] = None
            elif isinstance(resource_values, list):
                for item in resource_values:
                    if item is None:
                        pass
                    elif '#text' in item:
                        res[item['@name']] = item['#text']
                    elif 'item' in item:
                        res[item['@name']] = item['item']
                    elif '@name' in item:
                        res[item['@name']] = None

    return res


device_overlays = {}

for device_path in DEVICE_PATHS:
    if len(list(Path('{}/{}'.format(BASE, device_path)).rglob('*.xml'))) > 0:
        device_overlays[device_path] = {}

        for absolute_path in Path('{}/{}'.format(BASE, device_path)).rglob('*.xml'):
            relative_path = str(absolute_path)[len('{}/{}/'.format(BASE, device_path)):]
            device_overlays[device_path][relative_path] = xmltodict.parse(absolute_path.read_text())

system_resources = {}

for relative_path in set(sum([list(device_overlays[x].keys()) for x in device_overlays.keys()], [])):
    absolute_path = '{}/{}'.format(BASE, relative_path)

    try:
        with open(absolute_path) as f:
            system_resources[relative_path] = xmltodict.parse(f.read())
    except Exception as e:
        print(e)

system_resources_parsed = {}

for k, v in system_resources.items():
    system_resources_parsed[k] = parse(v)

for path, overlays in device_overlays.items():
    for k, v in overlays.items():
        print('{}/{}/{}'.format(BASE, path, k))

        for resource_key, resource_value in parse(v).items():
            if k not in system_resources_parsed:
                print(' ', '{}/{} does not exist'.format(BASE, k))
                break

            if resource_key not in system_resources_parsed[k]:
                print(' ', '{} is not in {}/{}'.format(resource_key, BASE, k))
            elif resource_value == system_resources_parsed[k][resource_key]:
                print(' ', '{} is same as in system resources'.format(resource_key))
