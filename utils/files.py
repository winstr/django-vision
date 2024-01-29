import os
import fnmatch
from typing import Generator


def get_files(name_pattern: str,
              root_dir: str,
              recursive: bool=True
    ) -> Generator:

    for parent_dir, _, files in os.walk(root_dir):
        if files:
            for file in fnmatch.filter(files, name_pattern):
                yield os.path.join(parent_dir, file)
        if not recursive:
            break