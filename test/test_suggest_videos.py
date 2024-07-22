import unittest
from function import suggest_videos, utils

class SuggestVideosUnitTest(unittest.TestCase):

	@unittest.skip("Not needed for now")
	def test_get_tiktok_access_token(self):
		is_success, response = suggest_videos.get_tiktok_access_token()

		self.assertTrue(is_success)

		self.assertRegex(response["access_token"], r'^clt\..+$')

	def test_suggest_random_video_by_location(self):
		location = "New York, NY"
		num_videos = 5

		result, response = suggest_videos.suggest(location, num_videos)

		self.assertTrue(result)
		suggested_videos = response["result"]
		self.assertEqual(len(suggested_videos), num_videos)

		for video in suggested_videos:
			is_valid_url, msg, _ = utils.verify_tiktok_url(video)
			self.assertTrue(is_valid_url, msg)

if __name__ == '__main__':
	unittest.main()
