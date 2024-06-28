import unittest
from function import analyze_videos
import json
from . import helper

TEST_VIDEOS: list[helper.VideoAnalysisTestObject] = helper.get_test_video_urls()

class AnalyzeVideoUnitTest(unittest.TestCase):
	
	def test_analyze_video(self):
		# This is the downloaded video of the first video in the test_videos
		video = "test/data/test_video.mp4"
		f = open('test/data/test_video_metadata.json')
		metadata = json.load(f)
		f.close()
		result, analysis = analyze_videos.analyze_from_path(
			video_path=video,
			metadata=metadata
		)

		self.assertEqual(result, True)
		self._verify_contain(analysis["content"], ["sandwich", "chicken"])

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

	def _verify_video_analysis(
			self,
			test_vid: helper.VideoAnalysisTestObject,
			analysis: dict
		):
		video_user = test_vid.user
		video_id = test_vid.id

		self.assertIn("content", analysis)
		self.assertIn("location", analysis)
		self.assertIn("video_url", analysis)

		# verify content
		self._verify_contain(analysis["content"], test_vid.should_contain["content"])

		# verify location
		self._verify_contain(analysis["location"], test_vid.should_contain["location"])

		# verify url
		self.assertEqual(
			analysis["video_url"],
			f"https://www.tiktok.com/{ video_user }/video/{ video_id }"
		)

	def _verify_contain(self, content: str, should_contains: list[list[str]]):
		"""
			Private function to verify that the given content contain things that
			are in the list of should_contains.
			should_contains is formatted as a list of should_contain_list,
			where each should_contain_list has a number of words. The word ideally
			should be in the same category. 
			
			The satisfaction criteria is:
			- content must have at least one of the word in the should_contain_list.
			- content must satisfy all the should_contain_list in the should_contains.
			
			Example:
			should_contains = [["New York", "NY"], ["US", "United States"]]

			content #1: New York, US => accepted
			content #2: NY, US => accepted
			content #3: New Jersey, US => not accepted
			content #4: United States => not accepted
		"""

		for should_contain_list in should_contains:
			is_good = False
			# content must satisfy all the should_contain_list in the should_contains.
			for should_contain in should_contain_list:
				# content must have at least one of the word in the should_contain_list
				if should_contain in content:
					is_good = True
					break
			if not is_good:
				self.fail(f"\"{ content }\" does not have one of the required { should_contain_list }")

	def test_analyze_video_from_url(self):
		test_vid = TEST_VIDEOS[0]
		video_user = test_vid.user
		video_id = test_vid.id
		url = f"https://www.tiktok.com/{ video_user }/video/{ video_id }?lang=en"
		result, data = analyze_videos.analyze_from_urls([url], metadata_fields=["title"])

		self.assertTrue(result)
		self.assertIn(video_id, data)
		self.assertIsNotNone(data[video_id])

		# verify analysis of video
		self._verify_video_analysis(test_vid, data[video_id])

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
		self._send_test_request_with_multiple_urls(use_parallel=False, metadata_fields=["title"])

	def test_analyze_video_from_multiple_urls_speedup(self):
		self._send_test_request_with_multiple_urls(use_parallel=True, metadata_fields=["title"])

	def _send_test_request_with_multiple_urls(self, use_parallel: bool, metadata_fields: list[str]):
		test_videos: list[helper.VideoAnalysisTestObject] = helper.get_test_video_urls()

		urls = []
		for test_video in test_videos:
			urls.append(test_video.get_video_url())
		
		result, content = analyze_videos.analyze_from_urls(
			urls,
			metadata_fields=metadata_fields,
			use_parallel=use_parallel
		)

		self.assertTrue(result)

		for test_video in test_videos:
			video_id = test_video.id
			self.assertIn(video_id, content)
			self.assertIsNotNone(content[video_id])
			
			self._verify_video_analysis(test_video, content[video_id])

if __name__ == '__main__':
	unittest.main()
