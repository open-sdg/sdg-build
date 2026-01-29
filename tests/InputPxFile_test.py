import sdg
import os
import inputs_common

def test_px_input():

    data_file = os.path.join('tests', 'assets', 'data', 'px', 'SDG010201.px')
    indicator_id_map = {
        data_file: ['1.2.1'],
    }
    meta_map = {
        'CONTACT': 'CONTACT',
        'LAST-UPDATED': 'META_LAST_UPDATE',
        'SOURCE': 'DATA_SOURCE',
    }
    data_input = sdg.inputs.InputPxFile(
        indicator_id_map=indicator_id_map,
        meta_map=meta_map
    )
    indicator_options = sdg.IndicatorOptions()
    indicator_options.add_non_disaggregation_columns('Series')
    indicator_options.add_non_disaggregation_columns('Units')
    data_input.execute(indicator_options=indicator_options)

    translation_input = sdg.translations.TranslationInputPx(
        indicator_id_map=indicator_id_map,
        indicator_options=indicator_options,
        meta_map=meta_map,
    )
    translation_helper = sdg.translations.TranslationHelper([translation_input])

    indicator = data_input.indicators['1-2-1']
    indicator.translate('en', translation_helper)
    indicator.translate('fo', translation_helper)

    correct_data_english = """
        Year,Series,sex,age,Value
        2009,Proportion of population living below the national poverty line,Total (sex),Total (age),3.8
        2010,Proportion of population living below the national poverty line,Total (sex),Total (age),3.6
        2011,Proportion of population living below the national poverty line,Total (sex),Total (age),3.9
        2012,Proportion of population living below the national poverty line,Total (sex),Total (age),4.2
        2013,Proportion of population living below the national poverty line,Total (sex),Total (age),4.2
        2014,Proportion of population living below the national poverty line,Total (sex),Total (age),4.0
        2015,Proportion of population living below the national poverty line,Total (sex),Total (age),3.8
        2016,Proportion of population living below the national poverty line,Total (sex),Total (age),3.4
        2017,Proportion of population living below the national poverty line,Total (sex),Total (age),3.3
        2018,Proportion of population living below the national poverty line,Total (sex),Total (age),3.0
        2019,Proportion of population living below the national poverty line,Total (sex),Total (age),2.7
        2020,Proportion of population living below the national poverty line,Total (sex),Total (age),2.4
        2021,Proportion of population living below the national poverty line,Total (sex),Total (age),2.7
        2009,Proportion of population living below the national poverty line,Total (sex),00-17 years,3.7
        2010,Proportion of population living below the national poverty line,Total (sex),00-17 years,3.5
        2011,Proportion of population living below the national poverty line,Total (sex),00-17 years,3.7
        2012,Proportion of population living below the national poverty line,Total (sex),00-17 years,4.0
        2013,Proportion of population living below the national poverty line,Total (sex),00-17 years,3.8
        2014,Proportion of population living below the national poverty line,Total (sex),00-17 years,3.7
        2015,Proportion of population living below the national poverty line,Total (sex),00-17 years,3.6
        2016,Proportion of population living below the national poverty line,Total (sex),00-17 years,3.2
        2017,Proportion of population living below the national poverty line,Total (sex),00-17 years,3.1
        2018,Proportion of population living below the national poverty line,Total (sex),00-17 years,2.8
        2019,Proportion of population living below the national poverty line,Total (sex),00-17 years,2.4
        2020,Proportion of population living below the national poverty line,Total (sex),00-17 years,2.2
        2021,Proportion of population living below the national poverty line,Total (sex),00-17 years,2.6
        2009,Proportion of population living below the national poverty line,Total (sex),18-24 years,4.0
        2010,Proportion of population living below the national poverty line,Total (sex),18-24 years,3.8
        2011,Proportion of population living below the national poverty line,Total (sex),18-24 years,4.2
        2012,Proportion of population living below the national poverty line,Total (sex),18-24 years,4.3
        2013,Proportion of population living below the national poverty line,Total (sex),18-24 years,4.5
        2014,Proportion of population living below the national poverty line,Total (sex),18-24 years,4.3
        2015,Proportion of population living below the national poverty line,Total (sex),18-24 years,4.1
        2016,Proportion of population living below the national poverty line,Total (sex),18-24 years,3.6
        2017,Proportion of population living below the national poverty line,Total (sex),18-24 years,3.5
        2018,Proportion of population living below the national poverty line,Total (sex),18-24 years,3.2
        2019,Proportion of population living below the national poverty line,Total (sex),18-24 years,3.1
        2020,Proportion of population living below the national poverty line,Total (sex),18-24 years,2.7
        2021,Proportion of population living below the national poverty line,Total (sex),18-24 years,2.8
        2009,Proportion of population living below the national poverty line,Total (sex),25-54 years,4.7
        2010,Proportion of population living below the national poverty line,Total (sex),25-54 years,4.7
        2011,Proportion of population living below the national poverty line,Total (sex),25-54 years,5.2
        2012,Proportion of population living below the national poverty line,Total (sex),25-54 years,5.5
        2013,Proportion of population living below the national poverty line,Total (sex),25-54 years,5.8
        2014,Proportion of population living below the national poverty line,Total (sex),25-54 years,5.3
        2015,Proportion of population living below the national poverty line,Total (sex),25-54 years,5.0
        2016,Proportion of population living below the national poverty line,Total (sex),25-54 years,4.6
        2017,Proportion of population living below the national poverty line,Total (sex),25-54 years,4.2
        2018,Proportion of population living below the national poverty line,Total (sex),25-54 years,3.7
        2019,Proportion of population living below the national poverty line,Total (sex),25-54 years,3.6
        2020,Proportion of population living below the national poverty line,Total (sex),25-54 years,3.4
        2021,Proportion of population living below the national poverty line,Total (sex),25-54 years,3.5
        2009,Proportion of population living below the national poverty line,Total (sex),55-66 years,4.6
        2010,Proportion of population living below the national poverty line,Total (sex),55-66 years,4.4
        2011,Proportion of population living below the national poverty line,Total (sex),55-66 years,4.9
        2012,Proportion of population living below the national poverty line,Total (sex),55-66 years,5.6
        2013,Proportion of population living below the national poverty line,Total (sex),55-66 years,5.5
        2014,Proportion of population living below the national poverty line,Total (sex),55-66 years,5.0
        2015,Proportion of population living below the national poverty line,Total (sex),55-66 years,4.7
        2016,Proportion of population living below the national poverty line,Total (sex),55-66 years,4.6
        2017,Proportion of population living below the national poverty line,Total (sex),55-66 years,4.1
        2018,Proportion of population living below the national poverty line,Total (sex),55-66 years,3.8
        2019,Proportion of population living below the national poverty line,Total (sex),55-66 years,3.1
        2020,Proportion of population living below the national poverty line,Total (sex),55-66 years,3.1
        2021,Proportion of population living below the national poverty line,Total (sex),55-66 years,3.3
        2009,Proportion of population living below the national poverty line,Total (sex),67+ years,4.8
        2010,Proportion of population living below the national poverty line,Total (sex),67+ years,5.0
        2011,Proportion of population living below the national poverty line,Total (sex),67+ years,5.5
        2012,Proportion of population living below the national poverty line,Total (sex),67+ years,5.5
        2013,Proportion of population living below the national poverty line,Total (sex),67+ years,6.1
        2014,Proportion of population living below the national poverty line,Total (sex),67+ years,5.6
        2015,Proportion of population living below the national poverty line,Total (sex),67+ years,5.4
        2016,Proportion of population living below the national poverty line,Total (sex),67+ years,4.7
        2017,Proportion of population living below the national poverty line,Total (sex),67+ years,4.3
        2018,Proportion of population living below the national poverty line,Total (sex),67+ years,3.7
        2019,Proportion of population living below the national poverty line,Total (sex),67+ years,4.0
        2020,Proportion of population living below the national poverty line,Total (sex),67+ years,3.6
        2021,Proportion of population living below the national poverty line,Total (sex),67+ years,3.7
        2009,Proportion of population living below the national poverty line,Males,Total (age),4.7
        2010,Proportion of population living below the national poverty line,Males,Total (age),4.4
        2011,Proportion of population living below the national poverty line,Males,Total (age),5.5
        2012,Proportion of population living below the national poverty line,Males,Total (age),6.0
        2013,Proportion of population living below the national poverty line,Males,Total (age),5.6
        2014,Proportion of population living below the national poverty line,Males,Total (age),6.0
        2015,Proportion of population living below the national poverty line,Males,Total (age),5.5
        2016,Proportion of population living below the national poverty line,Males,Total (age),4.5
        2017,Proportion of population living below the national poverty line,Males,Total (age),3.7
        2018,Proportion of population living below the national poverty line,Males,Total (age),3.9
        2019,Proportion of population living below the national poverty line,Males,Total (age),3.4
        2020,Proportion of population living below the national poverty line,Males,Total (age),2.9
        2021,Proportion of population living below the national poverty line,Males,Total (age),3.5
        2009,Proportion of population living below the national poverty line,Males,00-17 years,3.3
        2010,Proportion of population living below the national poverty line,Males,00-17 years,3.1
        2011,Proportion of population living below the national poverty line,Males,00-17 years,3.8
        2012,Proportion of population living below the national poverty line,Males,00-17 years,4.4
        2013,Proportion of population living below the national poverty line,Males,00-17 years,4.1
        2014,Proportion of population living below the national poverty line,Males,00-17 years,4.7
        2015,Proportion of population living below the national poverty line,Males,00-17 years,4.6
        2016,Proportion of population living below the national poverty line,Males,00-17 years,3.2
        2017,Proportion of population living below the national poverty line,Males,00-17 years,2.4
        2018,Proportion of population living below the national poverty line,Males,00-17 years,2.7
        2019,Proportion of population living below the national poverty line,Males,00-17 years,2.6
        2020,Proportion of population living below the national poverty line,Males,00-17 years,1.9
        2021,Proportion of population living below the national poverty line,Males,00-17 years,2.7
        2009,Proportion of population living below the national poverty line,Males,18-24 years,6.4
        2010,Proportion of population living below the national poverty line,Males,18-24 years,5.9
        2011,Proportion of population living below the national poverty line,Males,18-24 years,7.5
        2012,Proportion of population living below the national poverty line,Males,18-24 years,8.0
        2013,Proportion of population living below the national poverty line,Males,18-24 years,7.6
        2014,Proportion of population living below the national poverty line,Males,18-24 years,7.4
        2015,Proportion of population living below the national poverty line,Males,18-24 years,6.7
        2016,Proportion of population living below the national poverty line,Males,18-24 years,6.0
        2017,Proportion of population living below the national poverty line,Males,18-24 years,5.1
        2018,Proportion of population living below the national poverty line,Males,18-24 years,5.4
        2019,Proportion of population living below the national poverty line,Males,18-24 years,4.4
        2020,Proportion of population living below the national poverty line,Males,18-24 years,4.1
        2021,Proportion of population living below the national poverty line,Males,18-24 years,4.4
        2009,Proportion of population living below the national poverty line,Males,25-54 years,3.4
        2010,Proportion of population living below the national poverty line,Males,25-54 years,3.3
        2011,Proportion of population living below the national poverty line,Males,25-54 years,3.6
        2012,Proportion of population living below the national poverty line,Males,25-54 years,3.7
        2013,Proportion of population living below the national poverty line,Males,25-54 years,3.8
        2014,Proportion of population living below the national poverty line,Males,25-54 years,3.6
        2015,Proportion of population living below the national poverty line,Males,25-54 years,3.6
        2016,Proportion of population living below the national poverty line,Males,25-54 years,3.2
        2017,Proportion of population living below the national poverty line,Males,25-54 years,3.1
        2018,Proportion of population living below the national poverty line,Males,25-54 years,2.9
        2019,Proportion of population living below the national poverty line,Males,25-54 years,2.7
        2020,Proportion of population living below the national poverty line,Males,25-54 years,2.3
        2021,Proportion of population living below the national poverty line,Males,25-54 years,2.8
        2009,Proportion of population living below the national poverty line,Males,55-66 years,3.3
        2010,Proportion of population living below the national poverty line,Males,55-66 years,3.2
        2011,Proportion of population living below the national poverty line,Males,55-66 years,3.4
        2012,Proportion of population living below the national poverty line,Males,55-66 years,3.5
        2013,Proportion of population living below the national poverty line,Males,55-66 years,3.3
        2014,Proportion of population living below the national poverty line,Males,55-66 years,3.1
        2015,Proportion of population living below the national poverty line,Males,55-66 years,3.2
        2016,Proportion of population living below the national poverty line,Males,55-66 years,2.9
        2017,Proportion of population living below the national poverty line,Males,55-66 years,2.9
        2018,Proportion of population living below the national poverty line,Males,55-66 years,2.7
        2019,Proportion of population living below the national poverty line,Males,55-66 years,2.3
        2020,Proportion of population living below the national poverty line,Males,55-66 years,2.0
        2021,Proportion of population living below the national poverty line,Males,55-66 years,2.7
        2009,Proportion of population living below the national poverty line,Males,67+ years,3.6
        2010,Proportion of population living below the national poverty line,Males,67+ years,3.4
        2011,Proportion of population living below the national poverty line,Males,67+ years,3.7
        2012,Proportion of population living below the national poverty line,Males,67+ years,4.0
        2013,Proportion of population living below the national poverty line,Males,67+ years,4.3
        2014,Proportion of population living below the national poverty line,Males,67+ years,4.1
        2015,Proportion of population living below the national poverty line,Males,67+ years,4.1
        2016,Proportion of population living below the national poverty line,Males,67+ years,3.6
        2017,Proportion of population living below the national poverty line,Males,67+ years,3.4
        2018,Proportion of population living below the national poverty line,Males,67+ years,3.1
        2019,Proportion of population living below the national poverty line,Males,67+ years,3.1
        2020,Proportion of population living below the national poverty line,Males,67+ years,2.7
        2021,Proportion of population living below the national poverty line,Males,67+ years,2.9
        2009,Proportion of population living below the national poverty line,Females,Total (age),3.8
        2010,Proportion of population living below the national poverty line,Females,Total (age),3.3
        2011,Proportion of population living below the national poverty line,Females,Total (age),3.2
        2012,Proportion of population living below the national poverty line,Females,Total (age),3.3
        2013,Proportion of population living below the national poverty line,Females,Total (age),3.2
        2014,Proportion of population living below the national poverty line,Females,Total (age),3.2
        2015,Proportion of population living below the national poverty line,Females,Total (age),3.0
        2016,Proportion of population living below the national poverty line,Females,Total (age),2.7
        2017,Proportion of population living below the national poverty line,Females,Total (age),2.6
        2018,Proportion of population living below the national poverty line,Females,Total (age),2.1
        2019,Proportion of population living below the national poverty line,Females,Total (age),2.1
        2020,Proportion of population living below the national poverty line,Females,Total (age),1.9
        2021,Proportion of population living below the national poverty line,Females,Total (age),2.1
        2009,Proportion of population living below the national poverty line,Females,00-17 years,4.3
        2010,Proportion of population living below the national poverty line,Females,00-17 years,3.8
        2011,Proportion of population living below the national poverty line,Females,00-17 years,3.6
        2012,Proportion of population living below the national poverty line,Females,00-17 years,3.8
        2013,Proportion of population living below the national poverty line,Females,00-17 years,3.6
        2014,Proportion of population living below the national poverty line,Females,00-17 years,3.7
        2015,Proportion of population living below the national poverty line,Females,00-17 years,3.6
        2016,Proportion of population living below the national poverty line,Females,00-17 years,3.1
        2017,Proportion of population living below the national poverty line,Females,00-17 years,3.0
        2018,Proportion of population living below the national poverty line,Females,00-17 years,2.4
        2019,Proportion of population living below the national poverty line,Females,00-17 years,2.4
        2020,Proportion of population living below the national poverty line,Females,00-17 years,2.1
        2021,Proportion of population living below the national poverty line,Females,00-17 years,2.4
        2009,Proportion of population living below the national poverty line,Females,18-24 years,3.2
        2010,Proportion of population living below the national poverty line,Females,18-24 years,2.7
        2011,Proportion of population living below the national poverty line,Females,18-24 years,2.7
        2012,Proportion of population living below the national poverty line,Females,18-24 years,2.8
        2013,Proportion of population living below the national poverty line,Females,18-24 years,2.8
        2014,Proportion of population living below the national poverty line,Females,18-24 years,2.8
        2015,Proportion of population living below the national poverty line,Females,18-24 years,2.3
        2016,Proportion of population living below the national poverty line,Females,18-24 years,2.3
        2017,Proportion of population living below the national poverty line,Females,18-24 years,2.3
        2018,Proportion of population living below the national poverty line,Females,18-24 years,1.9
        2019,Proportion of population living below the national poverty line,Females,18-24 years,1.8
        2020,Proportion of population living below the national poverty line,Females,18-24 years,1.7
        2021,Proportion of population living below the national poverty line,Females,18-24 years,1.7
        2009,Proportion of population living below the national poverty line,Females,25-54 years,2.5
        2010,Proportion of population living below the national poverty line,Females,25-54 years,2.2
        2011,Proportion of population living below the national poverty line,Females,25-54 years,2.1
        2012,Proportion of population living below the national poverty line,Females,25-54 years,2.4
        2013,Proportion of population living below the national poverty line,Females,25-54 years,2.1
        2014,Proportion of population living below the national poverty line,Females,25-54 years,2.3
        2015,Proportion of population living below the national poverty line,Females,25-54 years,2.1
        2016,Proportion of population living below the national poverty line,Females,25-54 years,1.8
        2017,Proportion of population living below the national poverty line,Females,25-54 years,2.5
        2018,Proportion of population living below the national poverty line,Females,25-54 years,2.4
        2019,Proportion of population living below the national poverty line,Females,25-54 years,1.6
        2020,Proportion of population living below the national poverty line,Females,25-54 years,1.4
        2021,Proportion of population living below the national poverty line,Females,25-54 years,1.1
        2009,Proportion of population living below the national poverty line,Females,55-66 years,2.7
        2010,Proportion of population living below the national poverty line,Females,55-66 years,2.3
        2011,Proportion of population living below the national poverty line,Females,55-66 years,2.0
        2012,Proportion of population living below the national poverty line,Females,55-66 years,2.6
        2013,Proportion of population living below the national poverty line,Females,55-66 years,2.0
        2014,Proportion of population living below the national poverty line,Females,55-66 years,2.2
        2015,Proportion of population living below the national poverty line,Females,55-66 years,2.2
        2016,Proportion of population living below the national poverty line,Females,55-66 years,1.9
        2017,Proportion of population living below the national poverty line,Females,55-66 years,2.2
        2018,Proportion of population living below the national poverty line,Females,55-66 years,2.1
        2019,Proportion of population living below the national poverty line,Females,55-66 years,1.4
        2020,Proportion of population living below the national poverty line,Females,55-66 years,1.2
        2021,Proportion of population living below the national poverty line,Females,55-66 years,1.0
        2009,Proportion of population living below the national poverty line,Females,67+ years,2.4
        2010,Proportion of population living below the national poverty line,Females,67+ years,2.1
        2011,Proportion of population living below the national poverty line,Females,67+ years,2.1
        2012,Proportion of population living below the national poverty line,Females,67+ years,2.2
        2013,Proportion of population living below the national poverty line,Females,67+ years,2.2
        2014,Proportion of population living below the national poverty line,Females,67+ years,2.3
        2015,Proportion of population living below the national poverty line,Females,67+ years,2.1
        2016,Proportion of population living below the national poverty line,Females,67+ years,1.8
        2017,Proportion of population living below the national poverty line,Females,67+ years,2.7
        2018,Proportion of population living below the national poverty line,Females,67+ years,2.7
        2019,Proportion of population living below the national poverty line,Females,67+ years,1.9
        2020,Proportion of population living below the national poverty line,Females,67+ years,1.6
        2021,Proportion of population living below the national poverty line,Females,67+ years,1.2
    """

    correct_data_faroese = """
        Year,Series,kyn,aldur,Value
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),3.8
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),3.6
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),3.9
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),4.2
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),4.2
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),4.0
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),3.8
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),3.4
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),3.3
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),3.0
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),2.7
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),2.4
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,Tils. (aldur),2.7
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,3.7
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,3.5
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,3.7
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,4.0
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,3.8
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,3.7
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,3.6
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,3.2
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,3.1
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,2.8
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,2.4
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,2.2
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,00-17 ár,2.6
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,4.0
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,3.8
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,4.2
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,4.3
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,4.5
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,4.3
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,4.1
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,3.6
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,3.5
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,3.2
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,3.1
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,2.7
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,18-24 ár,2.8
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,4.7
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,4.7
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,5.2
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,5.5
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,5.8
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,5.3
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,5.0
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,4.6
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,4.2
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,3.7
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,3.6
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,3.4
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,25-54 ár,3.5
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,4.6
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,4.4
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,4.9
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,5.6
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,5.5
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,5.0
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,4.7
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,4.6
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,4.1
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,3.8
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,3.1
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,3.1
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,55-66 ár,3.3
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,4.8
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,5.0
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,5.5
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,5.5
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,6.1
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,5.6
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,5.4
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,4.7
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,4.3
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,3.7
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,4.0
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,3.6
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Bæði kyn,67+ ár,3.7
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),4.7
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),4.4
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),5.5
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),6.0
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),5.6
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),6.0
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),5.5
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),4.5
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),3.7
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),3.9
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),3.4
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),2.9
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,Tils. (aldur),3.5
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,3.3
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,3.1
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,3.8
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,4.4
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,4.1
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,4.7
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,4.6
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,3.2
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,2.4
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,2.7
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,2.6
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,1.9
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,00-17 ár,2.7
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,6.4
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,5.9
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,7.5
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,8.0
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,7.6
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,7.4
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,6.7
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,6.0
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,5.1
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,5.4
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,4.4
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,4.1
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,18-24 ár,4.4
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,3.4
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,3.3
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,3.6
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,3.7
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,3.8
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,3.6
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,3.6
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,3.2
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,3.1
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,2.9
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,2.7
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,2.3
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,25-54 ár,2.8
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,3.3
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,3.2
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,3.4
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,3.5
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,3.3
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,3.1
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,3.2
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,2.9
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,2.9
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,2.7
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,2.3
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,2.0
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,55-66 ár,2.7
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,3.6
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,3.4
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,3.7
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,4.0
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,4.3
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,4.1
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,4.1
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,3.6
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,3.4
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,3.1
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,3.1
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,2.7
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Menn,67+ ár,2.9
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),3.8
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),3.3
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),3.2
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),3.3
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),3.2
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),3.2
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),3.0
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),2.7
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),2.6
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),2.1
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),2.1
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),1.9
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,Tils. (aldur),2.1
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,4.3
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,3.8
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,3.6
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,3.8
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,3.6
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,3.7
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,3.6
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,3.1
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,3.0
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,2.4
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,2.4
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,2.1
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,00-17 ár,2.4
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,3.2
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,2.7
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,2.7
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,2.8
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,2.8
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,2.8
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,2.3
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,2.3
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,2.3
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,1.9
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,1.8
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,1.7
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,18-24 ár,1.7
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,2.5
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,2.2
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,2.1
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,2.4
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,2.1
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,2.3
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,2.1
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,1.8
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,2.5
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,2.4
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,1.6
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,1.4
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,25-54 ár,1.1
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,2.7
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,2.3
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,2.0
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,2.6
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,2.0
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,2.2
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,2.2
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,1.9
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,2.2
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,2.1
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,1.4
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,1.2
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,55-66 ár,1.0
        2009,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,2.4
        2010,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,2.1
        2011,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,2.1
        2012,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,2.2
        2013,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,2.2
        2014,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,2.3
        2015,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,2.1
        2016,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,1.8
        2017,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,2.7
        2018,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,2.7
        2019,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,1.9
        2020,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,1.6
        2021,"Patur av fólkinum, ið livir av minni enn fátækamarkinum í landinum",Kvinnur,67+ ár,1.2
    """

    correct_meta_english = {
        'computation_units': 'Testing units',
        'data_footnote': 'Testing note',
        'page_content': 'Testing note',
        'graph_title': 'Testing info',
        'indicator_name': 'Testing info',
        'CONTACT': 'Testing contact',
        'META_LAST_UPDATE': '20230911 09:00',
        'DATA_SOURCE': 'Testing source',
    }
    correct_meta_faroese = {
        'computation_units': 'Testing units FO',
        'data_footnote': 'Testing note FO',
        'page_content': 'Testing note FO',
        'graph_title': 'Testing info FO',
        'indicator_name': 'Testing info FO',
        'CONTACT': 'Testing contact FO',
        'META_LAST_UPDATE': '20230911 09:00',
        'DATA_SOURCE': 'Testing source FO',
    }
    print(indicator.language('fo').meta)
    inputs_common.assert_input_has_correct_data(indicator.language('en').data, correct_data_english)
    inputs_common.assert_input_has_correct_data(indicator.language('fo').data, correct_data_faroese)
    inputs_common.assert_input_has_correct_meta(indicator.language('en').meta, correct_meta_english)
    inputs_common.assert_input_has_correct_meta(indicator.language('fo').meta, correct_meta_faroese)

