from __future__ import absolute_import, division, print_function

import shutil
import os
from astropy.io import fits
from .. import updatewcs
from ..wcsutil import headerlet, wcsdiff
from ..wcsutil import HSTWCS
import numpy as np
from numpy.testing import utils
import pytest

from . import data
data_path = os.path.split(os.path.abspath(data.__file__))[0]


def get_filepath(filename, directory=data_path):
    return os.path.join(directory, filename)


class TestCreateHeaderlet(object):

    def setup_class(self):
        acs_orig_file = get_filepath('j94f05bgq_flt.fits')
        simple_orig_file = get_filepath('simple.fits')
        current_dir = os.path.abspath(os.path.curdir)
        simple_file = get_filepath('simple.fits', current_dir)
        acs_file = get_filepath('j94f05bgq_flt.fits', current_dir)
        comp_file = get_filepath('comp.fits', current_dir)
        self.headerlet_name = get_filepath('acs_hlet.fits', current_dir)

        try:
            os.remove(acs_file)
            os.remove('comp.fits')
            os.remove(simple_file)
        except OSError:
            pass
        idctab = get_filepath('postsm4_idc.fits')
        npol_file = get_filepath('qbu16424j_npl.fits')
        d2imfile = get_filepath('new_wfc_d2i.fits ')

        shutil.copyfile(acs_orig_file, acs_file)
        shutil.copyfile(simple_orig_file, simple_file)
        fits.setval(acs_file, ext=0, keyword="IDCTAB", value=idctab)
        fits.setval(acs_file, ext=0, keyword="NPOLFILE", value=npol_file)
        fits.setval(acs_file, ext=0, keyword="D2IMFILE", value=d2imfile)

        updatewcs.updatewcs(acs_file)

        shutil.copyfile(acs_file, comp_file)
        self.comp_file = comp_file
        self.simple_file = simple_file

    def testAllExt(self):
        """
        Test create_headerlet stepping through all
        extensions in the science file
        """
        hlet = headerlet.create_headerlet(self.comp_file, hdrname='hdr1')
        hlet.writeto(self.headerlet_name, clobber=True)
        assert(wcsdiff.is_wcs_identical(self.comp_file, self.headerlet_name,
                                        [1, 4], [("SIPWCS", 1), ("SIPWCS", 2)],
                                        verbose=True)[0])

    def testSciExtList(self):
        """
        Test create_headerlet using a list of (EXTNAME, EXTNUM)
        extensions in the science file
        """
        hlet = headerlet.create_headerlet(self.comp_file,
                                          sciext=[('SCI', 1), ('SCI', 2)],
                                          hdrname='hdr1')
        hlet.writeto(self.headerlet_name, clobber=True)
        assert(wcsdiff.is_wcs_identical(self.comp_file, self.headerlet_name,
                                        [1, 4], [("SIPWCS", 1), ("SIPWCS", 2)],
                                        verbose=True)[0])

    def testSciExtNumList(self):
        """
        Test create_headerlet using a list of EXTNUM
        extensions in the science file
        """
        hlet = headerlet.create_headerlet(self.comp_file,
                                          sciext=[1, 4],
                                          hdrname='hdr1')
        hlet.writeto(self.headerlet_name, clobber=True)
        assert(wcsdiff.is_wcs_identical(self.comp_file, self.headerlet_name,
                                        [1, 4], [("SIPWCS", 1), ("SIPWCS", 2)],
                                        verbose=True)[0])

    def testHletFromSimpleFITS(self):
        """
        Test create_headerlet using a FITS HDUList extension
        number in the science file
        """
        hlet = headerlet.create_headerlet(self.simple_file,
                                          sciext=0,
                                          hdrname='hdr1')
        hlet.writeto(self.headerlet_name, clobber=True)
        assert(wcsdiff.is_wcs_identical(self.simple_file, self.headerlet_name,
                                        [0], [1], verbose=True)[0])

    def test_no_HDRNAME_no_WCSNAME(self):
        """
        Test create_headerlet stepping through all
        extensions in the science file
        """
        newf = get_filepath('ncomp.fits', os.path.abspath(os.path.curdir))
        shutil.copyfile(self.comp_file, newf)
        #fits.delval(newf, 'HDRNAME', ext=1)
        fits.delval(newf, 'WCSNAME', ext=1)
        with pytest.raises(KeyError):
            hlet = headerlet.create_headerlet(newf)

    def test1SciExt(self):
        """
        Create a headerlet from only 1 SCI ext
        """
        hlet = headerlet.create_headerlet(self.comp_file,
                                          sciext=4,
                                          hdrname='hdr1')
        hlet.writeto(self.headerlet_name, clobber=True)
        assert(wcsdiff.is_wcs_identical(self.comp_file, self.headerlet_name,
                                        [4], [1], verbose=True)[0])


