import unittest
from function import openai_request
import cv2

class OpenAIRequestUnitTest(unittest.TestCase):
	def test_send_request_image(self):
		image = cv2.imread("test/data/test_image.png")
		result = openai_request.analyze_image(image)

		self.assertIsNotNone(result)
		self.assertTrue("@jacksdiningroom" in result)
		self.assertTrue("Trying Viral NYC Sandwich" in result)


if __name__ == '__main__':
	unittest.main()
