import unittest
from app import app
from . import helper
import json

class HttpTest(unittest.TestCase):
		def setUp(self):
				self.app = app.test_client()
				self.app.testing = True

		def test_hello_world(self):

			response = self.app.get("/")
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response.data.decode("utf-8"), 'Hello world')

		def test_analyze_videos(self):

			# retrieves test video urls
			test_videos: list[helper.VideoAnalysisTestObject] = helper.get_test_video_urls()
			urls = []
			for test_video in test_videos:
				urls.append(test_video.get_video_url())
			
			# setup test packet
			packet = {
				"num_frames_to_sample": 10,
				"urls": urls,
			}

			response = self.app.post(
				"/analyze_videos",
				data=json.dumps(packet),
				content_type='application/json'
			)
			self.assertEqual(response.status_code, 200)
			self.assertTrue(response.is_json())

			content = response.get_json()

			for test_video in test_videos:
				video_id = test_video.video_id
				self.assertIn(video_id, content)
				self.assertIsNotNone(content[video_id])

				analysis = content[video_id]

				# Test quality of analysis
				for should_contain in test_video.should_contain:
					self.assertIn(should_contain, analysis)

if __name__ == "__main__":
		unittest.main()