class TestApplyHeaderlet:

    def setup_class(self):
        acs_orig_file = get_filepath('j94f05bgq_flt.fits')
        simple_orig_file = get_filepath('simple.fits')
        current_dir = os.path.abspath(os.path.curdir)
        simple_file = get_filepath('simple.fits', current_dir)
        acs_file = get_filepath('j94f05bgq_flt.fits', current_dir)
        comp_file = get_filepath('comp.fits', current_dir)
        self.headerlet_name = get_filepath('acs_hlet.fits', current_dir)

        try:
            os.remove(acs_file)
            os.remove('comp.fits')
            os.remove(simple_file)
        except OSError:
            pass
        idctab = get_filepath('postsm4_idc.fits')
        npol_file = get_filepath('qbu16424j_npl.fits')
        d2imfile = get_filepath('new_wfc_d2i.fits ')

        shutil.copyfile(acs_orig_file, acs_file)
        shutil.copyfile(simple_orig_file, simple_file)
        fits.setval(acs_file, ext=0, keyword="IDCTAB", value=idctab)
        fits.setval(acs_file, ext=0, keyword="NPOLFILE", value=npol_file)
        fits.setval(acs_file, ext=0, keyword="D2IMFILE", value=d2imfile)

        updatewcs.updatewcs(acs_file)

        shutil.copyfile(acs_file, comp_file)
        self.comp_file = comp_file

    '''
    def setUp(self):
        try:
            os.remove('j94f05bgq_flt.fits')
            os.remove('comp.fits')
        except OSError:
            pass
        shutil.copyfile('orig/j94f05bgq_flt.fits', './j94f05bgq_flt.fits')
        updatewcs.updatewcs('j94f05bgq_flt.fits')
        shutil.copyfile('j94f05bgq_flt.fits', './comp.fits')
    '''
    """
    Does not raise an error currently, should it?
    @raises(TypeError)
    def testWrongDestim(self):
        hlet = headerlet.create_headerlet('comp.fits', sciext=4,
                                          hdrname='hdr1', destim='WRONG')
        hlet.apply_as_primary('comp.fits')
    """


    def testWrongSIPModel(self):
        hlet = headerlet.create_headerlet(self.comp_file, hdrname='test1',
                                          sipname='WRONG')
        with pytest.raises(ValueError):
            hlet.apply_as_primary(self.comp_file)

    def testWrongNPOLModel(self):
        hlet = headerlet.create_headerlet(self.comp_file, hdrname='test1',
                                          npolfile='WRONG')
        with pytest.raises(ValueError):
            hlet.apply_as_primary(self.comp_file)

    def testWrongD2IMModel(self):
        hlet = headerlet.create_headerlet(self.comp_file, hdrname='test1',
                                          d2imfile='WRONG')
        with pytest.raises(ValueError):
            hlet.apply_as_primary(self.comp_file)

    def test_apply_as_primary_method(self):
        hlet = headerlet.create_headerlet(self.comp_file, hdrname='test2')
        hlet['SIPWCS', 1].header['CRPIX1'] = 1
        hlet['SIPWCS', 1].header['CRPIX2'] = 1
        hlet['SIPWCS', 2].header['CRPIX1'] = 2
        hlet['SIPWCS', 2].header['CRPIX2'] = 2
        hlet.apply_as_primary(self.comp_file)
        hlet.writeto(self.headerlet_name, clobber=True)
        assert(wcsdiff.is_wcs_identical(self.comp_file, self.headerlet_name,
                                        [('SCI', 1), ('SCI', 2)],
                                        [("SIPWCS", 1), ("SIPWCS", 2)],
                                        verbose=True)[0])
        # repeated hlet should not change sci file
        try:
            headerlet.apply_headerlet_as_primary(self.comp_file, 'hdr1_hlet.fits')
        except:
            pass
        assert(wcsdiff.is_wcs_identical(self.comp_file, self.headerlet_name,
                                        [('SCI', 1), ('SCI', 2)],
                                        [("SIPWCS", 1), ("SIPWCS", 2)],
                                        verbose=True)[0])

    def test_apply_as_alternate_method(self):
        hlet = headerlet.create_headerlet(self.comp_file, hdrname='test1')
        hlet.apply_as_alternate(self.comp_file, wcskey='K', wcsname='KK')
        hlet.writeto(self.headerlet_name, clobber=True)
        assert(wcsdiff.is_wcs_identical(self.comp_file, self.headerlet_name,
                                        [('SCI', 1), ('SCI', 2)],
                                        [("SIPWCS", 1), ("SIPWCS", 2)],
                                        scikey='K', verbose=True)[0])
        headerlet.apply_headerlet_as_alternate(self.comp_file,
                                               self.headerlet_name, wcskey='P')
        assert(wcsdiff.is_wcs_identical(self.comp_file, self.headerlet_name,
                                        [('SCI', 1), ('SCI', 2)],
                                        [("SIPWCS", 1), ("SIPWCS", 2)],
                                        scikey='P', verbose=True)[0])


