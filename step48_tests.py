"""Step 48: Test Framework"""
import unittest
from pathlib import Path
from core.validation import sanitize_filename, validate_choice

class TestValidation(unittest.TestCase):
    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename('Test Podcast!'), 'Test_Podcast')
        self.assertEqual(sanitize_filename('AI & ML'), 'AI__ML')
    
    def test_validate_choice(self):
        result = validate_choice('casual', {'casual', 'professional'}, 'tone')
        self.assertEqual(result, 'casual')

if __name__ == '__main__':
    print('Step 48: Running tests...')
    unittest.main(verbosity=2)
