import cv2
from function import openai_request 
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
import threading

# YoutubeDL options to set output filename to vid-{id} and put it in dl folder
ydl_opts = {
	'outtmpl': './dl/vid-%(id)s.%(ext)s'
}


def analyze_from_urls(
		video_urls: list[str],
		num_frames_to_sample: int = 5,
		use_parallel: bool = False
	) -> dict[str: str | None] | str:
	# mapping: {video_id: analysis}
	video_analysis = {}

	for url in video_urls:
		parsed_url = urlparse(url)
		if "tiktok.com" not in parsed_url.hostname:
			return False, "One or more video URLs are not from TikTok."
		paths = parsed_url.path.split("/")
		if len(paths) < 4:
			return False, "Invalid TikTok video URL."
		video_analysis[paths[3]] = None

	try:
		download_videos(video_urls)
	except Exception as e:
		return False, "Something happens during downloading video."

	video_ids = video_analysis.keys()

	# Use async to speed up requests from open_ai
	if use_parallel:
		threads = []
		results = {}
		for video_id in video_ids:
			print(f"Analyzing {video_id}")
			thread = threading.Thread(
				target=lambda id_: results.update(
					{id_: analyze_from_path(
						f'dl/vid-{id_}.mp4',
						num_frames_to_sample
					)}
				),
				args=(video_id,)
			)
			threads.append(thread)
			thread.start()

		for thread in threads:
			thread.join()

		for video_id, (result, content) in results.items():
			if result == True:
				video_analysis[video_id] = content
			else:
				return False, f"Error happens during analyzing video id {video_id}: {content}"
			
	else:
		# sequential calls to open_ai, mostly here for testing purposes
		for video_id in video_ids:
			print(f"Analyzing {video_id}")
			result, content = analyze_from_path(f'dl/vid-{video_id}.mp4', num_frames_to_sample)
			if result == True:
				video_analysis[video_id] = content
			else:
				return False, f"Error happens during analyzing video id {video_id}: {content}"

	return True, video_analysis

def analyze_from_path(
		video_path: str,
		num_frames_to_sample: int = 5,
		metadata: dict[str: str] = {}
	):
	frames = []
	try:
		frames = sample_images(video_path, num_frames_to_sample)
	except Exception as e:
		return (False, str(e))

	return (True, openai_request.analyze_images(frames, metadata=metadata))

def download_videos(video_urls):
	with YoutubeDL(ydl_opts) as ydl:
		ydl.download(video_urls)

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
