"""Package module delivery files using an explicit allowlist."""
import hashlib
import json
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def validate_apk_layout(path: Path) -> None:
    """Fail packaging before Android can reject a static RRO at boot."""
    with zipfile.ZipFile(path) as archive:
        info = archive.getinfo('resources.arsc')
        if info.compress_type != zipfile.ZIP_STORED:
            raise ValueError(f'{path.name}: resources.arsc must be uncompressed')
        with path.open('rb') as stream:
            stream.seek(info.header_offset + 26)
            name_len, extra_len = struct.unpack('<HH', stream.read(4))
        data_offset = info.header_offset + 30 + name_len + extra_len
        if data_offset % 4:
            raise ValueError(f'{path.name}: resources.arsc is not 4-byte aligned')


prop = dict(line.split('=', 1) for line in (ROOT / 'module.prop').read_text(encoding='utf-8').splitlines() if '=' in line)
for spec_path in sorted((ROOT / 'compat').glob('[0-9]*.json')):
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    if 'overlays' not in spec or 'versionCode' not in spec:
        continue
    for name in spec['overlays']:
        artifact = ROOT / 'files' / f"{name}-{spec['versionCode']}.apk"
        if not artifact.is_file():
            raise FileNotFoundError(f'Missing versioned overlay: {artifact}')
destination = ROOT / f"WeChatMonet-CN-{prop['version']}.zip"
paths = [ROOT / name for name in (
    'module.prop', 'config.conf', 'update.json', 'README.md', 'CHANGELOG.md',
    'action.sh', 'boot-completed.sh', 'common.sh', 'customize.sh', 'service.sh',
    'adapt_wechat.py', 'wx_patch.py', 'build_module.py',
)]
if (ROOT / 'target-version.conf').is_file():
    paths.append(ROOT / 'target-version.conf')
paths += sorted((ROOT / 'files').glob('*.apk'))
for apk in paths:
    if apk.suffix == '.apk':
        validate_apk_layout(apk)
paths.append(ROOT / 'files' / 'aapt2')
paths += sorted((ROOT / 'compat').glob('*.json'))
paths += sorted((ROOT / 'compat').glob('*.md'))
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in paths:
        name = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        if path.suffix in ('.sh', '.py', '.md', '.json', '.prop', '.conf'):
            data = data.replace(b'\r\n', b'\n')
        info = zipfile.ZipInfo(name)
        info.create_system = 3
        info.external_attr = (0o100755 if path.suffix == '.sh' else 0o100644) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, data)
with zipfile.ZipFile(destination) as archive:
    if archive.testzip() is not None:
        raise RuntimeError('Module ZIP failed CRC verification')
print(destination)
print('SHA256:', hashlib.sha256(destination.read_bytes()).hexdigest())
