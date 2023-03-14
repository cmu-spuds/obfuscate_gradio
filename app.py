import cv2
import gradio as gr
import numpy as np
from mtcnn_cv2 import MTCNN

detector = MTCNN()

def predict(img, selection):
  faces = detector.detect_faces(img)

  privacy_fn = None
  if(selection == "Low"):
    opts = (anonymize_face_pixelate, 20)
  elif(selection == "Medium"):
    opts = (anonymize_face_pixelate, 10)
  elif(selection == "High"):
    opts = (anonymize_face_pixelate, 4)
  elif(selection == "Emoji"):
    opts = (anonymize_face_emoji, "smiley")
  else:
    raise Exception("I don't know how you did it but you chose something else.")

  if len(faces) > 0:
    for features in faces:
      img = opts[0](img, features, opts[1])
  else:
    raise Exception("No faces detected");
  return img

def anonymize_face_pixelate(image, features, blocks=10):
  bb = features['box']
  face_crop = image[bb[1]:bb[1]+bb[3], bb[0]:bb[0]+bb[2]]
  # Divide the input image into NxN blocks
  (h,w) = face_crop.shape[:2]
  xSteps = np.linspace(0, w, blocks + 1, dtype="int")
  ySteps = np.linspace(0, h, blocks + 1, dtype="int")

  # loop over the blocks in both x and y direction
  for i in range(1, len(ySteps)):
    for j in range(1, len(xSteps)):
      # compute starting and ending (x, y)-coordinates
      # for current block
      startX = xSteps[j - 1]
      startY = ySteps[i - 1]
      endX = xSteps[j]
      endY = ySteps[i]

      # Extract the ROI using NumPy array slicing, compute the
      # mean of the ROI, and then draw a rectangle with the
      # mean RGB values over the ROI in teh original image
      roi = face_crop[startY:endY, startX:endX]
      (B, G, R) = [int(x) for x in cv2.mean(roi)[:3]]
      cv2.rectangle(face_crop, (startX, startY), (endX, endY),
                    (B,G,R), -1)

  image[bb[1]:bb[1]+bb[3], bb[0]:bb[0]+bb[2]] = face_crop
  return image

def anonymize_face_emoji(img, features, name="smiley"):
  bb = features['box']
  (y, x) = (bb[1] + int(bb[3]/2), bb[0] + int(bb[2]/2))
  (h,w) = (bb[3], bb[2])
  # Get emoji with transparency
  mask = cv2.imread('raccoon_emoji.png', -1)

  mshape = max(h,w)
  offset = int(mshape/2)

  return overlay_transparent(img, mask, 
                            x - offset,
                            y - offset, 
                            (mshape, mshape))

def overlay_transparent(background_img, img_to_overlay_t, x, y, overlay_size=None):
	"""
	@brief      Overlays a transparant PNG onto another image using CV2
	
	@param      background_img    The background image
	@param      img_to_overlay_t  The transparent image to overlay (has alpha channel)
	@param      x                 x location to place the top-left corner of our overlay
	@param      y                 y location to place the top-left corner of our overlay
	@param      overlay_size      The size to scale our overlay to (tuple), no scaling if None
	
	@return     Background image with overlay on top
	"""
	
	bg_img = background_img.copy()
	
	if overlay_size is not None:
		img_to_overlay_t = cv2.resize(img_to_overlay_t.copy(), overlay_size)

	# Extract the alpha mask of the RGBA image, convert to RGB 
	b,g,r,a = cv2.split(img_to_overlay_t)
	overlay_color = cv2.merge((b,g,r))
	
	# Apply some simple filtering to remove edge noise
	mask = cv2.medianBlur(a,5)

	h, w, _ = overlay_color.shape
	roi = bg_img[y:y+h, x:x+w]

	# Black-out the area behind the logo in our original ROI
	img1_bg = cv2.bitwise_and(roi.copy(),roi.copy(),mask = cv2.bitwise_not(mask))
	
	# Mask out the logo from the logo image.
	img2_fg = cv2.bitwise_and(overlay_color,overlay_color,mask = mask)

	# Update the original image with our new ROI
	bg_img[y:y+h, x:x+w] = cv2.add(img1_bg, img2_fg)

	return bg_img

gr.Interface(fn=predict,
             inputs=[gr.components.Image(type='numpy'), gr.components.Radio(["Low", "Medium", "High", "Emoji"], value="Medium")],
             outputs=gr.components.Image(type="pil"), allow_flagging="never").launch(show_error=True, quiet=False)
