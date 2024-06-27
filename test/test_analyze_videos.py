import unittest
from function import analyze_videos
import json
from . import helper

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
		result, data = analyze_videos.analyze_from_urls([url], metadata_fields=["title"])

		self.assertTrue(result)
		self.assertIn(video_id, data)
		self.assertIsNotNone(data[video_id])

		# verify fields in analysis
		analysis = data[video_id]
		self.assertIn("content", analysis)
		self.assertIn("location", analysis)

		# verify content
		content = analysis["content"]
		self.assertIn("sandwich", content)

		# verify location
		location = analysis["location"]
		self.assertTrue(
			"New York" in location
			or "NY" in location
		)
		self.assertTrue(
			"US" in location
			or "United States" in location
		)

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

	@unittest.skip("Sequential version, here for debugging purpose only")
	def test_analyze_video_from_multiple_urls_no_speedup(self):
		self._send_test_request_with_multiple_urls(use_parallel=False)

	def test_analyze_video_from_multiple_urls_speedup(self):
		self._send_test_request_with_multiple_urls(use_parallel=True)

	def _send_test_request_with_multiple_urls(self, use_parallel: bool):
		test_videos: list[helper.VideoAnalysisTestObject] = helper.get_test_video_urls()

		urls = []
		for test_video in test_videos:
			urls.append(test_video.get_video_url())
		
		result, content = analyze_videos.analyze_from_urls(urls, use_parallel=use_parallel)

		self.assertTrue(result)

		for test_video in test_videos:
			video_id = test_video.video_id
			self.assertIn(video_id, content)
			self.assertIsNotNone(content[video_id])

			analysis = content[video_id]

			# Test quality of analysis
			for should_contain in test_video.should_contain:
				self.assertIn(should_contain, analysis)

	def test_analyze_video_with_metadata(self):
		video = "test/data/test_video.mp4"
		f = open('test/data/test_video_metadata.json')
		metadata = json.load(f)
		f.close()
		result, content = analyze_videos.analyze_from_path(
			video_path=video,
			metadata=metadata
		)

		self.assertEqual(result, True)
		self.assertTrue("video" in content)
		self.assertTrue("sandwich" in content)
		self.assertTrue("Mama" in content)
		self.assertTrue("Too" in content)
		self.assertTrue(
			"New York" in content
			or "NYC" in content
		)

	def test_analyze_video_from_url_with_metadata(self):
		video_id = "7273630854000364846"
		url = f"https://www.tiktok.com/@jacksdiningroom/video/{video_id}?lang=en"
		result, content = analyze_videos.analyze_from_urls(
			[url],
			metadata_fields=["title"]
		)

		self.assertTrue(result)
		self.assertIn(video_id, content)
		self.assertIsNotNone(content[video_id])

		analysis = content[video_id]

		self.assertEqual(result, True)
		self.assertTrue("video" in analysis)
		self.assertTrue("sandwich" in analysis)
		self.assertTrue("Mama" in analysis)
		self.assertTrue("Too" in analysis)
		self.assertTrue(
			"New York" in analysis
			or "NY" in analysis
		)

	def test_analyze_video_from_url_with_metadata_no_speedup(self):
		video_id = "7273630854000364846"
		url = f"https://www.tiktok.com/@jacksdiningroom/video/{video_id}?lang=en"
		result, content = analyze_videos.analyze_from_urls(
			[url],
			metadata_fields=["title"],
			use_parallel=False
		)

		self.assertTrue(result)
		self.assertIn(video_id, content)
		self.assertIsNotNone(content[video_id])

		analysis = content[video_id]

		self.assertEqual(result, True)
		self.assertTrue("video" in analysis)
		self.assertTrue("sandwich" in analysis)
		self.assertTrue("Mama" in analysis)
		self.assertTrue("Too" in analysis)
		self.assertTrue(
			"New York" in analysis
			or "NY" in analysis
		)

if __name__ == '__main__':
	unittest.main()