class TestLegacyFiles:

    def setup_class(self):
        acs_orig_file = get_filepath('j94f05bgq_flt.fits')
        current_dir = os.path.abspath(os.path.curdir)
        self.acs_file = get_filepath('j94f05bgq_flt.fits', current_dir)
        self.legacy_file = get_filepath('jlegacy.fits', current_dir)

        try:
            os.remove(self.acs_file)
            os.remove(self.legacy_file)
        except OSError:
            pass
        idctab = get_filepath('postsm4_idc.fits')
        npol_file = get_filepath('qbu16424j_npl.fits')
        d2imfile = get_filepath('new_wfc_d2i.fits ')

        shutil.copyfile(acs_orig_file, self.acs_file)
        shutil.copyfile(acs_orig_file, self.legacy_file)

        fits.setval(self.acs_file, ext=0, keyword="IDCTAB", value=idctab)
        fits.setval(self.acs_file, ext=0, keyword="NPOLFILE", value=npol_file)
        fits.setval(self.acs_file, ext=0, keyword="D2IMFILE", value=d2imfile)
        updatewcs.updatewcs(self.acs_file)

    '''
    def setUp(self):
        try:
            os.remove('j94f05bgq_flt.fits')
            os.remove('jlegacy.fits')
        except OSError:
            pass
        shutil.copyfile('orig/j94f05bgq_flt.fits', './j94f05bgq_flt.fits')
        shutil.copyfile('j94f05bgq_flt.fits', './jlegacy.fits')
        updatewcs.updatewcs('j94f05bgq_flt.fits')
    '''

    def test_update_legacy_file(self):
        hlet = headerlet.create_headerlet(self.acs_file)
        hlet.apply_as_primary(self.legacy_file, archive=False, attach=False)
        assert(wcsdiff.is_wcs_identical(self.acs_file, self.legacy_file,
                                        [('SCI', 1), ('SCI', 2)],
                                        [("SCI", 1), ("SCI", 2)],
                                        verbose=True)[0])
