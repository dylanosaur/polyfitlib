from numpy import zeros, sqrt, cos, exp, dot, logspace, log10
from math import pow


#from globals import init_globals
from Data import Data
from scipy.weave import inline
from scipy.weave.converters import blitz

from numpy import zeros

#LASER_LAM = 1064.3		# in nanometers
#ELECTRON_MASS = 510998.0	# in electron-volts / c^2



def cold2o_Spec(ps, temp, globals):
	# A function to calculate the low temperature expansion of the second order approximation to the
	# scattering integral (for scattered light of all polarization states).  The scipy.weave.inline
	# routine is used to incorporate C code that accelerates the function call.
	#
	# Parameters:
	# ps ---- A PolySegData object containing:
	#		ps.lam ------ the array of wavelength values
	#		ps.scatAng -- the scattering angle
	# temp -- The electron temperature in eV
	#
	# Returns:
	# dist -- Ndarray containing the values of the scattering spectrum
        LASER_LAM = 1064.3		# in nanometers
        ELECTRON_MASS = 510998.0	# in electron-volts / c^2
	lam0 = LASER_LAM
	theta = ps.scatAng
	alpha = ELECTRON_MASS / (2*temp)

	dist = zeros(len(ps.lam))
	lam = ps.lam.copy()

	# define the list of variables and the code to pass to weave.inline
	cvars = ['dist', 'lam', 'lam0', 'theta', 'alpha']

	code = """
	int i;
	double pie = 3.1415926535897931;
	double x, kc, eta, s_eta, arg, K2approx, beta_e;

	for(i = 0; i < Nlam[0]; i++)
		{
		x = lam0 / lam(i);
		kc = sqrt(1 + x*x - 2*x*cos(theta));
		eta = (x - 1) / kc;
		s_eta = sqrt(1 - eta*eta);

		arg = 2*alpha*(1 - 1 / s_eta);
		K2approx = sqrt(pie / alpha) * (1 + 15/(16*alpha) + 195/(512*alpha*alpha) );
		beta_e = (1 - cos(theta))*(1 - cos(theta)) * pow(s_eta, 3) / (2 * alpha);

		dist(i) = pow(x, 3) * (1 - beta_e) * exp(arg)/(lam0 * kc * K2approx);
		}
	"""

	hcode = """#include <math.h> """

	inline(code, cvars, support_code = hcode, type_converters = blitz)
	return dist

def selden_Spec(ps, temp):
	"""A function to calculate the Selden approximation to the scattering spectrum (neglecting the
	depolarization term).  This contains a factor of omega_i in the denominator, which Selden seems
	to have neglected due to a typo (it's correct in Zhuravlev 1979).  The scipy.weave.inline routine
	is used to incorporate C code that accelerates the function call.
	
	Parameters:
	ps ---- A PolySegData object containing:
			ps.lam ------ the array of wavelength values
			ps.scatAng -- the scattering angle
	temp -- The electron temperature in eV
	
	Returns:
	dist -- Ndarray containing the values of the scattering spectrum
	"""

	# define some constants
	LASER_LAM = 1064.3
	lam0 = LASER_LAM
	theta = ps.scatAng
	alpha = ELECTRON_MASS / (2*temp)

	dist = zeros(len(ps.lam))
	lam = ps.lam.copy()

	# define the list of variables and the code to pass to weave.inline
	cvars = ['dist', 'lam', 'lam0', 'theta', 'alpha']

	code = """
	int i;
	double pie = 3.1415926535897931;
	double x, kc, eta, arg;
	double K2approx = sqrt(pie / alpha) * (1 + 15/(16*alpha) + 195/(512*alpha*alpha) );

	for(i = 0; i < Nlam[0]; i++)
		{
		x = lam0 / lam(i);
		kc = sqrt(1 + x*x - 2*x*cos(theta));
		eta = (x - 1) / kc;

		arg = 2*alpha*(1 - 1 / sqrt(1 - eta*eta) );


		dist(i) = pow(x, 3) * exp(arg) / (lam0 * kc * K2approx);
		}
	"""

	hcode = """#include <math.h> """

	inline(code, cvars, support_code = hcode, type_converters = blitz)
	return dist

