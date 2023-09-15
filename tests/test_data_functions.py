import unittest

from controllers.data_controller import add_data_to, edit_data_for

# Mock data for testing
mock_data = {
    "data": {
        "ingredients": [
            {"id": 1, "name": "Salt", "location_id": 1},
            {"id": 2, "name": "Pepper", "location_id": 2}
        ],
        "locations": [
            {"id": 1, "name": "Pantry"},
            {"id": 2, "name": "Refrigerator"}
        ]
    }
}

class TestDataFunctions(unittest.TestCase):

    def test_add_data_to(self):
        """Test adding new data."""
        new_ingredient = {"name": "Sugar", "location_id": "1"}
        result = add_data_to(mock_data, new_ingredient, "ingredients")
        data = result["data"]["ingredients"]
        # Check if the new ingredient is added and has the correct ID
        self.assertEqual(data[-1]["name"], "Sugar")
        self.assertEqual(data[-1]["location_id"], 1)

    def test_edit_data_for(self):
        """Test editing existing data."""
        edited_ingredient = {"id": 1, "name": "Sea Salt", "location_id": 1}
        result = edit_data_for(mock_data, edited_ingredient, "ingredients")
        data = result["data"]["ingredients"]
        # Check if the ingredient has been edited correctly
        self.assertEqual(data[0]["name"], "Sea Salt")

# Running the tests
unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestDataFunctions))
