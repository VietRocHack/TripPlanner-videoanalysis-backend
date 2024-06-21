import unittest
from function import openai_request
import cv2

class OpenAIRequestUnitTest(unittest.TestCase):
	def test_send_request_image(self):
		# Read the image using OpenCV
		image = cv2.imread("test/data/test_image.png")

		# Call the analyze_image function and store the result
		result = openai_request.analyze_image(image)

		# Assert that the result is not empty
		self.assertIsNotNone(result)

		# Assert that the result is a valid JSON
		self.assertIsInstance(result, dict)


if __name__ == '__main__':
	unittest.main()