def selden_old(ps, temp):
	# Parameters:
	# ps ---- A PolySegData object containing:
	#		ps.lam ------ the array of wavelength values
	#		ps.scatAng -- the scattering angle
	# temp -- The electron temperature in eV
	#
	# Returns:
	# dist -- Ndarray containing the values of the scattering spectrum

	# define some constants
	LASER_LAM = 1064.3
	lam0 = LASER_LAM
	theta = ps.scatAng
	#alpha = ELECTRON_MASS / (2*temp)
	alpha = 0.5 * 8.19e-14 / (temp * 1.6e-19)

	dist = zeros(len(ps.lam))
	lam = ps.lam.copy()

	# define the list of variables and the code to pass to weave.inline
	cvars = ['dist', 'lam', 'lam0', 'theta', 'alpha']

	code = """
	int i = Nlam[0];
	double pie = 3.1415926535897931;
	double eps, tmpVar, AS, BS;
	double Calpha = sqrt(alpha / pie) * (1 - (15 / (16*alpha)) + (345 / (512 * pow(alpha, 2))) );

	while(i--)
		{
		eps = (lam(i) / lam0) - 1;
		tmpVar = 2 * (1 - cos(theta)) * (1 + eps);

		AS = pow(1 + eps, 3) * sqrt(tmpVar + pow(eps, 2));
		BS = sqrt(1 + pow(eps, 2) / tmpVar) - 1.0;

		dist(i) = lam(i) * Calpha * exp(-2 * alpha * BS) / AS;
		}
	"""

	hcode = """#include <math.h> """

	inline(code, cvars, support_code = hcode, type_converters = blitz)
	return dist

def calcModelProbability(ps, modelPhotons):
	"""Calculate the probability of getting the number of measured photons 
	given the expected photon distribution for a particular temperature and density.

	Parameters:
	ps -- The polySegData object containing:
			ps.scatPhotonsDC ---- the measured DC scattered photons
			ps.bgPhotons -------- the measured background photons
			ps.calib.APDfqeDC --- the DC FQE values for each APD module
	modelPhotons -- the expected number of photons on each channel for a given temperature/density

	Returns: The negative probability value. We return a negative value so 
	we can utilize minimization routines.
	"""

	scatPhotons = ps.scPhotons_Bayes
	bgPhotons = ps.bgPhotons_Bayes
	FQE = ps.fqe_Bayes
	probability = zeros(1)

	# define the list of variables and the code to pass to weave.inline
	cvars = ['modelPhotons','scatPhotons', 'bgPhotons', 'FQE', 'probability']

	code = """
	int i = NmodelPhotons[0];
	double sqrt_2pie = 2.506628274631;
	double sigma, tmpProd = 1.0, chi2 = 0.0;

	while(i--)
		{
		sigma = sqrt( (modelPhotons(i) + bgPhotons(i)) * FQE(i) );
		tmpProd *= sqrt_2pie * sigma;
		chi2 += pow( (scatPhotons(i) - modelPhotons(i)) / sigma , 2);
		}

	probability(0) = -(1.0 / tmpProd) * exp(-0.5 * chi2);

	"""

	hcode = """#include <math.h> """

	inline(code, cvars, support_code = hcode, type_converters = blitz)
	return probability[0]



# Grid search parameters - rough search
#Te_MIN = 10.0
#Te_MAX = 2500.0
#ne_MIN = 1000.0
#ne_MAX = 100000.0

def compareGrid(specFlag, globals):

    Te_MIN = globals.TE_MIN
    Te_MAX = globals.TE_MAX
    ne_MAX = globals.NE_MAX
    ne_MIN = globals.NE_MIN

    
    data = Data()
    data.loadData(1110328120)
    ps = data.getPolySegData(3,0)
    fitPolySeg(ps)
    print "Init density: ", ps.ne0, " Init temp: ", ps.Te0

    maxProb = 0
    ps.ne0 = -1
    ps.Te0 = -1
    gridPts = 10.0
    gridsearch = zeros((gridPts,gridPts))
    i = 0
    for Te in logspace(log10(Te_MIN), log10(Te_MAX), gridPts):
	    j = 0
	    for ne in logspace(log10(ne_MIN), log10(ne_MAX), gridPts):
		    Nphotons = specPhotons(ne, Te, ps, specFlag)
		    prob = - calcModelProbability(ps, globals, Nphotons)
		    gridsearch[i,j] = prob
		    if prob > maxProb:
		        maxProb = prob
		       	ps.ne0 = ne
		       	ps.Te0 = Te
			j += 1
	    i += 1
    return gridsearch, maxProb, ps

def specPhotons(ne, Te, ps, specFlag = "selden"):
	ang = ps.scatAng
	if specFlag == "selden":
		dist = selden_Spec(ps, Te)
	elif specFlag == "cold2o":
		dist = cold2o_Spec(ps, Te)
	elif specFlag == "old":
		dist = selden_old(ps, Te) / 1200000.0
        return ne * ps.calib.deltaLam * dot(ps.calib.trans, dist)
