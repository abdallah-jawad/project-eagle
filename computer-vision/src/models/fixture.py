class Fixture:
    def __init__(self, location_id: str, fixture_id: str, fixture_name: str, fixture_type: str, position: str, dimensions: str, planograms=None, cameras=None):
        self.location_id = location_id
        self.fixture_id = fixture_id
        self.fixture_name = fixture_name
        self.fixture_type = fixture_type
        self.position = position
        self.dimensions = dimensions
        self.planograms = planograms if planograms is not None else []
        self.cameras = cameras if cameras is not None else []

    def __repr__(self):
        return f"Fixture(location_id={self.location_id}, fixture_id={self.fixture_id}, fixture_name={self.fixture_name}, fixture_type={self.fixture_type}, position={self.position}, dimensions={self.dimensions})" 