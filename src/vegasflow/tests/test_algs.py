"""
    Checks that the different integation algorithms
    are able to run and don't produce a crazy result
"""

""" Test a run with a simple function to make sure
everything works """
import numpy as np
import tensorflow as tf
from vegasflow.configflow import DTYPE
from vegasflow.vflow import VegasFlow
from vegasflow.plain import PlainFlow

# Test setup
dim = 2
ncalls = np.int32(1e5)
n_iter = 4

@tf.function
def example_integrand(xarr, n_dim = None, weight=None):
    """ Example function that integrates to 1 """
    if n_dim is None:
        n_dim = xarr.shape[-1]
    a = tf.constant(0.1, dtype=DTYPE)
    n100 = tf.cast(100 * n_dim, dtype=DTYPE)
    pref = tf.pow(1.0 / a / np.sqrt(np.pi), n_dim)
    coef = tf.reduce_sum(tf.range(n100 + 1))
    coef += tf.reduce_sum(tf.square((xarr - 1.0 / 2.0) / a), axis=1)
    coef -= (n100 + 1) * n100 / 2.0
    return pref * tf.exp(-coef)

def instance_and_compile(Integrator):
    """ Wrapper for convenience """
    int_instance = Integrator(dim, ncalls)
    int_instance.compile(example_integrand)
    return int_instance

def check_is_one(result, sigmas = 3):
    """ Wrapper for convenience """
    res = result[0]
    err = result[1]*sigmas
    # Check that it passes by {sigmas} number of sigmas
    np.testing.assert_allclose(res, 1., atol=err)

def test_VegasFlow():
    vegas_instance = instance_and_compile(VegasFlow)
    _ = vegas_instance.run_integration(n_iter)
    vegas_instance.freeze_grid()
    result = vegas_instance.run_integration(n_iter)
    check_is_one(result)

def test_PlainFlow():
    plain_instance = instance_and_compile(PlainFlow)
    result = plain_instance.run_integration(n_iter)
    check_is_one(result)
