import pprint
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Sequence,
    Union
)
from pathlib import Path
import h5py
from ..torchio import DATA, TYPE, INTENSITY, DVF, TypePath
from .image import Image
from .subject import Subject

class HDFSubject(dict):
    """Class to store information about the images corresponding to a subject.

    Args:
        *args: If provided, a dictionary of items.
        **kwargs: Items that will be added to the subject sample.

    Example:

        >>> import torchio
        >>> from torchio import Image, HDFSubject
        >>> # One way:
        >>> subject = HDFSubject(
        ...     path='/path/to/file.hdf'
        ...     keys=['t1', 't2', 'mask']
        ...     labels=[torchio.INTENSITY, torchio.INTENSITY, torchio.LABEL]
        ...     age=45,
        ...     name='John Doe',
        ...     hospital='Hospital Juan Negrín',
        ... )
        >>> # If you want to create the mapping before, or have spaces in the keys:
        >>> subject_dict = {
        ...     'path': '/path/to/file.hdf',
        ...     'keys': ['t1', 't2', 'mask'],
        ...     'labels': [torchio.INTENSITY, torchio.INTENSITY, torchio.LABEL],
        ...     'age': 45,
        ...     'name': 'John Doe',
        ...     'hospital': 'Hospital Juan Negrín',
        ... }

    """

    def __init__(self, *args, ** kwargs: Dict[str, Any]):
        if args:
            if len(args) == 1 and isinstance(args[0], dict):
                kwargs.update(args[0])
            else:
                message = (
                    'Only one dictionary as positional argument is allowed')
                raise ValueError(message)
        super().__init__(**kwargs)
        # self.path = self._parse_path(self.path)
        # self.type = type_
        # self.is_sample = False  # set to True by ImagesDataset
        self._verify_object()

    def _verify_object(self):
        if not(all(elem in self.keys() for elem in ['path', 'keys', 'labels'])):
            raise ValueError('HDFSubject needs a path, keys for the HDF file, and torchio labels')

        self.path = self._parse_path(self.get('path'))

        if len(self.get('keys')) != len(self.get('labels')):
            raise ValueError('Every image needs a label')

        if len(self.get('keys')) != len(self.get('hdfpath')):
            raise ValueError('Every image needs a path')

    def __repr__(self):
        string = (
            f'{self.__class__.__name__}'
            f'(Keys: {tuple(self.keys())})'
        )
        return string

    def _parse_path(self, path: TypePath) -> Path:
        try:
            path = Path(path).expanduser()
        except TypeError:
            message = f'Conversion to path not possible for variable: {path}'
            raise TypeError(message)
        if not (path.is_file() or path.is_dir()):  # might be a dir with DICOM
            raise FileNotFoundError(f'File not found: {path}')
        return path

    def to_subject(self):
        dic = {}
        with h5py.File(self.path, 'r') as hdf_file:
            keys = self.get('keys')
            labels = self.get('labels')
            hdf_path = self.get('hdfpath')

            for i, key in enumerate(keys):
                dic[key] = Image(hdf_file[hdf_path[i]].value[()].T, labels[i])

        return Subject(dic)
