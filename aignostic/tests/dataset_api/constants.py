from folktables import ACSDataSource, ACSEmployment
data_source = ACSDataSource(survey_year="2018", horizon="1-Year", survey="person")
acs_data = data_source.get_data(states=["AL"], download=True)
features, label, _ = ACSEmployment.df_to_pandas(acs_data)

expected_ACS_column_names = features.columns.tolist() + label.columns.tolist()
