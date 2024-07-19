import unittest
from function import suggest_videos

class SuggestVideosUnitTest(unittest.TestCase):

	async def test_suggest_random_video_by_location(self):
		location = "New York, NY"
		num_videos = 5

		suggestions = suggest_videos.suggest(location, num_videos)

		self.assertEqual(len(suggestions), num_videos)

if __name__ == '__main__':
	unittest.main()
