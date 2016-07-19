#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>


const double PI =  3.1415926535897931; // Pi.
const double LAM0 = 1064.3; // The laser's wavelength.
const double MEC2 = 8.19e-14; //Mass-energy of electron.
const double SQRT2PI = 2.506628274631; // sqrt(2 * pi)



// Forward declaration.
static PyObject *selden(PyObject *self, PyObject *args);
static PyObject *calcNeTeProbability(PyObject *self, PyObject *args);



/*
 * All module functions must appear here.
 */
static PyMethodDef ts_cMethods[] = {
    { "selden", selden, METH_VARARGS,
    "Selden Equation. \n\
    \n\
    Parameters:\n\
    lam     -- A array of wavelengths to compute.\n\
    ne      -- The electron number density. \n\
    Te      -- The electron temperature. \n\
    theta   -- The scattering angle.\n\
    \n\
    Returns the a photon distribution with one element for each lambda value\n\
    given in lam."
    },

    { "calcNeTeProbability", calcNeTeProbability, METH_VARARGS,
    "Calculate the probability of getting the number of measured photons \n\
    given the temperature and density.\n\
    \n\
    Parameters:\n\
    \n\
    N_model     -- Array of model photons per APD.\n\
    scatPhotons -- Array of measured scattered photons per APD.\n\
    bgPhotons   -- Array of measured background photons per APD.\n\
    APDfqe      -- Array of fqe values per APD. \n\
    \n\
    Returns: The negative probability value. We return a negative value so \n\
    we can utilize minimization routines."
    },
    {NULL, NULL, 0, NULL} /* Sentinel */
};



/*
 * All module functions must appear here.
 */
PyMODINIT_FUNC
initts_c(void)
{
        (void) Py_InitModule("ts_c", ts_cMethods);
        import_array();
}



/*
 * Convenience function to get a double array from a PyArrayObject.
 */
double *py_vec_double_array(PyArrayObject *arrayin)  {
    return (double *) arrayin->data;
}



/*
 * Convenience function to get a float array from a PyArrayObject.
 */
float *py_vec_float_array(PyArrayObject *arrayin) {
  return (float *) arrayin->data;
}



/*
 * Selden's equation.
 */
static PyObject *
selden(PyObject *self, PyObject *args)
{
    double ne, Te, theta;
    PyArrayObject *pLam, *pDist;

    if (!PyArg_ParseTuple(args, "Oddd", &pLam, &ne, &Te, &theta))
        return NULL;

    // Convert temperature to joules.
    Te = Te * 1.6e-19;

    // Get the length of lambda.
    int i = pLam->dimensions[0];

    // Create return value.
    int dims[1];
    dims[0] = i;

    pDist = (PyArrayObject *) PyArray_SimpleNew(1, dims, PyArray_DOUBLE);
    double *dist = py_vec_double_array(pDist);

    // Construct a C array from the lambda array.
    double *lam = py_vec_double_array(pLam);

    // Create needed variables.
    double eps, tmpVar, AS, BS;
    double alpha = 0.5 * MEC2 / Te;
    double calpha = sqrt(alpha/PI) * (1.0 - (15.0 / (16.0 * alpha)) +
                                      (345.0 / (512.0 * pow(alpha, 2))));

    while(i--) {
      eps = (lam[i] / LAM0) - 1.0;
      tmpVar = 2 * (1 - cos(theta)) * (1 + eps);
      AS = pow(1 + eps, 3) * sqrt(tmpVar + pow(eps, 2));
      BS = sqrt(1 + (pow(eps, 2) / tmpVar)) - 1.0;
      dist[i] = ne * calpha * lam[i] * exp(-2 * alpha * BS) / AS;
    }

    return PyArray_Return(pDist);
}


/*
 * Calculate the probability of getting the given temperature and density given
 * the measured number of photons.
 */
static PyObject *
calcNeTeProbability(PyObject *self, PyObject *args)
{
    PyArrayObject *pN_model, *pScatPhotons, *pBgPhotons, *pAPDfqe;

    if(!PyArg_ParseTuple(args, "OOOO", &pN_model, &pScatPhotons, &pBgPhotons,
                         &pAPDfqe))
        return NULL;

    // Create C-objects to work with
    double *N_model = py_vec_double_array(pN_model);
    double *scatPhotons = py_vec_double_array(pScatPhotons);
    double *bgPhotons = py_vec_double_array(pBgPhotons);
    double *APDfqe = py_vec_double_array(pAPDfqe);

    int i = pN_model->dimensions[0];
    double sigma;
    double tmpProd = 1.0;
    double chi2 = 0.0;

    while(i--) {
        sigma = sqrt((N_model[i] + bgPhotons[i]) * APDfqe[i]);
        tmpProd *= SQRT2PI * sigma;
        chi2 += pow((scatPhotons[i] - N_model[i]) / sigma, 2);
    }

    double ret = -(1.0 / tmpProd) * exp(-0.5 * chi2);

    return Py_BuildValue("d", ret);
}
