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
			request = {
				"num_frames_to_sample": 5,
				"video_urls": urls,
			}

			response = self.app.post(
				"/analyze_videos",
				data=json.dumps(request),
				content_type='application/json'
			)
			self.assertEqual(response.status_code, 200)
			self.assertTrue(response.is_json)

			# check for all fields
			response_data = response.get_json()
			self.assertIn("video_analysis", response_data)
			self.assertIn("metadata", response_data)

			# checking for analysis
			content = response_data["video_analysis"]
			for test_video in test_videos:
				video_id = test_video.id
				self.assertIn(video_id, content)
				self.assertIsNotNone(content[video_id])

				analysis = content[video_id]

				# Test quality of analysis
				for should_contain in test_video.should_contain:
					self.assertIn(should_contain, analysis)

			# checking for metadata
			metadata = response_data["metadata"]
			self.assertIn("request", metadata)
			self.assertIn("timestamp", metadata)

			metadata_request = metadata["request"]
			self.assertEqual(metadata_request, request)

if __name__ == "__main__":
		unittest.main()
