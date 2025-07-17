class Planogram:
    def __init__(self, fixture_id: str, planogram_id: str, planogram_name: str, version: str, layout_data: str, products: str):
        self.fixture_id = fixture_id
        self.planogram_id = planogram_id
        self.planogram_name = planogram_name
        self.version = version
        self.layout_data = layout_data
        self.products = products

    def __repr__(self):
        return f"Planogram(fixture_id={self.fixture_id}, planogram_id={self.planogram_id}, planogram_name={self.planogram_name}, version={self.version}, layout_data={self.layout_data}, products={self.products})" 