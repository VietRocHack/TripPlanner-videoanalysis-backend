import json

class VideoAnalysisTestObject():
	def __init__(self, user: str, video_id: str, should_contain: list[str]):
		self.user = user
		self.id = video_id
		# should_contains describes what the resulting analysis should have once done
		self.should_contain = should_contain

	def get_video_url(self):
		return f"https://www.tiktok.com/{self.user}/video/{self.id}"

def get_test_video_urls() -> list[VideoAnalysisTestObject]:
	"""
		Helper function to load the list of test video objects
	"""
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

	return test_videos
