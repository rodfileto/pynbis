/*******************************************************************************
PyNBIS - Python bindings for NBIS (NIST Biometric Image Software)

This software wraps the NBIS library which is in the public domain.

License: 
This software and/or related materials was developed at the National Institute
of Standards and Technology (NIST) by employees of the Federal Government
in the course of their official duties. Pursuant to title 17 Section 105
of the United States Code, this software is not subject to copyright
protection and is in the public domain.

Disclaimer: 
This software and/or related materials are provided "AS-IS" without warranty
of any kind including NO WARRANTY OF PERFORMANCE, MERCHANTABILITY,
NO WARRANTY OF NON-INFRINGEMENT OF ANY 3RD PARTY INTELLECTUAL PROPERTY
or FITNESS FOR A PARTICULAR PURPOSE or for any purpose whatsoever.

*******************************************************************************/

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>
#include <string.h>
#include <stdlib.h>

/* NBIS Headers */
#include "bozorth.h"
#include "lfs.h"
#include "nfiq.h"

/*******************************************************************************
 * Define global variables needed by NBIS libraries
 ******************************************************************************/

/* Bozorth3 globals (normally defined in command-line tools) */
int m1_xyt = 0;
int max_minutiae = MAX_BOZORTH_MINUTIAE;
int min_computable_minutiae = MIN_COMPUTABLE_BOZORTH_MINUTIAE;
int verbose_main = 0;
int verbose_load = 0;
int verbose_bozorth = 0;
int verbose_threshold = 0;
FILE *errorfp = NULL;  /* Error output stream */

/*******************************************************************************
 * Helper Functions
 ******************************************************************************/

/* Convert Python bytes/array to image data */
static unsigned char* py_to_image_data(PyObject *image_obj, int *width, int *height, int *depth) {
    PyArrayObject *array = NULL;
    unsigned char *data = NULL;
    
    if (PyArray_Check(image_obj)) {
        array = (PyArrayObject*)PyArray_FROM_OTF(image_obj, NPY_UINT8, NPY_ARRAY_IN_ARRAY);
        if (!array) {
            PyErr_SetString(PyExc_ValueError, "Failed to convert image to uint8 array");
            return NULL;
        }
        
        int ndim = PyArray_NDIM(array);
        npy_intp *dims = PyArray_DIMS(array);
        
        if (ndim == 2) {
            *height = (int)dims[0];
            *width = (int)dims[1];
            *depth = 8;
        } else if (ndim == 3 && dims[2] == 1) {
            *height = (int)dims[0];
            *width = (int)dims[1];
            *depth = 8;
        } else {
            PyErr_SetString(PyExc_ValueError, "Image must be 2D grayscale");
            Py_DECREF(array);
            return NULL;
        }
        
        /* Copy data */
        size_t data_size = (*width) * (*height);
        data = (unsigned char*)malloc(data_size);
        if (!data) {
            PyErr_NoMemory();
            Py_DECREF(array);
            return NULL;
        }
        memcpy(data, PyArray_DATA(array), data_size);
        Py_DECREF(array);
    } else {
        PyErr_SetString(PyExc_TypeError, "Image must be a numpy array");
        return NULL;
    }
    
    return data;
}

/*******************************************************************************
 * Minutiae Extraction (MINDTCT)
 ******************************************************************************/

