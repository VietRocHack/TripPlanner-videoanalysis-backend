import unittest
from function import openai_request
import cv2
from aiohttp import ClientSession

class OpenAIRequestUnitTest(unittest.IsolatedAsyncioTestCase):
	async def _analyze_images(self, images: list):
		async with ClientSession() as session:
			return await openai_request.analyze_images(session, images)

	async def _analyze_transcript(self, transcript: str):
		async with ClientSession() as session:
			return await openai_request.analyze_transcript(session, transcript)

	async def test_send_request_image(self):
		# Read the image using OpenCV
		image = cv2.imread("test/data/test_images/frame_0.jpg")
		# Put image in list because this function takes in a list of images
		analysis = await self._analyze_images([image])


		self.assertIsNotNone(analysis)
		self.assertIn("content", analysis)
		content = analysis["content"]
		self.assertIn("sandwich", content)
		self.assertIn("video", content)

	async def test_send_request_multiple_images(self):
		image_list = []
		for i in range(10):
			image_path = f"test/data/test_images/frame_{i}.jpg"
			image = cv2.imread(image_path)
			image_list.append(image)
		analysis = await self._analyze_images(image_list)

		self.assertIsNotNone(analysis)
		self.assertIn("content", analysis)

		content = analysis["content"]
		self.assertIn("sandwich", content)
		self.assertIn("video", content)

	async def test_send_request_transcript(self):
		
		with open("test/data/test_video_transcript.txt") as f:
			transcript = f.read()

		analysis = await self._analyze_transcript(transcript)

		self.assertIsNotNone(analysis)
		self.assertIn("content", analysis)

		content = analysis["content"]
		self.assertIn("sandwich", content)
		self.assertIn("Mama", content)

if __name__ == '__main__':
	unittest.main()
