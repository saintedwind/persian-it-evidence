"""Explicit download of pinned public model files. No query/API credentials sent."""
import hashlib
from pathlib import Path
from urllib.request import build_opener, ProxyHandler
from semantic import MODEL, REVISION, FILES, ROOT


def prepare():
    directory = ROOT / '.runtime/multilingual'
    directory.mkdir(parents=True, exist_ok=True)
    opener = build_opener(ProxyHandler({}))
    for name, digest in FILES.items():
        target = directory / name
        if target.is_file():
            with target.open('rb') as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() == digest:
                    continue
        part = target.with_suffix('.part')
        count, sha = 0, hashlib.sha256()
        try:
            with opener.open(f'https://huggingface.co/{MODEL}/resolve/{REVISION}/{name}', timeout=60) as response, part.open('wb') as output:
                while block := response.read(1024 * 1024):
                    count += len(block)
                    if count > 260_000_000:
                        raise ValueError('Model download exceeded size limit')
                    sha.update(block)
                    output.write(block)
            if sha.hexdigest() != digest:
                raise ValueError('Downloaded file failed integrity check')
            part.replace(target)
            print(name, count, 'bytes; SHA-256 verified', flush=True)
        finally:
            part.unlink(missing_ok=True)


if __name__ == '__main__':
    prepare()
