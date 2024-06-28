import cv2
from function import openai_request 
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
from dataclasses import dataclass
from aiohttp import ClientSession
import asyncio

# YoutubeDL options to set output filename to vid-{id} and put it in dl folder
ydl_opts = {
	'outtmpl': './dl/vid-%(id)s.%(ext)s',
	'quiet': True,
	'no_warnings': True,
}

@dataclass
class _TikTokVideoObject:
	id: str
	user: str
	path: str
	metadata: dict[str, str]

	def get_clean_url(self) -> str:
		return f"https://www.tiktok.com/{ self.user }/video/{ self.id }"

async def analyze_from_urls(
		video_urls: list[str],
		num_frames_to_sample: int = 5,
		metadata_fields: list[str] = [] # supports "title", [more to be added]
	) -> tuple[bool, dict[str, str]]:
	# mapping: {video_id: analysis}
	video_analysis: dict[str, dict[str: str]] = {}
	video_objects: dict[str, _TikTokVideoObject] = {}

	for url in video_urls:
		parsed_url = urlparse(url)
		if "tiktok.com" not in parsed_url.hostname:
			return False, "One or more video URLs are not from TikTok."
		paths = parsed_url.path.split("/")
		if len(paths) < 4:
			return False, "Invalid TikTok video URL."

		try:
			metadata = download_single_video(url, metadata_fields=metadata_fields)
		except Exception:
			return False, "Something happens during downloading video."

		# If successfully downloaded, then keep data organized in one dataclass obj
		video_id = paths[3]
		video_objects[video_id] = _TikTokVideoObject(
			id=video_id,
			user=paths[1],
			path=f'dl/vid-{video_id}.mp4',
			metadata=metadata
		)


	video_ids = video_objects.keys()

	# Use async to speed up requests from open_ai
	async with ClientSession() as session:
		# TODO: there's probably better way to manage this but idfk
		tasks = []
		task_ids = []
		for video_id in video_ids:
			print(f"Analyzing {video_id}")
			vid_obj = video_objects[video_id]
			task_ids.append(video_id)
			tasks.append(
				analyze_from_path(
					session=session,
					video_path=vid_obj.path,
					num_frames_to_sample=1,
					metadata=vid_obj.metadata
				)
			)
		results = await asyncio.gather(*tasks)

		# post-process results here
		for i in range(len(video_ids)):
			video_id = task_ids[i]
			result, data = results[i]
			if result == True:
				# True if result succeeds
				vid_obj = video_objects[video_id]
				data["video_url"] = vid_obj.get_clean_url()
				video_analysis[video_id] = data
			else:
				# False if some shit happens TODO: Log something here
				video_analysis[video_id] = {"error": "Error when analyzing"}

		return True, video_analysis

async def analyze_from_path(
		session: ClientSession,
		video_path: str,
		num_frames_to_sample: int = 5,
		metadata: dict[str, str] = {}
	) -> tuple[bool, dict]:
	"""
		Analyze a video from its video path and metadata (optional)
	"""
	frames = []
	try:
		frames = sample_images(video_path, num_frames_to_sample)
	except Exception as e:
		return (False, str(e))

	analysis = await openai_request.analyze_images(
			session=session,
			images=frames,
			metadata=metadata
		)

	return (True, analysis)

def download_single_video(video_url: str, metadata_fields: dict[str, str] = []):
	"""
		Helper function to download single video using #download_videos()
	"""
	metadata = download_videos([video_url], metadata_fields)[0]
	return metadata


def download_videos(
		video_urls: list[str], 
		metadata_fields: dict[str, str] = []
	) -> list[dict[str, str]]:
	"""
		Returns a list of metadata object that is filtered by the given metadata_fields
	"""
	metadata_list = []
	with YoutubeDL(ydl_opts) as ydl:
		for video_url in video_urls:
			# download video and also extracting info
			video = ydl.extract_info(video_url, download=True)

			metadata = {}

			for field in metadata_fields:
				metadata[field] = video.get(field, None)

			metadata_list.append(metadata)
		
	return metadata_list

def sample_images(video_path: str, num_frames_to_sample: int = 5) -> list:
	# Load the video
	cap = cv2.VideoCapture(video_path)

	# Check if video is successfully loaded
	if not cap.isOpened():
		raise Exception("Failed to load video")

	frames = []
	total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

	# Calculate the step size to sample frames equally
	step_size = total_frames // num_frames_to_sample

	# Sample frames from the video
	for i in range(num_frames_to_sample):
		# Set the frame position to the desired step
		cap.set(cv2.CAP_PROP_POS_FRAMES, i * step_size)
		ret, frame = cap.read()
		if not ret:
			break

		frames.append(frame)

	cap.release()

	return frames
