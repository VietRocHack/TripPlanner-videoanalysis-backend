import re
import traceback
import cv2
from function import openai_request 
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
from dataclasses import dataclass
from aiohttp import ClientSession
import asyncio
from function import utils
import time

logger = utils.setup_logger(__name__, f"../logs/analyze_videos_logger_{int(time.time())}.log")

# YoutubeDL options to set output filename to vid-{id} and put it in dl folder
ydl_opts = {
	'outtmpl': './dl/vid-%(id)s.%(ext)s',
	'quiet': True,
}

ydl_transcript_opts = {
	'outtmpl': './dl/vid-%(id)s.%(ext)s',
	'skip_download': True,
	'writesubtitles': True,
	'quiet': True,
}

@dataclass
class _TikTokVideoObject:
	id: str
	user: str
	path: str
	metadata: dict[str, str]
	transcript_path: str

	def get_clean_url(self) -> str:
		return f"https://www.tiktok.com/{ self.user }/video/{ self.id }"

async def analyze_from_urls(
		video_urls: list[str],
		num_frames_to_sample: int = 5,
		metadata_fields: list[str] = [] # supports "title", [more to be added]
	) -> tuple[bool, dict[str, str]]:
	"""
		Helper functions for analyze_from_url. Returns True if every video is
		finished analyzing successfully, returns False if one or more video has
		problem analyzing
	"""
	# mapping: {video_id: analysis}
	logger.info(f"Analyzing with { num_frames_to_sample } frames with metatdata { metadata_fields }: { video_urls }")

	# Returns a list of dictionary that contains the analysis of each video
	# in the given video_urls
	video_analysis: list[dict] = []

	# Use async to speed up requests from open_ai
	async with ClientSession() as session:
		# TODO: there's probably better way to manage this but idfk
		tasks = []
		for video_url in video_urls:
			logger.info(f"Analyzing: { video_url }")
			tasks.append(
				analyze_from_url(
					session=session,
					video_url=video_url,
					num_frames_to_sample=num_frames_to_sample,
					metadata_fields=metadata_fields
				)
			)
		results = await asyncio.gather(*tasks)

		# verify overall results and return whatever we can even if things fail
		overall_result = True
		for result, analysis in results:
			overall_result &= result
			video_analysis.append(analysis)
		return overall_result, video_analysis

async def analyze_from_url(
		session: ClientSession,
		video_url: str,
		num_frames_to_sample: int = 5,
		metadata_fields: list[str] = []
) -> tuple[bool, dict]:
	"""
		Takes in an url of a video, a positive integer of frames to sample and
		metadata fields and process them to get video analysis for each of the
		videos.
	"""
	# Checking for validity of url
	parsed_url = urlparse(video_url)
	if "tiktok.com" not in parsed_url.hostname:
		logger.info(f"Invalid TikTok URL - bad hostname: { video_url }")
		return False, {"error": "One or more video URLs are not from TikTok."}
	paths = parsed_url.path.split("/")
	if len(paths) < 4:
		logger.info(f"Invalid TikTok URL - bad format: { video_url }")
		return False, {"error": "Invalid TikTok video URL."}

	# Download video from url
	try:
		transcript_path, metadata = download_single_transcript(video_url, metadata_fields)
	except Exception as e:
		logger.info(f"Unable to download with { video_url } with exception { traceback.format_exc() }")
		return False, {"error": "Something happens during downloading video."}

	# If successfully downloaded, then keep data organized in one dataclass obj
	video_id = paths[3]
	vid_obj = _TikTokVideoObject(
		id=video_id,
		user=paths[1],
		path=f'dl/vid-{video_id}.mp4',
		metadata=metadata,
		transcript_path=transcript_path
	)

	# Start analyzing process 
	# result, data = await analyze_from_path(
	# 	session,
	# 	vid_obj.path,
	# 	num_frames_to_sample,
	# 	vid_obj.metadata
	# )

	result, data = await analyze_from_transcript(
		session,
		transcript_path,
		vid_obj.metadata
	)

	# Post-process result
	if result == True:
		logger.info(f"Finished analyzing { video_id }, result: { data }")
		# True if result succeeds
		data["video_url"] = vid_obj.get_clean_url()
		return True, data
	else:
		logger.error(f"Error when analyzing: { video_id }")
		return False, {"error": "Error when analyzing"}

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

async def analyze_from_transcript(
		session: ClientSession,
		transcript_path: str,
		metadata: dict[str, str] = {}
	) -> tuple[bool, dict]:
	"""
		Analyze a video from its video path and metadata (optional)
	"""
	transcript = _trim_transcript_vtt(transcript_path)

	analysis = await openai_request.analyze_transcript(
			session=session,
			transcript=transcript,
			metadata=metadata
		)

	return (True, analysis)

def _trim_transcript_vtt(transcript_path: str) -> str:
	with open(transcript_path) as f:
		transcript_lines = f.readlines()
	transcript = ""
	for line in transcript_lines:
			# Check if the line is a timestamp line
		if not re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}$', line) and line.strip() != '':
			transcript += line

	return transcript

def download_single_transcript(
		video_url: str,
		metadata_fields: dict[str, str] = []
	) -> tuple[str, str]:
	"""
		Helper function to download single video using #download_videos()
	"""
	subtitle_list, metadata_list = download_transcripts([video_url], metadata_fields)
	subtitle_path, metadata = subtitle_list[0], metadata_list[0]
	return subtitle_path, metadata

def download_transcripts(
		video_urls: list[str],
		metadata_fields: dict[str, str] = []
	) -> tuple[list[str], list[str]]:
	metadata_list = []
	subtitle_list = []
	with YoutubeDL(ydl_transcript_opts) as ydl:
		for video_url in video_urls:
			# download transcript
			info = ydl.extract_info(video_url)

			metadata = {}

			# extract metadata by requested metadata fields
			for field in metadata_fields:
				metadata[field] = info.get(field, None)

			metadata_list.append(metadata)

			# extract downloaded subtitles, if any
			requested_subtitles: dict = info.get("requested_subtitles", None)
			if requested_subtitles is None:
				subtitle_list.append("")
			subtitle_lang = list(requested_subtitles.keys())[0]
			subtitle_list.append(requested_subtitles[subtitle_lang]["filepath"])
		
	return subtitle_list, metadata_list

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
		Downloads the video in the given list of urls in video_urls.
		Also returns a list of metadata object that is filtered by the given
		metadata_fields
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
	"""
		Samples the number of images from the video in the given video_path
	"""
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
