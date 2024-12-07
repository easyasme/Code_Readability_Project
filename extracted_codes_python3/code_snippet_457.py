import nrrd
import sys
import warnings
from numpy import (
    int,
    round,
    linspace,
    newaxis,
    shape,
    array,
    uint32,
    uint8,
    max,
    sqrt,
    abs,
    mean,
    dtype,
    int32,
    add,
    divide,
    subtract,
    sum,
    square,
    multiply,
    asarray,
    squeeze,
    float128,
    average,
    ones,
    fmin,
)


def zsampleslice(data):
    """Returns four sample Z slices through a 3d image array."""
    data = array(data, ndmin=3)
    l = shape(data)[2]
    a = data[:, :, 0]
    s = int(l / 3)
    b = data[:, :, s]
    c = data[:, :, -s]
    d = data[:, :, l - 1]
    return array([a, b, c, d])


def ysampleslice(data):
    """Returns four sample Z slices through a 3d image array."""
    data = array(data, ndmin=3)
    l = shape(data)[1]
    a = data[:, 0, :]
    s = int(l / 4)
    b = data[:, s, :]
    c = data[:, -s, :]
    d = data[:, l - 1, :]
    return array([a, b, c, d])


def xsampleslice(data):
    """Returns four sample Z slices through a 3d image array."""
    data = array(data, ndmin=3)
    l = shape(data)[0]
    a = data[0, :, :]
    s = int(l / 4)
    b = data[s, :, :]
    c = data[-s, :, :]
    d = data[l - 1, :, :]
    return array([a, b, c, d])


def RMSdiff(data1, data2):
    """Returns the RMS difference between two images."""
    return sqrt(mean(abs(data1 - (data2 + 0.0)) ** 2.0))


def OverlapCoeff(data1, data2):
    """Returns the Overlap Coefficent between two images."""
    nd1 = squeeze(asarray(data1, dtype=float128))
    nd2 = squeeze(asarray(data2, dtype=float128))
    r = sum(multiply(nd1, nd2)) / sqrt(multiply(sum(square(nd1)), sum(square(nd2))))
    print(r)
    return r


def minOverlapCoeff(data1, data2):
    """Returns the min Overlap Coefficent between image slices."""
    r = []
    print(shape(data1))
    for i in range(0, min(shape(data1))):
        nd1 = squeeze(asarray(data1[i], dtype=float128))
        if sum(nd1) < 1:
            nd1[0, 0] = 1.0
        print(shape(nd1))
        print(sum(nd1))
        nd2 = squeeze(asarray(data2[i], dtype=float128))
        if sum(nd2) < 1:
            nd2[0, 0] = 1.0
        print(shape(nd2))
        print(sum(nd2))
        if (sum(nd1) + sum(nd2)) > 0:
            r.append(sum(multiply(nd1, nd2)) / sqrt(multiply(sum(square(nd1)), sum(square(nd2)))))
        else:
            print('Note: both equal only as blank')
            r.append(1.0)
        print(r)
    return fmin(r)


def avgOverlapCoeff(data1, data2):
    """Returns the min Overlap Coefficent between image slices."""
    r = []
    weights = ones(min(shape(data1)), dtype=float)
    weights[0] = 0.1
    weights[-1] = 0.1
    for i in range(0, min(shape(data1))):
        nd1 = squeeze(asarray(data1[i], dtype=float128))
        if sum(nd1) < 1:
            nd1[0, 0] = 1.0
        nd2 = squeeze(asarray(data2[i], dtype=float128))
        if sum(nd2) < 1:
            nd2[0, 0] = 1.0
        if (sum(nd1) + sum(nd2)) > 0:
            r.append(sum(multiply(nd1, nd2)) / sqrt(multiply(sum(square(nd1)), sum(square(nd2)))))
        else:
            print('Note: both equal only as blank')
            r.append(1.0)
    print(r)
    print(weights)
    print(average(r, weights=weights))
    return average(r, weights=weights)


def symTest(function, data):
    """Applies the given function to the diagonal slices output from xslice. Can be used to assess the symmetry of a 3D image using a comparison function such as OverlapCoeff."""
    if data.ndim < 3:
        warnings.warn("must be used with data output from xslice", SyntaxWarning)
        return False
    else:
        return function(data[0], data[1])
