import unittest
from function import analyze_videos
import json
from . import helper
from aiohttp import ClientSession

TEST_VIDEOS: list[helper.VideoAnalysisTestObject] = helper.get_test_video_urls()

class AnalyzeVideoUnitTest(unittest.IsolatedAsyncioTestCase):

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

	async def _send_test_request_with_multiple_urls(self, metadata_fields: list[str]):
		test_videos: list[helper.VideoAnalysisTestObject] = helper.get_test_video_urls()

		urls = []

		for test_video in test_videos:
			urls.append(test_video.get_video_url())
		
		result, analysis_list = await analyze_videos.analyze_from_urls(
			urls,
			metadata_fields=metadata_fields,
		)

		self.assertTrue(result)
		for i in range(len(test_videos)):
			test_video = test_videos[i]
			analysis = analysis_list[i]
			self._verify_video_analysis(test_video, analysis)

	async def _analyze_from_video_path(
			self,
			video_path: str,
			num_frames_to_sample: int = 5,
			metadata: dict[str, str] = {}
		):
		"""
			Helper function to run analyze_videos.analyze_from_path since it needs a
			ClientSession. TODO: there's probably better way to do this...
		"""
		async with ClientSession() as session:
			result, analysis = await analyze_videos.analyze_from_path(
				session,
				video_path,
				num_frames_to_sample,
				metadata
			)

			return result, analysis

	async def _analyze_from_transcript_path(
			self,
			transcript_path: str,
			metadata: dict[str, str] = {}
	):
		"""
			Helper function to run analyze_videos.analyze_from_path since it needs a
			ClientSession. TODO: there's probably better way to do this...
		"""
		async with ClientSession() as session:
			result, analysis = await analyze_videos.analyze_from_transcript(
				session,
				transcript_path,
				metadata
			)

			return result, analysis

	async def test_analyze_video_by_images(self):
		# This is the downloaded video of the first video in the test_videos
		video = "test/data/test_video.mp4"
		f = open('test/data/test_video_metadata.json')
		metadata = json.load(f)
		f.close()

		result, analysis = await self._analyze_from_video_path(
			video_path=video,
			metadata=metadata
		)

		self.assertEqual(result, True)
		self._verify_contain(analysis["content"], ["sandwich", "chicken"])

	async def test_analyze_video_dne(self):
		video = "test/data/dne.mp4"
		result, content = await self._analyze_from_video_path(video)

		self.assertEqual(result, False)
		self.assertEqual(content, "Failed to load video")

	def test_sample_images(self):
		video = "test/data/test_video.mp4"
		num_frames_to_sample = 10
		result = analyze_videos.sample_images(video, num_frames_to_sample)

		self.assertEqual(len(result), num_frames_to_sample)

	async def test_analyze_video_from_url(self):
		test_vid = TEST_VIDEOS[0]
		url = test_vid.get_video_url()
		result, data = await analyze_videos.analyze_from_urls([url], metadata_fields=["title"])

		# verify result
		self.assertTrue(result)
		self.assertGreater(len(data), 0)

		# verify analysis of video
		self._verify_video_analysis(test_vid, data[0])

	async def test_invalid_url_not_from_tiktok(self):
		url = "https://www.youtube.com"
		result, content = await analyze_videos.analyze_from_urls([url])

		self.assertFalse(result)
		self.assertEqual(content, [{"error": "Invalid TikTok URL - provided URL is not from TikTok"}])

	async def test_invalid_url_invalid_download_link(self):
		url = "https://www.tiktok.com/@jacksdiningroom/video"
		result, content = await analyze_videos.analyze_from_urls([url])

		self.assertFalse(result)
		self.assertEqual(content, [{"error": "Invalid TikTok URL - bad format"}])

	async def test_invalid_url_bad_download_link(self):
		url = "https://www.tiktok.com/@jacksdiningroom/video/gibberish"
		result, content = await analyze_videos.analyze_from_urls([url])

		self.assertFalse(result)
		self.assertEqual(content, [{"error": "Something happens during downloading video."}])

	async def test_analyze_video_from_multiple_urls(self):
		await self._send_test_request_with_multiple_urls(metadata_fields=["title"])

	async def test_analyze_video_using_transcript(self):
		# This is the downloaded video of the first video in the test_videos
		transcript = "test/data/test_video_transcript_raw.vtt"
		f = open('test/data/test_video_metadata.json')
		metadata = json.load(f)
		f.close()

		result, analysis = await self._analyze_from_transcript_path(
			transcript,
			metadata
		)

		self.assertEqual(result, True)
		self._verify_contain(analysis["content"], ["sandwich", "chicken"])

	async def test_trim_transcript_vtt(self):
		transcript = analyze_videos._trim_transcript_vtt("test/data/test_video_transcript_raw.vtt")
		
		with open("test/data/test_video_transcript.txt") as f:
			expected_transcript = f.read()

		self.assertEqual(transcript, expected_transcript)

	async def test_analyze_video_using_url_no_transcript(self):
		url = "https://www.tiktok.com/@asmrjade_yt/video/7369739907775941895"
		result, data = await analyze_videos.analyze_from_urls(
			[url],
			num_frames_to_sample=5,
			metadata_fields=["title"]
		)

		# verify result
		self.assertTrue(result)
		self.assertGreater(len(data), 0)
		analysis = data[0]

		self.assertIn("marshmallow", analysis["content"])

if __name__ == '__main__':
	unittest.main()
