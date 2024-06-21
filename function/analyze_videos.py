import cv2

def analyze(video_url):
	frames = []
	try:
		frames = sample_images(video_url)
	except Exception as e:
		return (False, str(e))

	return (True, "")

def sample_images(video_url: str, num_frames_to_sample: int = 5) -> list:
	# Load the video
	cap = cv2.VideoCapture(video_url)

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
