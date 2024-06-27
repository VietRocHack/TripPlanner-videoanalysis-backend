import cv2
from function import openai_request 
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
import threading
from dataclasses import dataclass

# YoutubeDL options to set output filename to vid-{id} and put it in dl folder
ydl_opts = {
	'outtmpl': './dl/vid-%(id)s.%(ext)s'
}

@dataclass
class _TikTokVideoObject:
	id: str
	path: str
	metadata: dict[str, str]

def analyze_from_urls(
		video_urls: list[str],
		num_frames_to_sample: int = 5,
		use_parallel: bool = True, # use parallel running by default
		metadata_fields: list[str] = [] # supports "title", [more to be added]
	) -> dict[str, str | None] | str:
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
			path=f'dl/vid-{video_id}.mp4',
			metadata=metadata
		)


	video_ids = video_objects.keys()

	# Use async to speed up requests from open_ai
	if use_parallel:
		threads = []
		results = {}
		for video_id in video_ids:
			print(f"Analyzing {video_id}")
			thread = threading.Thread(
				target=lambda vid_obj: results.update(
					{vid_obj.id: analyze_from_path(
						vid_obj.path,
						num_frames_to_sample,
						vid_obj.metadata
					)}
				),
				args=(video_objects[video_id],)
			)
			threads.append(thread)
			thread.start()

		for thread in threads:
			thread.join()

		# Verify video analysis results is correct before returning
		for video_id, (result, content) in results.items():
			if result == True:
				video_analysis[video_id] = content
			else:
				return False, f"Error happens during analyzing video id {video_id}: {content}"
			
	else:
		# sequential calls to open_ai, mostly here for testing purposes
		for video_id in video_ids:
			print(f"Analyzing {video_id}")
			vid_obj = video_objects[video_id]
			result, content = analyze_from_path(vid_obj.path, num_frames_to_sample)
			if result == True:
				video_analysis[video_id] = content
			else:
				return False, f"Error happens during analyzing video id {video_id}: {content}"

	return True, video_analysis

def analyze_from_path(
		video_path: str,
		num_frames_to_sample: int = 5,
		metadata: dict[str, str] = {}
	) -> tuple[bool, str]:
	frames = []
	try:
		frames = sample_images(video_path, num_frames_to_sample)
	except Exception as e:
		return (False, str(e))

	return (True, openai_request.analyze_images(frames, metadata=metadata))

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

			print(metadata)
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
