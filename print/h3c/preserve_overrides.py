"""Keep intentional CLI process/material settings when a single-material 3MF opens in Studio."""
from pathlib import Path
import json
import zipfile

PROCESS_KEYS = (
    'layer_height', 'initial_layer_print_height', 'wall_loops',
    'top_shell_layers', 'bottom_shell_layers', 'top_shell_thickness', 'bottom_shell_thickness',
    'sparse_infill_density', 'sparse_infill_pattern', 'enable_support',
    'brim_type', 'brim_width', 'brim_object_gap', 'initial_layer_speed',
    'initial_layer_infill_speed', 'outer_wall_speed', 'top_surface_speed',
)
MATERIAL_KEYS = (
    'nozzle_temperature', 'nozzle_temperature_initial_layer',
    'textured_plate_temp', 'textured_plate_temp_initial_layer',
    'filament_max_volumetric_speed', 'additional_cooling_fan_speed',
    'optional_cooling_fan_speed',
)


def preserve(path):
    path = Path(path)
    key = 'Metadata/project_settings.config'
    with zipfile.ZipFile(path) as src:
        entries = [(i, src.read(i)) for i in src.infolist()]
    settings = json.loads(next(data for info, data in entries if info.filename == key))
    assert len(settings['filament_settings_id']) == 1, 'Single-material jobs only'
    flags = settings.get('different_settings_to_system', ['', '', ''])
    assert len(flags) == 3
    for index, keys in enumerate((PROCESS_KEYS, MATERIAL_KEYS)):
        existing = set(filter(None, flags[index].split(';')))
        flags[index] = ';'.join(sorted(existing | {k for k in keys if k in settings}))
    settings['different_settings_to_system'] = flags
    temp = path.with_suffix('.overrides.tmp')
    with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_DEFLATED) as dst:
        for info, data in entries:
            dst.writestr(info, json.dumps(settings).encode() if info.filename == key else data)
    temp.replace(path)


if __name__ == '__main__':
    import sys
    preserve(sys.argv[1])