static PyObject* nbis_extract_minutiae(PyObject *self, PyObject *args, PyObject *kwargs) {
    static char *kwlist[] = {"image", "ppi", NULL};
    PyObject *image_obj = NULL;
    int ppi = DEFAULT_PPI;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|i", kwlist, &image_obj, &ppi)) {
        return NULL;
    }
    
    /* Convert image */
    int width, height, depth;
    unsigned char *image_data = py_to_image_data(image_obj, &width, &height, &depth);
    if (!image_data) {
        return NULL;
    }
    
    /* Run minutiae detection */
    MINUTIAE *minutiae = NULL;
    int *direction_map = NULL;
    int *low_contrast_map = NULL;
    int *low_flow_map = NULL;
    int *high_curve_map = NULL;
    int map_w, map_h;
    unsigned char *binarized = NULL;
    int bw, bh;
    
    int ret = lfs_detect_minutiae_V2(&minutiae,
                                      &direction_map, &low_contrast_map,
                                      &low_flow_map, &high_curve_map,
                                      &map_w, &map_h,
                                      &binarized, &bw, &bh,
                                      image_data, width, height,
                                      &lfsparms_V2);
    
    free(image_data);
    
    if (ret != 0) {
        PyErr_SetString(PyExc_RuntimeError, "Minutiae detection failed");
        return NULL;
    }
    
    /* Build result dictionary */
    PyObject *result = PyDict_New();
    PyObject *minutiae_list = PyList_New(0);
    
    for (int i = 0; i < minutiae->num; i++) {
        MINUTIA *m = minutiae->list[i];
        PyObject *min_dict = Py_BuildValue("{s:i,s:i,s:i,s:i,s:d,s:s}",
            "x", m->x,
            "y", m->y,
            "direction", m->direction,
            "type", m->type,
            "quality", m->reliability,
            "type_str", m->type == RIDGE_ENDING ? "ending" : "bifurcation");
        PyList_Append(minutiae_list, min_dict);
        Py_DECREF(min_dict);
    }
    
    PyDict_SetItemString(result, "minutiae", minutiae_list);
    PyDict_SetItemString(result, "count", PyLong_FromLong(minutiae->num));
    
    /* Create binarized image array */
    npy_intp dims[2] = {bh, bw};
    PyObject *bin_array = PyArray_SimpleNew(2, dims, NPY_UINT8);
    memcpy(PyArray_DATA((PyArrayObject*)bin_array), binarized, bw * bh);
    PyDict_SetItemString(result, "binarized", bin_array);
    
    /* Cleanup */
    Py_DECREF(minutiae_list);
    Py_DECREF(bin_array);
    free_minutiae(minutiae);
    free(direction_map);
    free(low_contrast_map);
    free(low_flow_map);
    free(high_curve_map);
    free(binarized);
    
    return result;
}

/*******************************************************************************
 * XYT Format Conversion
 ******************************************************************************/

static struct xyt_struct* minutiae_to_xyt(MINUTIAE *minutiae, int max_count) {
    struct xyt_struct *xyt = (struct xyt_struct*)malloc(sizeof(struct xyt_struct));
    if (!xyt) return NULL;
    
    int count = minutiae->num < max_count ? minutiae->num : max_count;
    xyt->nrows = count;
    
    for (int i = 0; i < count; i++) {
        MINUTIA *m = minutiae->list[i];
        xyt->xcol[i] = m->x;
        xyt->ycol[i] = m->y;
        xyt->thetacol[i] = m->direction;
    }
    
    return xyt;
}

/*******************************************************************************
 * Fingerprint Matching (Bozorth3)
 ******************************************************************************/

static PyObject* nbis_match_fingerprints(PyObject *self, PyObject *args) {
    PyObject *probe_obj = NULL;
    PyObject *gallery_obj = NULL;
    
    if (!PyArg_ParseTuple(args, "OO", &probe_obj, &gallery_obj)) {
        return NULL;
    }
    
    /* Extract minutiae from both images */
    int width1, height1, depth1, width2, height2, depth2;
    unsigned char *probe_data = py_to_image_data(probe_obj, &width1, &height1, &depth1);
    unsigned char *gallery_data = py_to_image_data(gallery_obj, &width2, &height2, &depth2);
    
    if (!probe_data || !gallery_data) {
        free(probe_data);
        free(gallery_data);
        return NULL;
    }
    
    /* Extract minutiae from probe */
    MINUTIAE *probe_min = NULL;
    int *dmap1, *lcm1, *lfm1, *hcm1, mw1, mh1;
    unsigned char *bin1;
    int bw1, bh1;
    
    int ret1 = lfs_detect_minutiae_V2(&probe_min, &dmap1, &lcm1, &lfm1, &hcm1,
                                       &mw1, &mh1, &bin1, &bw1, &bh1,
                                       probe_data, width1, height1, &lfsparms_V2);
    free(probe_data);
    
    if (ret1 != 0) {
        free(gallery_data);
        PyErr_SetString(PyExc_RuntimeError, "Probe minutiae detection failed");
        return NULL;
    }
    
    /* Extract minutiae from gallery */
    MINUTIAE *gallery_min = NULL;
    int *dmap2, *lcm2, *lfm2, *hcm2, mw2, mh2;
    unsigned char *bin2;
    int bw2, bh2;
    
    int ret2 = lfs_detect_minutiae_V2(&gallery_min, &dmap2, &lcm2, &lfm2, &hcm2,
                                       &mw2, &mh2, &bin2, &bw2, &bh2,
                                       gallery_data, width2, height2, &lfsparms_V2);
    free(gallery_data);
    
    if (ret2 != 0) {
        free_minutiae(probe_min);
        free(dmap1); free(lcm1); free(lfm1); free(hcm1); free(bin1);
        PyErr_SetString(PyExc_RuntimeError, "Gallery minutiae detection failed");
        return NULL;
    }
    
    /* Convert to XYT format */
    struct xyt_struct *probe_xyt = minutiae_to_xyt(probe_min, MAX_BOZORTH_MINUTIAE);
    struct xyt_struct *gallery_xyt = minutiae_to_xyt(gallery_min, MAX_BOZORTH_MINUTIAE);
    
    if (!probe_xyt || !gallery_xyt) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to convert minutiae to XYT format");
        free(probe_xyt);
        free(gallery_xyt);
        free_minutiae(probe_min);
        free_minutiae(gallery_min);
        free(dmap1); free(lcm1); free(lfm1); free(hcm1); free(bin1);
        free(dmap2); free(lcm2); free(lfm2); free(hcm2); free(bin2);
        return NULL;
    }
    
    /* Perform matching */
    int score = bz_match_score(DEFAULT_BOZORTH_MINUTIAE, probe_xyt, gallery_xyt);
    
    /* Cleanup */
    free(probe_xyt);
    free(gallery_xyt);
    free_minutiae(probe_min);
    free_minutiae(gallery_min);
    free(dmap1); free(lcm1); free(lfm1); free(hcm1); free(bin1);
    free(dmap2); free(lcm2); free(lfm2); free(hcm2); free(bin2);
    
    return PyLong_FromLong(score);
}

