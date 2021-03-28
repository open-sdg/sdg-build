from sdg.inputs import InputJsonStat


class InputPxWebApi(InputJsonStat):
    """Sources of SDG data that are in a PxWeb API."""

    def get_indicator_id_map(self):
        if self.indicator_id_map is not None:
            return self.indicator_id_map
        tables = self.get_all_tables_from_endpoint(self.endpoint)
        return tables

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
