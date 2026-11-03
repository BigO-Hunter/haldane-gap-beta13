"""Exact Gaussian-coordinate Horner errors and four-rotation moment intervals
at inverse temperature 13 (MultiAgency port of verify_quarter_traces.py).

Differences from upstream (49/4):
- reads independent_results/beta13_quarter_twist_totals.json (twist=3,
  beta='13', engine-emitted guards) and independent_results/
  beta13_boundary_twists.json (twists 0,1 at all lengths);
- enclosure series argument x = 13*n*(3/2-a0); the upstream guard x<15 is
  relaxed to x<25. Soundness: the upper bound (s+term) dominates s+R for the
  exp-series tail R exactly when (x/101)/(1-x/102) <= 1, i.e. x <= 50.75;
  x<25 keeps a >2x margin. At beta=13, n=12: x = 15.368 < 25.
- cyclic source: upstream verify_extended_cyclic at 49/4 is NOT valid at
  beta=13; the CYCLIC_SOURCE below must be switched per the beta-dependence
  map before this module's output is used in any certificate. Until then,
  moments() raises (fails closed).
"""
from fractions import Fraction as Q
from math import factorial, isqrt
from pathlib import Path
import json

from thermal_error_bounds import errors as real_errors
from verify_quarter_traces import gaussian_errors  # beta-free
from verify_octahedral_sectors import certificate as group_certificate

ROOT = Path(__file__).resolve().parent
BETA = Q(13)
A0 = Q(700741, 500000)  # energy constant; beta-independent (upstream)


def enclosure(total, n, E):
    """Exact exp-series enclosure of the Gaussian-integer trace at beta=13."""
    r = isqrt(total); assert r*r <= total < (r+1)**2 and r > E
    x = BETA*n*(Q(3, 2)-A0); term = s = Q(1)
    for j in range(1, 101):
        term *= x/j; s += term
    # Tail domination (see module docstring): valid for x <= 50.75; guard at 25.
    assert 0 < x < 25 and x/(101-x) < 1, f'beta=13 series argument out of sound range: x={float(x)}'
    return s*(r-E)**2/2**110, (s+term)*(r+1+E)**2/2**110


def _coefficients():
    c = [Q(104)**j/factorial(j) for j in range(281)]
    den = sum(c)
    coeff = [int(2**55*x/den) for x in c]
    while coeff[-1] == 0:
        coeff.pop()
    return coeff


COEFF = _coefficients()
LAST_NONZERO = len(COEFF)-1


def _engine_guard(rec, n):
    assert int(rec['n']) == n and int(rec['multiplicity_sum']) == 3**n
    assert int(rec['maximum_coordinate_row_l1']) <= 80


def enclosures():
    """Twist=3 exact enclosures at beta=13, n=4..12."""
    if not __debug__:
        raise RuntimeError('Assertions must be enabled.')
    d = json.loads((ROOT/'independent_results/beta13_quarter_twist_totals.json').read_text())
    assert d['beta'] == '13' and d['success'] and d['series_base'] == 104
    # Coefficient-integrity anchors: the n=4 packed-reference matches in the
    # crosschecks ran reference.probs against exactly these coefficients.
    assert any(c.get('packed_reference_exact_match') for c in d['crosschecks'])
    assert 2**55*3**98 < 2**280
    out = []
    for n in range(4, 13):
        rec = d['totals'][str(n)]
        _engine_guard(rec, n)
        assert int(rec['twist']) == 3
        total = int(rec['total'])
        E, emax = gaussian_errors(n)
        assert 80*(2*2**55+2*emax) < 2**63
        assert (2**55+emax)**2*4*n < 2**127
        assert 3**n*(2**55+emax)**2 < 2**256
        lo, hi = enclosure(total, n, E)
        out.append({'n': n, 'lower': str(lo), 'upper': str(hi),
                    'frobenius_error_Q_units': E, 'maximum_column_error_Q_units': emax})
    return out


