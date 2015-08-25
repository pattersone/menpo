import numpy as np
from nose.tools import assert_equals

import menpo.io as mio
from menpo.landmark import labeller, face_ibug_68_to_face_ibug_68


def test_double_type():
    image = mio.import_builtin_asset('breakingbad.jpg')
    patch_shape = (16, 16)
    patches = image.extract_patches(image.landmarks['PTS'].lms,
                                    patch_size=patch_shape)
    assert(patches[0].pixels.dtype == np.float64)


def test_float_type():
    image = mio.import_builtin_asset('breakingbad.jpg')
    image.pixels = image.pixels.astype(np.float32)
    patch_shape = (16, 16)
    patches = image.extract_patches(image.landmarks['PTS'].lms,
                                    patch_size=patch_shape)
    assert(patches[0].pixels.dtype == np.float32)


def test_uint8_type():
    image = mio.import_builtin_asset('breakingbad.jpg', normalise=False)
    patch_shape = (16, 16)
    patches = image.extract_patches(image.landmarks['PTS'].lms,
                                    patch_size=patch_shape)
    assert(patches[0].pixels.dtype == np.uint8)


def test_uint8_type_single_array():
    image = mio.import_builtin_asset('breakingbad.jpg', normalise=False)
    patch_shape = (16, 16)
    patches = image.extract_patches(image.landmarks['PTS'].lms,
                                    patch_size=patch_shape,
                                    as_single_array=True)
    assert(patches.dtype == np.uint8)


def test_squared_even_patches():
    image = mio.import_builtin_asset('breakingbad.jpg')
    patch_shape = (16, 16)
    patches = image.extract_patches(image.landmarks['PTS'].lms,
                                    patch_size=patch_shape)
    assert_equals(len(patches), 68)


def test_squared_odd_patches():
    image = mio.import_builtin_asset('breakingbad.jpg')
    patch_shape = (15, 15)
    patches = image.extract_patches(image.landmarks['PTS'].lms,
                                    patch_size=patch_shape)
    assert_equals(len(patches), 68)


def test_nonsquared_even_patches():
    image = mio.import_builtin_asset('breakingbad.jpg')
    patch_shape = (16, 18)
    patches = image.extract_patches(image.landmarks['PTS'].lms,
                                    patch_size=patch_shape)
    assert_equals(len(patches), 68)


def test_nonsquared_odd_patches():
    image = mio.import_builtin_asset('breakingbad.jpg')
    patch_shape = (15, 17)
    patches = image.extract_patches(image.landmarks['PTS'].lms,
                                    patch_size=patch_shape)
    assert_equals(len(patches), 68)


def test_nonsquared_even_odd_patches():
    image = mio.import_builtin_asset('breakingbad.jpg')
    patch_shape = (15, 16)
    patches = image.extract_patches(image.landmarks['PTS'].lms,
                                    patch_size=patch_shape)
    assert_equals(len(patches), 68)


def test_squared_even_patches_landmarks():
    image = mio.import_builtin_asset('breakingbad.jpg')
    patch_shape = (16, 16)
    patches = image.extract_patches_around_landmarks('PTS',
                                                     patch_size=patch_shape)
    assert_equals(len(patches), 68)


def test_squared_even_patches_landmarks_label():
    image = mio.import_builtin_asset('breakingbad.jpg')
    image = labeller(image, 'PTS', face_ibug_68_to_face_ibug_68)
    patch_shape = (16, 16)
    patches = image.extract_patches_around_landmarks('face_ibug_68',
                                                     label='nose',
                                                     patch_size=patch_shape)
    assert_equals(len(patches), 9)


def test_squared_even_patches_single_array():
    image = mio.import_builtin_asset('breakingbad.jpg')
    patch_shape = (16, 16)
    patches = image.extract_patches(image.landmarks['PTS'].lms,
                                    as_single_array=True,
                                    patch_size=patch_shape)
    assert_equals(patches.shape, ((68, 1, 3) + patch_shape))


def test_squared_even_patches_sample_offsets():
    image = mio.import_builtin_asset('breakingbad.jpg')
    sample_offsets = np.array([[0, 0], [1, 0]])
    patches = image.extract_patches(image.landmarks['PTS'].lms,
                                    sample_offsets=sample_offsets)
    assert_equals(len(patches), 136)
