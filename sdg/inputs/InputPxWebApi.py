from sdg.inputs import InputJsonStat


class InputPxWebApi(InputJsonStat):
    """Sources of SDG data that are in a PxWeb API."""

    def get_indicator_id_map(self):
        if self.indicator_id_map is not None:
            return self.indicator_id_map
        tables = self.get_all_tables_from_endpoint(self.endpoint)
        self.warn('The indicator_id_map parameter was not supplied, and there will likely be errors.')
        self.warn('To help you generate an indicator_id_map, here are the tables that were manually compiled:')
        self.warn(str(tables))
        return tables


    def get_post_data(self):
        return {"query": []} if self.post_data is None else self.post_data


    def get_all_tables_from_endpoint(self, endpoint):
        all_tables = []
        self.wait_for_next_request()
        print("About to fetch: " + endpoint)
        resources = self.fetch_json_response(endpoint)
        list_resources = self.get_list_resources(resources)
        for list_resource in list_resources:
            resource_endpoint = endpoint + "/" + list_resource["id"]
            all_tables += self.get_all_tables_from_endpoint(resource_endpoint)
        table_resources = self.get_table_resources(resources)
        for table_resource in table_resources:
            resource_endpoint = endpoint + "/" + table_resource["id"]
            all_tables.append(resource_endpoint)
        return all_tables

    def get_table_resources(self, resources):
        return [item for item in resources if item["type"] == "t"]

    def get_list_resources(self, resources):
        return [item for item in resources if item["type"] == "l"]
