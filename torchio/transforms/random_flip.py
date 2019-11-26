import torch
import numpy as np


class RandomFlip:
    def __init__(self, axes, flip_probability=0.5):
        self.axes = axes
        assert flip_probability > 0
        assert flip_probability <= 1
        self.flip_probability = flip_probability

    @staticmethod
    def get_params(axes, probability):
        axes_hot = [False, False, False]
        for axis in axes:
            n = torch.rand(1)
            flip_this = bool(probability > n)
            axes_hot[axis] = flip_this
        return axes_hot

    def __call__(self, sample):
        """
        https://github.com/facebookresearch/InferSent/issues/99#issuecomment-446175325
        """
        axes_to_flip = self.get_params(self.axes, self.flip_probability)
        sample['random_flip'] = axes_to_flip
        for key in 'image', 'label', 'sampler':
            if key not in sample: continue
            array = sample[key]
            for axis, flip_this in enumerate(axes_to_flip):
                if not flip_this: continue
                array = np.flip(array, axis=axis).copy()
                sample[key] = array
        return sample
