import unittest
from function import analyze_videos

class AnalyzeVideoUnitTest(unittest.TestCase):
	def test_analyze_video(self):
		video = "test/data/test_video.mp4"
		result, error_msg = analyze_videos.analyze(video)

		assert result == True
		assert error_msg == ""

	def test_analyze_video_dne(self):
		video = "test/data/dne.mp4"
		result, error_msg = analyze_videos.analyze(video)

		assert result == False
		assert error_msg == "Failed to load video"

	def test_sample_images(self):
		video = "test/data/test_video.mp4"
		num_frames_to_sample = 10
		result = analyze_videos.sample_images(video, num_frames_to_sample)

		assert len(result) == num_frames_to_sample

if __name__ == '__main__':
	unittest.main()
