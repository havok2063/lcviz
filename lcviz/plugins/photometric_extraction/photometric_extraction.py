from astropy import units as u
from traitlets import Unicode, observe
from lightkurve import LightCurve

from jdaviz.core.registries import tray_registry
from jdaviz.configs.cubeviz.plugins import SpectralExtraction
from jdaviz.core.template_mixin import (PluginTemplateMixin,
                                        DatasetSelectMixin, AddResultsMixin,
                                        skip_if_no_updates_since_last_active,
                                        with_spinner, with_temp_disable)
from jdaviz.core.user_api import PluginUserApi


__all__ = ['PhotometricExtraction']


@tray_registry('photometric-extraction', label="Photometric Extraction")
class PhotometricExtraction(SpectralExtraction):
    """
    See the :ref:`Photometric Extraction Plugin Documentation <photometric-extraction>`
    for more details.

    Only the following attributes and methods are available through the
    :ref:`public plugin API <plugin-apis>`:

    * :meth:`~jdaviz.core.template_mixin.PluginTemplateMixin.show`
    * :meth:`~jdaviz.core.template_mixin.PluginTemplateMixin.open_in_tray`
    * :meth:`~jdaviz.core.template_mixin.PluginTemplateMixin.close_in_tray`
    * ``dataset`` (:class:`~jdaviz.core.template_mixin.DatasetSelect`):
      Dataset to extract.
    * ``add_results`` (:class:`~jdaviz.core.template_mixin.AddResults`)
    * :meth:`extract`
    """
    resulting_product_name = Unicode("light curve").tag(sync=True)
    do_auto_extraction = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.docs_link = f"https://lcviz.readthedocs.io/en/{self.vdocs}/plugins.html#photometric-extraction"
        self.docs_description = "Extract light curve from target pixel file cube."  # noqa


        def is_tpf(data):
            return len(data.shape) == 3
        self.dataset.filters = [is_tpf]
        self._set_relevant()  # move upstream?

    @property
    def user_api(self):
        expose = ['dataset', 'function', 'aperture',
                  'background', 
                  'add_results', 'extract',
                  'aperture_method']

        return PluginUserApi(self, expose=expose)

    @observe('dataset_items')
    def _set_relevant(self, *args):
        # NOTE: upstream will set disabled_msg to something similar, but mentioning
        if len(self.dataset_items) < 1:
            self.irrelevant_msg = 'Requires at least one TPF cube to be loaded'
        else:
            self.irrelevant_msg = ''

    @property
    def slice_display_unit_name(self):
        return 'time'

    @property
    def spatial_axes(self):
        return (1, 2)

    def _return_extracted(self, cube, wcs, collapsed_nddata):
        lc = LightCurve(time=cube.get_object(LightCurve).time, flux=collapsed_nddata.data)
        return lc

    def _preview_x_from_extracted(self, extracted):
        return extracted.time.value - self.dataset.selected_obj.meta.get('reference_time', 0.0 * u.d).value

    def _preview_y_from_extracted(self, extracted):
        return extracted.flux.value