CYCLIC_SOURCE_RESOLVED = True  # cyclic == engine twist 2; beta13_boundary_twists.json carries it


def cyclic_enclosures():
    """Rational enclosures for the extended cyclic (twist=2) table at beta=13.

    Port of verify_extended_cyclic.enclosures(); reads our beta13 engine rows
    instead of the 49/4 wrapper format, keeps every guard (contraction,
    Eisenstein overflow bounds, series tail domination with the sound
    x<25 relaxation documented in the module docstring).
    """
    from thermal_error_bounds import errors
    assert certificate_beta13_ok()
    d = json.loads((ROOT/'independent_results/beta13_boundary_twists.json').read_text())
    assert d['beta'] == '13' and d['success'] and d['series_base'] == 104
    result = []
    for n in range(4, 13):
        rec = d['totals']['2'][str(n)]
        _engine_guard(rec, n)
        assert int(rec['twist']) == 2
        assert 1-Q(5*n, 32) >= -1
        E, max_error, kappa = errors(n)
        assert 80*(2*2**55+2*max_error) < 2**63
        assert (2**55+max_error)**2*4*n < 2**127
        assert 3**n*(2**55+max_error)**2 < 2**256
        lo, hi = enclosure(int(rec['total']), n, E)
        assert 0 < lo < hi
        result.append({'n': n, 'lower': str(lo), 'upper': str(hi),
                       'frobenius_error_Q_units': E, 'maximum_column_error_Q_units': max_error,
                       'contraction_modulus_upper': str(kappa)})
    return result


def certificate_beta13_ok():
    """Upstream local-energy certificate gate (beta-independent per recon)."""
    from verify_local_energy import certificate
    return certificate()['success']


def moments():
    """Sector moment tables from the four boundary rotations at beta=13."""
    assert group_certificate()['success']
    if not CYCLIC_SOURCE_RESOLVED:
        raise RuntimeError('FAIL-CLOSED: the cyclic-trace source at beta=13 is not '
                           'yet wired (upstream verify_extended_cyclic is 49/4 data).')
    d = json.loads((ROOT/'independent_results/beta13_boundary_twists.json').read_text())
    assert d['beta'] == '13' and d['success']
    quarter = {r['n']: (Q(r['lower']), Q(r['upper'])) for r in enclosures()}
    c = {r['n']: (Q(r['lower']), Q(r['upper'])) for r in cyclic_enclosures()}
    tw01 = {}
    for tw in ('0', '1'):
        for n, rec in d['totals'][tw].items():
            _engine_guard(rec, int(n))
            assert int(rec['twist']) == int(tw)
            E, _ = gaussian_errors(int(n))
            tw01[(int(n), int(tw))] = enclosure(int(rec['total']), int(n), E)
    coeff = {'A': (1, 9, 8, 6), 'B': (1, -3, 8, -6), 'E': (2, 6, -8, 0), 'V': (3, -9, 0, 6)}
    out = {}
    for n in range(4, 13):
        zz = [tw01[(n, 0)], tw01[(n, 1)], c[n], quarter[n]]
        out[n] = {}
        for s, p in coeff.items():
            out[n][s+'lo'] = sum(a*zz[k][int(a < 0)] for k, a in enumerate(p))/24
            out[n][s+'hi'] = sum(a*zz[k][int(a >= 0)] for k, a in enumerate(p))/24
            assert out[n][s+'lo'] < out[n][s+'hi']
    return out


if __name__ == '__main__':
    result = {'quarter_twist': enclosures(),
              'sector_moments': {n: {k: str(x) for k, x in row.items()} for n, row in moments().items()},
              'success': True}
    print('PASS: beta=13 all four rotations enclosed exactly; sector moments built.')
    (ROOT/'independent_results/beta13_quarter_enclosures.json').write_text(json.dumps(result, indent=2)+'\n')