/*******************************************************************************
 * Quality Assessment (NFIQ)
 ******************************************************************************/

static PyObject* nbis_compute_nfiq(PyObject *self, PyObject *args, PyObject *kwargs) {
    static char *kwlist[] = {"image", "ppi", NULL};
    PyObject *image_obj = NULL;
    int ppi = DEFAULT_PPI;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|i", kwlist, &image_obj, &ppi)) {
        return NULL;
    }
    
    /* Convert image */
    int width, height, depth;
    unsigned char *image_data = py_to_image_data(image_obj, &width, &height, &depth);
    if (!image_data) {
        return NULL;
    }
    
    /* Compute NFIQ */
    int nfiq_value;
    float conf_value;
    int optflag = 0;
    
    int ret = comp_nfiq(&nfiq_value, &conf_value, image_data, width, height,
                        depth, ppi, &optflag);
    
    free(image_data);
    
    /* ret: 0=success; >0 are algorithm conditions (e.g., EMPTY_IMG, TOO_FEW_MINUTIAE); <0 indicates system error */
    if (ret < 0) {
        PyErr_SetString(PyExc_RuntimeError, "NFIQ computation failed");
        return NULL;
    }
    
    return Py_BuildValue("{s:i,s:f,s:i}",
                         "quality", nfiq_value,
                         "confidence", conf_value,
                         "return_code", ret);
}

/*******************************************************************************
 * XYT-based Matching (for pre-extracted minutiae)
 ******************************************************************************/

