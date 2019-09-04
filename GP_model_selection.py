import matplotlib.pyplot as plt
import UtilsNetwork as Utils
from sklearn.gaussian_process import GaussianProcessRegressor
# from sklearn.gaussian_process.kernels import WhiteKernel
from sklearn.gaussian_process.kernels import RBF
# from sklearn.gaussian_process.kernels import RationalQuadratic
from sklearn.gaussian_process.kernels import Matern
from matplotlib import rc
import joblib
import os
import sys
import warnings
from termcolor import colored
from sklearn.model_selection import train_test_split
import numpy as np
os.system('color')
warnings.filterwarnings("ignore")


def fit_gaussian_process(X_train_, y_train_, kernel="rbf", nu_=2.5):
    bound = (1e-012, 1000000.0)
    rbf_kernel = RBF(length_scale=1, length_scale_bounds=bound)
    matern_kernel = Matern(length_scale=1.0, length_scale_bounds=bound, nu=nu_)  # remeber you change it
    # periodic_kernel = ExpSineSquared(length_scale=1.0, periodicity=1.0, length_scale_bounds=bound, periodicity_bounds=bound)
    # rq_kernel = RationalQuadratic(length_scale=1.0, alpha=1.0, length_scale_bounds=bound)
    # white_kernel = WhiteKernel(noise_level=1, noise_level_bounds=bound)
    if kernel == "rbf":
        gp_kernel = rbf_kernel
    else:
        gp_kernel = matern_kernel
    model = GaussianProcessRegressor(kernel=gp_kernel, n_restarts_optimizer=1500)

    model.fit(X_train_, y_train_)
    return model


if sys.platform == "win32":
    rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
    rc('text', usetex=True)

keyword = "airf"
variable_name = "lift"
samples = 100
level_single = 0
level_c = 0
level_f = 1
string_norm = "true"
scaler = "m"
point = "sobol"

scaler = scaler.replace("'","")
string_norm = string_norm.replace("'","")

print(keyword)
print(variable_name)
print(samples)
print(level_single)
print(level_c)
print(level_f)
print(string_norm)
print(scaler)

# ====================================================
if string_norm == "true" or string_norm == "'true'":
    norm = True
elif string_norm == "false" or string_norm == "'false'":
    norm = False
else:
    raise ValueError("Norm can be 'true' or 'false'")

# ====================================================
if keyword == "parab":
    n_input = 7
    case_folder = "Parabolic"
elif keyword == "parab_diff":
    n_input = 7
    case_folder = "Parabolic"
elif keyword == "shock":
    n_input = 6
    case_folder = "ShockTube"
elif keyword == "shock_diff":
    n_input = 6
    case_folder = "ShockTube"
elif keyword == "airf_diff":
    n_input = 6
    case_folder = "Airfoil"
elif keyword == "airf":
    n_input = 6
    case_folder = "Airfoil"
else:
    raise ValueError("Chose one option between parab and shock")

# ====================================================
if "diff" in keyword:
    X, y, _, _, min_val, max_val = Utils.get_data_diff(keyword, samples, variable_name, level_c, level_f, n_input,
                                                       model_path_folder=None, normalize=norm, scaler=scaler, point=point)
else:
    X, y, _, _, min_val, max_val = Utils.get_data(keyword, samples, variable_name, level_single, n_input,
                                                  model_path_folder=None, normalize=norm, scaler=scaler, point=point)


mean_error_reg, std_error_reg, model_reg = Utils.linear_regression(keyword, variable_name, X.shape[0], level_c, level_f, level_single, n_input, norm, scaler=scaler)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
y_test = y_test.reshape(-1,)
if norm:
    if scaler == "m" or scaler == "'m'":
        y_test = y_test * (max_val - min_val) + min_val
    elif scaler == "s" or scaler == "'s'":
        y_test = y_test * max_val + min_val

for nu in [0.5, 1.5, 2.5]:
    print("##########################################")
    print(nu)
    y_train = np.log(y_train)
    gpr = fit_gaussian_process(X_train, y_train, kernel="", nu_=nu)
    y_pred, y_std = gpr.predict(X_test, return_std=True)
    y_pred = y_pred.reshape(-1,)
    y_pred = np.exp(y_pred)

    if norm:
        if scaler == "m" or scaler == "'m'":
            y_pred = y_pred * (max_val - min_val) + min_val
        elif scaler == "s" or scaler == "'s'":
            y_pred = y_pred *max_val + min_val

    print(colored("\nFinal prediction error:", "green", attrs=['bold']))
    mean_error = Utils.compute_mean_prediction_error(y_test, y_pred, 2) * 100
    variance_error = Utils.compute_prediction_error_variance(y_test, y_pred, 2) * 100
    print(str(mean_error) + "%")
    print(str(variance_error) + "%")


print("##########################################")
gpr = fit_gaussian_process(X_train, y_train)

y_pred, y_std = gpr.predict(X_test, return_std=True)
y_pred = y_pred.reshape(-1,)


if norm:
    if scaler == "m" or scaler == "'m'":
        y_pred = y_pred * (max_val - min_val) + min_val
    elif scaler == "s" or scaler == "'s'":
        y_pred = y_pred *max_val + min_val

print(colored("\nFinal prediction error:", "green", attrs=['bold']))
mean_error = Utils.compute_mean_prediction_error(y_test, y_pred, 2) * 100
variance_error = Utils.compute_prediction_error_variance(y_test, y_pred, 2) * 100
print(str(mean_error) + "%")
print(str(variance_error) + "%")
