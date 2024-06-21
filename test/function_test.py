import unittest
from function import analyze_videos

class AnalyzeVideoUnitTest(unittest.TestCase):
	def test_analyze_video(self):
		video = "test/data/test_video.mp4"
		result = analyze_videos.analyze(video)

		assert(result, True)

if __name__ == '__main__':
	unittest.main()
