"""Computes the realignment of a bipartite operator."""
import functools
import operator
import numpy as np
from toqito.perms.swap import swap
from toqito.super_operators.partial_transpose import partial_transpose


def realignment(input_mat: np.ndarray, dim=None) -> np.ndarray:
    r"""
    Compute the realignment of a bipartite operator [5]_.

    Gives the realignment of the matrix `input_mat`, where it is assumed that
    the number of rows and columns of `input_mat` are both perfect squares and
    both subsystems have equal dimension. The realignment is defined by mapping
    the operator :math:`|ij \rangle \langle kl |` to :math:`|ik \rangle \langle
    jl |` and extending linearly.

    If `input_mat` is non-square, different row and column dimensions can be
    specified by putting the row dimensions in the first row of `dim` and the
    column dimensions in the second row of `dim`.

    Examples
    ==========

    The standard realignmnet map

    Using `toqito`, we can generate the standard realignment map as follows.
    When viewed as a map on block matrices, the realignment map takes each block
    of the original matrix and makes its vectorization the rows of the
    realignment matrix. This is illustrated by the following small example:

    >>> from toqito.super_operators.realignment import realignment
    >>> import numpy as np
    >>> test_input_mat = np.array(
    >>>     [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
    >>> )
    >>> realignment(test_input_mat)
    [[ 1  2  5  6]
     [ 3  4  7  8]
     [ 9 10 13 14]
     [11 12 15 16]]

    References
    ==========
    .. [5] Lupo, Cosmo, Paolo Aniello, and Antonello Scardicchio.
        "Bipartite quantum systems: on the realignment criterion and beyond."
        Journal of Physics A: Mathematical and Theoretical
        41.41 (2008): 415301.
        https://arxiv.org/abs/0802.2019

    :param input_mat: The input matrix.
    :param dim: Default has all equal dimensions.
    :return: The realignment map matrix.
    """
    eps = np.finfo(float).eps
    dim_mat = input_mat.shape
    round_dim = np.round(np.sqrt(dim_mat))
    if dim is None:
        dim = np.transpose(np.array([round_dim]))
    if isinstance(dim, list):
        dim = np.array(dim)

    if isinstance(dim, int):
        dim = np.array([[dim], [dim_mat[0] / dim]])
        if np.abs(dim[1] - np.round(dim[1])) >= 2 * dim_mat[0] * eps:
            raise ValueError("InvalidDim:")
        dim[1] = np.round(dim[1])
        dim = np.array([[1], [4]])

    if min(dim.shape) == 1:
        dim = dim[:].T
        dim = functools.reduce(operator.iconcat, dim, [])
        dim = np.array([dim, dim])
        # dim = functools.reduce(operator.iconcat, dim, [])

    dim_x = np.array([[dim[0][1], dim[0][0]], [dim[1][0], dim[1][1]]])
    dim_y = np.array([[dim[1][0], dim[0][0]], [dim[0][1], dim[1][1]]])

    x_tmp = swap(input_mat, [1, 2], dim, True)
    y_tmp = partial_transpose(x_tmp, sys=1, dim=dim_x)
    return swap(y_tmp, [1, 2], dim_y, True)