static PyObject* nbis_match_xyt(PyObject *self, PyObject *args) {
    PyObject *probe_list = NULL;
    PyObject *gallery_list = NULL;
    
    if (!PyArg_ParseTuple(args, "OO", &probe_list, &gallery_list)) {
        return NULL;
    }
    
    if (!PyList_Check(probe_list) || !PyList_Check(gallery_list)) {
        PyErr_SetString(PyExc_TypeError, "Both arguments must be lists of minutiae");
        return NULL;
    }
    
    /* Convert Python lists to XYT structures */
    struct xyt_struct probe_xyt, gallery_xyt;
    
    Py_ssize_t probe_count = PyList_Size(probe_list);
    Py_ssize_t gallery_count = PyList_Size(gallery_list);
    
    if (probe_count > MAX_BOZORTH_MINUTIAE) probe_count = MAX_BOZORTH_MINUTIAE;
    if (gallery_count > MAX_BOZORTH_MINUTIAE) gallery_count = MAX_BOZORTH_MINUTIAE;
    
    probe_xyt.nrows = (int)probe_count;
    gallery_xyt.nrows = (int)gallery_count;
    
    /* Parse probe minutiae */
    for (Py_ssize_t i = 0; i < probe_count; i++) {
        PyObject *item = PyList_GetItem(probe_list, i);
        if (!PyDict_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "Minutiae must be dictionaries");
            return NULL;
        }
        
        PyObject *x_obj = PyDict_GetItemString(item, "x");
        PyObject *y_obj = PyDict_GetItemString(item, "y");
        PyObject *t_obj = PyDict_GetItemString(item, "direction");
        
        if (!x_obj || !y_obj || !t_obj) {
            PyErr_SetString(PyExc_ValueError, "Minutiae must have x, y, and direction");
            return NULL;
        }
        
        probe_xyt.xcol[i] = (int)PyLong_AsLong(x_obj);
        probe_xyt.ycol[i] = (int)PyLong_AsLong(y_obj);
        probe_xyt.thetacol[i] = (int)PyLong_AsLong(t_obj);
    }
    
    /* Parse gallery minutiae */
    for (Py_ssize_t i = 0; i < gallery_count; i++) {
        PyObject *item = PyList_GetItem(gallery_list, i);
        if (!PyDict_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "Minutiae must be dictionaries");
            return NULL;
        }
        
        PyObject *x_obj = PyDict_GetItemString(item, "x");
        PyObject *y_obj = PyDict_GetItemString(item, "y");
        PyObject *t_obj = PyDict_GetItemString(item, "direction");
        
        if (!x_obj || !y_obj || !t_obj) {
            PyErr_SetString(PyExc_ValueError, "Minutiae must have x, y, and direction");
            return NULL;
        }
        
        gallery_xyt.xcol[i] = (int)PyLong_AsLong(x_obj);
        gallery_xyt.ycol[i] = (int)PyLong_AsLong(y_obj);
        gallery_xyt.thetacol[i] = (int)PyLong_AsLong(t_obj);
    }
    
    /* Perform matching */
    int score = bz_match_score(DEFAULT_BOZORTH_MINUTIAE, &probe_xyt, &gallery_xyt);
    
    return PyLong_FromLong(score);
}

/*******************************************************************************
 * Module Definition
 ******************************************************************************/

static PyMethodDef NBISMethods[] = {
    {"extract_minutiae", (PyCFunction)nbis_extract_minutiae, METH_VARARGS | METH_KEYWORDS,
     "Extract minutiae from a fingerprint image.\n\n"
     "Args:\n"
     "    image: numpy array (grayscale, uint8)\n"
     "    ppi: pixels per inch (default: 500)\n\n"
     "Returns:\n"
     "    dict with keys: 'minutiae' (list), 'count' (int), 'binarized' (array)"},
    
    {"match_fingerprints", nbis_match_fingerprints, METH_VARARGS,
     "Match two fingerprint images (1:1 comparison).\n\n"
     "Args:\n"
     "    probe: numpy array (grayscale, uint8)\n"
     "    gallery: numpy array (grayscale, uint8)\n\n"
     "Returns:\n"
     "    int: match score (higher = better match)"},
    
    {"compute_nfiq", (PyCFunction)nbis_compute_nfiq, METH_VARARGS | METH_KEYWORDS,
     "Compute NFIQ quality score for a fingerprint image.\n\n"
     "Args:\n"
     "    image: numpy array (grayscale, uint8)\n"
     "    ppi: pixels per inch (default: 500)\n\n"
     "Returns:\n"
     "    dict with keys: 'quality' (1-5, 1=best), 'confidence' (float), 'return_code' (int)"},
    
    {"match_xyt", nbis_match_xyt, METH_VARARGS,
     "Match two sets of pre-extracted minutiae.\n\n"
     "Args:\n"
     "    probe: list of minutiae dicts with keys: x, y, direction\n"
     "    gallery: list of minutiae dicts with keys: x, y, direction\n\n"
     "Returns:\n"
     "    int: match score (higher = better match)"},
    
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef nbismodule = {
    PyModuleDef_HEAD_INIT,
    "_nbis_ext",
    "NBIS (NIST Biometric Image Software) Python Extension",
    -1,
    NBISMethods
};

PyMODINIT_FUNC PyInit__nbis_ext(void) {
    import_array();
    /* Ensure Bozorth uses a valid error stream */
    if (errorfp == NULL) {
        errorfp = stderr;
    }
    return PyModule_Create(&nbismodule);
}
