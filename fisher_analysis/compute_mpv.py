from ..theory.cosmology import Cosmology
from ..theory.sigma_interpolation import SigmaInterpolator
from ..theory.halo_bias import HaloBias
from ..theory.halo_bias_new import HaloBias as HaloBiasNew
from ..theory.mass_functions import JenkinsMassFunction, PressSchechterMassFunction
from ..theory.correlation_functions import CorrelationFunctions

from ..axion_camb_wrappers.growth_interpolation import GrowthInterpolation
from ..axion_camb_wrappers.power_interpolation import LinearPowerInterpolation

from ..auxiliary.integration_helper import IntegrationHelper
from ..auxiliary.survey_helper import SurveyType


def compute_mean_pairwise_velocity(r_vals, rMin, cosmo, lin_power, growth, survey, window="gaussian", old_bias=False, jenkins_mass=False, integrationHelper=None, kMin=1.0e-4, kMax=1.0e2, do_unbiased=False, get_correlation_functions=False):
    """

    Parameters
    ----------
    survey : SurveyType
    growth : GrowthInterpolation
    lin_power : LinearPowerInterpolation
    cosmo : Cosmology
    integrationHelper : IntegrationHelper
    """

    if integrationHelper is None:
        integrationHelper = IntegrationHelper(1024)

    sigmaInt = SigmaInterpolator(cosmo, lin_power, growth, survey.mMin, survey.mMax, survey.center_z, integrationHelper, Nr=1024, window_function=window)
    sigmaInt.compute(kMin, kMax, do_dr=True, do_dloga=False)

    if jenkins_mass:
        mass_function = JenkinsMassFunction(cosmo, sigmaInt)
    else:
        mass_function = PressSchechterMassFunction(cosmo, sigmaInt)

    if old_bias:
        halo_bias = HaloBias(cosmo, sigmaInt, mass_function, survey.mMin, survey.mMax, kMin, kMax, survey.center_z, integrationHelper, Nk=1024, window_function=window)
    else:
        halo_bias = HaloBiasNew(cosmo, sigmaInt, mass_function, survey.mMin, survey.mMax, kMin, kMax, survey.center_z, integrationHelper, Nk=1024, window_function=window)

    halo_bias.compute()

    corr = CorrelationFunctions(cosmo, lin_power, growth, halo_bias, kMin, halo_bias._kMax if window=="sharp_k" and old_bias and kMax>halo_bias._kMax else kMax, survey.center_z, rMin, r_vals, integrationHelper)

    if do_unbiased:
        xi_unbiased, xi, dbarxi_dloga_unbiased, dbarxi_dloga =  corr.compute(unbiased=True, old_bias=old_bias)
        v = r_vals * 100 * dbarxi_dloga / (3 * (1 + xi))
        v_dm = r_vals * 100 * dbarxi_dloga_unbiased / (3 * (1 + xi_unbiased))
        if get_correlation_functions:
            return v, v_dm, xi_unbiased, xi, dbarxi_dloga_unbiased, dbarxi_dloga
        else:
            return v, v_dm
    else:
        xi, dbarxi_dloga = corr.compute(unbiased=False, old_bias=old_bias)
        v = r_vals * 100 * dbarxi_dloga / (3 * (1 + xi))
        if get_correlation_functions:
            return v, xi, dbarxi_dloga
        else:
            return v
