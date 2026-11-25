"""Pure-numpy DoE helpers (no Streamlit import, so it is easy to unit-test)."""
import itertools
import numpy as np
from scipy import stats

FACTORS = ["X1", "X2", "X3", "X4"]
LABELS = {"X1": "Time (h)", "X2": "ZnCl\u2082 (mol%)", "X3": "Concentration (mM)", "X4": "2a (equiv)"}
CENTRE = {"X1": 5.0, "X2": 12.5, "X3": 242.0, "X4": 1.5}
HALF = {"X1": 2.0, "X2": 7.5, "X3": 81.0, "X4": 0.5}          # actual = centre + coded*half
CODED = ["X1_c", "X2_c", "X3_c", "X4_c"]
TERMS = ["b0", "b1 (X1)", "b2 (X2)", "b3 (X3)", "b4 (X4)",
         "b12", "b13", "b14", "b23", "b24", "b34",
         "b11 (X1^2)", "b22 (X2^2)", "b33 (X3^2)", "b44 (X4^2)"]


def decode(coded, factor):
    return CENTRE[factor] + np.asarray(coded) * HALF[factor]


def encode(actual, factor):
    return (np.asarray(actual) - CENTRE[factor]) / HALF[factor]


def design_matrix(C):
    """Full quadratic model matrix (n x 15) from coded factors C (n x 4)."""
    C = np.atleast_2d(np.asarray(C, dtype=float))
    cols = [np.ones(len(C))] + [C[:, i] for i in range(4)]
    cols += [C[:, i] * C[:, j] for i in range(4) for j in range(i + 1, 4)]
    cols += [C[:, i] ** 2 for i in range(4)]
    return np.column_stack(cols)


def candidate_grid():
    return np.array(list(itertools.product([-1, 0, 1], repeat=4)), dtype=float)


def fit_ols(C, y):
    """OLS fit + leave-one-out diagnostics (PRESS via the hat matrix)."""
    X = design_matrix(C)
    y = np.asarray(y, dtype=float)
    n, p = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ y
    yhat = X @ b
    e = y - yhat
    h = np.einsum("ij,jk,ik->i", X, XtX_inv, X)
    denom = np.where(1 - h < 1e-9, np.nan, 1 - h)
    loo_e = e / denom
    ss_res, ss_tot = float(e @ e), float(((y - y.mean()) ** 2).sum())
    dof = n - p
    r2 = 1 - ss_res / ss_tot
    adj = 1 - (1 - r2) * (n - 1) / dof if dof > 0 else np.nan
    s2 = ss_res / dof if dof > 0 else np.nan
    se = np.sqrt(s2 * np.diag(XtX_inv)) if dof > 0 else np.full(p, np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        pv = 2 * stats.t.sf(np.abs(b / se), dof) if dof > 0 else np.full(p, np.nan)
    press = float(np.nansum(loo_e ** 2))
    return dict(coef=b, fitted=yhat, resid=e, leverage=h, loo_resid=loo_e, loo_pred=y - loo_e,
                r2=r2, adj_r2=adj, dof=dof, resid_sd=np.sqrt(s2) if dof > 0 else np.nan,
                se=se, p=pv, rmsecv=float(np.sqrt(np.nanmean(loo_e ** 2))),
                q2=1 - press / ss_tot, XtX_inv=XtX_inv,
                se_pure_error=lambda s: s * np.sqrt(np.diag(XtX_inv)))


def predict(b, C):
    return design_matrix(C) @ np.asarray(b)


def logdet_info(C):
    """log det of the normalised information matrix X'X/N (the D-criterion)."""
    X = design_matrix(C)
    sign, ld = np.linalg.slogdet(X.T @ X / len(X))
    return ld if sign > 0 else -np.inf


def surface(b, fx, fy, fixed_coded, n=41):
    """Predicted response over the (fx, fy) plane, other factors fixed (coded)."""
    g = np.linspace(-1, 1, n)
    GX, GY = np.meshgrid(g, g)
    C = np.zeros((GX.size, 4))
    for f in FACTORS:
        i = FACTORS.index(f)
        C[:, i] = fixed_coded.get(f, 0.0)
    C[:, FACTORS.index(fx)] = GX.ravel()
    C[:, FACTORS.index(fy)] = GY.ravel()
    return g, predict(b, C).reshape(GX.shape)
