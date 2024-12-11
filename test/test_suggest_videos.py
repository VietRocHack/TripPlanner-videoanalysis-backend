import unittest
from function import suggest_videos, utils

class SuggestVideosUnitTest(unittest.TestCase):

	@unittest.skip("Not needed for now")
	def test_get_tiktok_access_token(self):
		is_success, response = suggest_videos.get_tiktok_access_token()

		self.assertTrue(is_success)

		self.assertRegex(response["access_token"], r'^clt\..+$')

	def test_suggest_random_video_by_location(self):
		location = "St. Louis, MO, USA"
		num_videos = 5

		result, response = suggest_videos.suggest_by_location(location, num_videos)

		self.assertTrue(result)
		suggested_videos = response["result"]
		self.assertEqual(len(suggested_videos), num_videos)

		for video in suggested_videos:
			is_valid_url, msg, _ = utils.verify_tiktok_url(video)
			self.assertTrue(is_valid_url, msg)

	def test_detect_bad_location(self):
		# TODO: This is not finished. Better to check if the Discover page actually
		# loads than waiting it all out which is too long
		location = "Some random location I don't know"

		result, response = suggest_videos.suggest_by_location(location)

		self.assertFalse(result)
		self.assertIn("error", response)
		self.assertEqual(response["error"], "An error has happened")

	def test_hardcoded_links(self):
		# Check only for supported locations
		supported_locations = [
			"New York, NY, USA",
			"Paris, France",
			"London, England",
			"Los Angeles, CA, USA",
			"Rochester, NY, USA",
			"Ho Chi Minh, Ho Chi Minh City, Vietnam",
			"Hanoi, Vietnam"
		]
		num_videos = 5
		for location in supported_locations:
			result = suggest_videos.check_hardcoded(location)
			self.assertIsNotNone(result)

			result, response = suggest_videos.suggest_by_location(location)
			self.assertTrue(result)
			suggested_videos = response["result"]
			self.assertEqual(len(suggested_videos), num_videos)

		# Check for other non-supported ones
		other_locations = ["City, Country"]
		for location in other_locations:
			result = suggest_videos.check_hardcoded(location)
			self.assertIsNone(result)

if __name__ == '__main__':
	unittest.main()
