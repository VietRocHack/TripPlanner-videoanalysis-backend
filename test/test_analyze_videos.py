import unittest
from function import analyze_videos
import json

class VideoAnalysisTestObject():
	def __init__(self, user: str, video_id: str, should_contain: list[str]):
		self.user = user
		self.video_id = video_id
		# should_contains describes what the resulting analysis should have once done
		self.should_contain = should_contain

	def get_video_url(self):
		return f"https://www.tiktok.com/{self.user}/video/{self.video_id}"

class AnalyzeVideoUnitTest(unittest.TestCase):
	def test_analyze_video(self):
		video = "test/data/test_video.mp4"
		result, content = analyze_videos.analyze_from_path(video)

		self.assertEqual(result, True)
		self.assertTrue("video" in content)
		self.assertTrue("sandwich" in content)

	def test_analyze_video_dne(self):
		video = "test/data/dne.mp4"
		result, content = analyze_videos.analyze_from_path(video)

		self.assertEqual(result, False)
		self.assertEqual(content, "Failed to load video")

	def test_sample_images(self):
		video = "test/data/test_video.mp4"
		num_frames_to_sample = 10
		result = analyze_videos.sample_images(video, num_frames_to_sample)

		self.assertEqual(len(result), num_frames_to_sample)

	def test_analyze_video_from_url(self):
		video_id = "7273630854000364846"
		url = f"https://www.tiktok.com/@jacksdiningroom/video/{video_id}?lang=en"
		result, content = analyze_videos.analyze_from_urls([url])

		self.assertTrue(result)
		self.assertIn(video_id, content)
		self.assertIsNotNone(content[video_id])

		analysis = content[video_id]

		self.assertTrue("video" in analysis)
		self.assertTrue("sandwich" in analysis)

	def test_invalid_url_not_from_tiktok(self):
		url = "https://www.youtube.com"
		result, content = analyze_videos.analyze_from_urls([url])

		self.assertFalse(result)
		self.assertEqual(content, "One or more video URLs are not from TikTok.")

	def test_invalid_url_invalid_download_link(self):
		url = "https://www.tiktok.com/@jacksdiningroom/video"
		result, content = analyze_videos.analyze_from_urls([url])

		self.assertFalse(result)
		self.assertEqual(content, "Invalid TikTok video URL.")

	def test_invalid_url_bad_download_link(self):
		url = "https://www.tiktok.com/@jacksdiningroom/video/gibberish"
		result, content = analyze_videos.analyze_from_urls([url])

		self.assertFalse(result)
		self.assertEqual(content, "Something happens during downloading video.")

	def test_analyze_video_from_multiple_urls(self):
		# Load videos for testing
		test_videos: list[VideoAnalysisTestObject] = []
		f = open('test/data/test_video_urls.json')
		data = json.load(f)
		for test_video in data:
			test_videos.append(
				VideoAnalysisTestObject(
					user=test_video["user"],
					video_id=test_video["video_id"],
					should_contain=test_video["should_contain"]
				)
			)
		f.close()

		urls = []
		for test_video in test_videos:
			urls.append(test_video.get_video_url())

		result, content = analyze_videos.analyze_from_urls(urls)

		self.assertTrue(result)

		for test_video in test_videos:
			video_id = test_video.video_id
			self.assertIn(video_id, content)
			self.assertIsNotNone(content[video_id])

			analysis = content[video_id]

			# Test quality of analysis
			for should_contain in test_video.should_contain:
				self.assertIn(should_contain, analysis)


if __name__ == '__main__':
	unittest.main()
