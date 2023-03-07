import sdg
import os
import OutputOpenSdg_test

def test_open_sdg():
    # Use empty alterations functions just to execute that code.
    def alter_data(data, context):
        return data
    def alter_meta(meta, context):
        return meta
    def alter_indicator(indicator, context):
        return indicator
    def my_indicator_callback(indicator):
        assert isinstance(indicator, sdg.Indicator)

    config_path = os.path.join('tests', 'assets', 'open-sdg', 'config_data.yml')
    assert sdg.open_sdg_check(config=config_path, alter_data=alter_data, alter_meta=alter_meta, alter_indicator=alter_indicator)
    assert sdg.open_sdg_build(config=config_path, alter_data=alter_data, alter_meta=alter_meta, alter_indicator=alter_indicator, indicator_callback=my_indicator_callback)

    OutputOpenSdg_test.test_open_sdg_output_comb()
    OutputOpenSdg_test.test_open_sdg_output_data_csv()
    OutputOpenSdg_test.test_open_sdg_output_data_json()
    OutputOpenSdg_test.test_open_sdg_output_edges_csv()
    OutputOpenSdg_test.test_open_sdg_output_edges_json()
    OutputOpenSdg_test.test_open_sdg_output_headline_all()
    OutputOpenSdg_test.test_open_sdg_output_headline_csv()
    OutputOpenSdg_test.test_open_sdg_output_headline_json()
    OutputOpenSdg_test.test_open_sdg_output_meta_all()
    OutputOpenSdg_test.test_open_sdg_output_meta_json()
    OutputOpenSdg_test.test_open_sdg_output_meta_schema()
    OutputOpenSdg_test.test_open_sdg_output_stats_disaggregation()
    OutputOpenSdg_test.test_open_sdg_output_stats_reporting()
    OutputOpenSdg_test.test_open_sdg_output_translations()
    OutputOpenSdg_test.test_open_sdg_output_zip()
